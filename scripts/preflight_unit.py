#!/usr/bin/env python3
"""Pre-grade reachability preflight for one UHBS lab unit.

Answers exactly one question before any grading compute is spent:
*can Module A reach and elicit a response from the target service?*

It deliberately reuses the grader's own resolution path —
``uhbs_core.inventory.load_inventory`` + ``resolve_target`` + TPS
``apply_tps`` — and the same ``_port_open`` TCP check the RFC probes use,
so a green preflight is a faithful predictor of a gradeable Module A run.

Failure classes it distinguishes (the taxonomy from the results-5.0.1 wave):

* ``site_missing``      — inventory has no such site (wave bug: wrong --target)
* ``no_port_mapped``    — site/TPS carry no port for the protocol (Module A
                          would fall back to 2222 and fail; espot-class bug)
* ``dns_error``         — alias does not resolve on uhbs-lab (target not
                          started / wrong --network-alias)
* ``port_closed``       — alias resolves but nothing listens (service not
                          enabled / crashed / wrong port)
* ``timeout``           — connect or UDP reply never arrived
* ``udp_no_reply``      — datagram sent, no response (silent-drop service or
                          dead target; Module A would score 0 either way)

Exit codes: 0 = all protocols reachable, 1 = at least one unreachable,
2 = configuration error (bad inventory/site/TPS path).

Run it from inside the Docker network for alias resolution, e.g.:

    docker run --rm --network uhbs-lab -v "$PWD:/work" -w /work \
      --entrypoint python3 uhbs:5.0.1 \
      scripts/preflight_unit.py --inventory docs/conformance/labs/cowrie/inventory.yaml \
        --site cowrie-ssh --tps docs/conformance/labs/cowrie/low_interaction_ssh_full.yaml
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uhbs_core.inventory import load_inventory  # noqa: E402
from uhbs_core.rfc_probes.socket_util import _port_open  # noqa: E402
from uhbs_core.tps import apply_tps, load_tps, resolve_tps_path  # noqa: E402

# Protocols carried over UDP. Everything else is probed with a TCP connect.
UDP_PROTOCOLS = frozenset({"snmp", "dns", "ntp", "sip", "tftp", "dhcp", "bacnet"})

DEFAULT_TIMEOUT = 3.0


# --- minimal, valid wire PDUs (reachability only — not conformance) ----------


def _dns_probe(host: str) -> bytes:
    qname = b"".join(bytes([len(p)]) + p.encode() for p in ("example", "com")) + b"\x00"
    return b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" + qname + b"\x00\x01\x00\x01"


def _ntp_probe(host: str) -> bytes:
    return b"\x1b" + 47 * b"\x00"


def _tlv(tag: int, payload: bytes) -> bytes:
    assert len(payload) < 128  # noqa: S101 - every PDU below stays short-form
    return bytes([tag, len(payload)]) + payload


def _snmp_probe(host: str) -> bytes:
    oid = bytes([0x2B, 6, 1, 2, 1, 1, 1, 0])  # 1.3.6.1.2.1.1.1.0 (sysDescr.0)
    varbind = _tlv(0x30, _tlv(0x06, oid) + _tlv(0x05, b""))
    varbinds = _tlv(0x30, varbind)
    pdu = _tlv(0xA0, _tlv(0x02, b"\x01") + _tlv(0x02, b"\x00") + _tlv(0x02, b"\x00") + varbinds)
    return _tlv(0x30, _tlv(0x02, b"\x01") + _tlv(0x04, b"public") + pdu)


def _sip_probe(host: str) -> bytes:
    msg = (
        f"OPTIONS sip:preflight@{host} SIP/2.0\r\n"
        "Via: SIP/2.0/UDP 127.0.0.1:5060;branch=z9hG4bKpf\r\n"
        f"From: <sip:preflight@{host}>\r\n"
        f"To: <sip:preflight@{host}>\r\n"
        f"Call-ID: pf@{host}\r\n"
        "CSeq: 1 OPTIONS\r\n"
        "Max-Forwards: 1\r\n"
        "Content-Length: 0\r\n\r\n"
    )
    return msg.encode()


def _tftp_probe(host: str) -> bytes:
    return b"\x00\x01preflight\x00octet\x00"


def _dhcp_probe(host: str) -> bytes:
    mac = bytes.fromhex("0242ac11ffaa")  # container-ish locally-administered MAC
    head = bytearray(240)
    head[0] = 1  # BOOTREQUEST
    head[1] = 1  # ethernet
    head[2] = 6  # hlen
    head[4:8] = b"\x12\x34\x56\x78"  # xid
    head[28:34] = mac
    head[236:240] = b"\x63\x82\x53\x63"  # magic cookie
    options = bytes([53, 1, 1, 61]) + bytes([len(mac)]) + mac + bytes([255])
    return bytes(head) + options


def _bacnet_probe(host: str) -> bytes:
    # BVLC original-unicast-NPDU wrapping a Who-Is (unconfirmed service 0).
    return b"\x81\x0b\x00\x07\x01\x00\x10"


UDP_PROBES = {
    "dns": _dns_probe,
    "ntp": _ntp_probe,
    "snmp": _snmp_probe,
    "sip": _sip_probe,
    "tftp": _tftp_probe,
    "dhcp": _dhcp_probe,
    "bacnet": _bacnet_probe,
}


# --- probes ------------------------------------------------------------------


def probe_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    if _port_open(host, port, timeout=timeout):
        return True, "tcp connect ok"
    # _port_open swallows the OSError class; re-derive it for classification.
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "tcp connect ok"
    except socket.gaierror as exc:
        return False, f"dns_error ({exc})"
    except ConnectionRefusedError:
        return False, "connection refused"
    except TimeoutError:
        return False, "connect timed out"
    except OSError as exc:
        return False, str(exc)


def probe_udp(host: str, port: int, protocol: str, timeout: float) -> tuple[bool, str]:
    builder = UDP_PROBES.get(protocol)
    if builder is None:
        return False, f"no UDP probe implemented for {protocol}"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(builder(host), (host, port))
            t0 = time.perf_counter()
            while True:
                data, _addr = s.recvfrom(4096)
                if data:
                    return (
                        True,
                        f"udp reply {len(data)}B in {time.perf_counter() - t0:.2f}s",
                    )
    except socket.gaierror as exc:
        return False, f"dns_error ({exc})"
    except TimeoutError:
        return False, "datagram sent, no response"
    except OSError as exc:
        return False, f"udp_error ({exc})"
    return False, "datagram sent, no response"


def find_site(sites: dict, requested: str, protocol: str, port: int | None) -> tuple[str | None, str]:
    """Resolve the inventory site the way an operator would.

    Exact id match first; then a unique site matching the unit's protocol and
    port. Ambiguous inventories return an error listing the candidates — that
    is precisely the espot/qeeqbox class of wave bug we want surfaced.
    """
    if requested in sites:
        return requested, ""
    matches = [
        name
        for name, spec in sites.items()
        if spec.ports_map
        and protocol in spec.ports_map
        and (port is None or spec.ports_map.get(protocol) == port)
    ]
    if len(matches) == 1:
        return matches[0], f"resolved by protocol/port match: {matches[0]}"
    return (
        None,
        f"site {requested!r} not in inventory (sites: {', '.join(sorted(sites)) or 'none'}); "
        f"protocol/port match was ambiguous or empty: {matches}",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--inventory", required=True, type=Path)
    p.add_argument("--site", required=True, help="inventory site id (e.g. cowrie-ssh)")
    p.add_argument("--tps", default=None, help="TPS yaml applied exactly like the grader")
    p.add_argument("--protocol", default=None, help="override protocol filter (comma list)")
    p.add_argument("--host", default=None, help="override target host/alias")
    p.add_argument("--port", type=int, default=None, help="override port")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--resolve-site-only", action="store_true",
                   help="only resolve the inventory site (no network probes; host-safe)")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(argv)

    if not args.inventory.is_file():
        _emit(args.json, {"ok": False, "class": "config_error",
                          "error": f"inventory not found: {args.inventory}"})
        return 2
    try:
        sites = load_inventory(args.inventory)
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the operator
        _emit(args.json, {"ok": False, "class": "config_error", "error": f"inventory parse: {exc}"})
        return 2

    # TPS is applied first so the protocol list matches what the grader sees.
    tps = None
    if args.tps:
        tps_path = resolve_tps_path(str(args.tps))
        if not tps_path:
            _emit(args.json, {"ok": False, "class": "config_error",
                              "error": f"TPS not found: {args.tps}"})
            return 2
        tps = load_tps(Path(tps_path))

    probe_site = args.site
    protocol_hint = args.protocol.split(",")[0].strip() if args.protocol else ""
    site_name, note = find_site(sites, probe_site, (protocol_hint or "").lower(), args.port)
    if site_name is None:
        _emit(args.json, {"ok": False, "class": "site_missing", "error": note})
        return 2
    if args.resolve_site_only:
        if not args.json:
            print(f"site={site_name} host={args.host or sites[site_name].host}"
                  + (f" ({note})" if note else ""))
        _emit(args.json, {"ok": True, "site": site_name, "site_note": note,
                          "host": args.host or sites[site_name].host})
        return 0
    target = sites[site_name]
    if tps is not None:
        try:
            apply_tps(target, tps)
        except Exception as exc:  # noqa: BLE001
            _emit(args.json, {"ok": False, "class": "config_error",
                              "error": f"apply_tps: {exc}"})
            return 2

    host = args.host or target.host
    protocols = [p.strip().lower() for p in (args.protocol.split(",") if args.protocol else (target.protocol_list() or []))]

    results = []
    for proto in protocols:
        port = args.port or target.port_for(proto)
        if not port:
            results.append({"protocol": proto, "host": host, "port": None,
                            "reachable": False, "class": "no_port_mapped",
                            "detail": "no port mapped for protocol (grader would "
                                      "fall back to 2222 and fail)"})
            continue
        if proto in UDP_PROTOCOLS:
            ok, detail = probe_udp(host, port, proto, args.timeout)
            if ok:
                klass = "reachable"
            elif detail.startswith("dns_error"):
                klass = "dns_error"
            elif detail == "datagram sent, no response":
                klass = "udp_no_reply"
            else:
                klass = "udp_error"
        else:
            ok, detail = probe_tcp(host, port, args.timeout)
            if ok:
                klass = "reachable"
            elif detail.startswith("dns_error"):
                klass = "dns_error"
            elif "refused" in detail:
                klass = "port_closed"
            elif "timed out" in detail:
                klass = "timeout"
            else:
                klass = "port_closed"
        results.append({"protocol": proto, "host": host, "port": port,
                        "reachable": ok, "class": klass, "detail": detail})

    ok_all = bool(results) and all(r["reachable"] for r in results)
    payload = {
        "ok": ok_all,
        "inventory": str(args.inventory),
        "site": site_name,
        "site_note": note,
        "tps": str(args.tps or ""),
        "host": host,
        "results": results,
    }
    _emit(args.json, payload)
    if args.json:
        return 0 if ok_all else 1

    print(f"preflight site={site_name} host={host} -> {'PASS' if ok_all else 'FAIL'}")
    if note:
        print(f"  note: {note}")
    for r in results:
        mark = "ok " if r["reachable"] else "FAIL"
        print(f"  [{mark}] {r['protocol']} {r['host']}:{r['port']} — {r['class']}: {r['detail']}")
    if not ok_all:
        print("\nNext steps by class:")
        print("  dns_error     -> target container not running / wrong --network-alias on uhbs-lab")
        print("  port_closed   -> service not listening: enable protocol in target config or fix inventory port")
        print("  no_port_mapped-> add protocol->port under site 'ports:' in the inventory")
        print("  udp_no_reply  -> datagram service silent: verify target config or probe PDU reachability")
        print("  site_missing  -> fix --site / --target to match an inventory site id")
    return 0 if ok_all else 1


def _emit(as_json: bool, payload: dict) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    if "error" in payload:
        print(f"preflight error [{payload.get('class')}]: {payload['error']}")


if __name__ == "__main__":
    raise SystemExit(main())
