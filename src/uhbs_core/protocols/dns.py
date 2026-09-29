"""DNS (UDP/TCP port 53) — RFC 1035 / RFC 7766 probes (10 Module A checks)."""

from __future__ import annotations

import struct

from uhbs_core.models import CheckOutcome, CheckResult, TargetSpec
from uhbs_core.netutil import tcp_transact, udp_transact
from uhbs_core.protocols.udp_base import UdpProtocolPlugin
from uhbs_core.tps import TPS

_RCODE_NAMES = {
    0: "NOERROR",
    1: "FORMERR",
    2: "SERVFAIL",
    3: "NXDOMAIN",
    4: "NOTIMP",
    5: "REFUSED",
}


def encode_qname(name: str) -> bytes:
    """Wire-format QNAME (RFC 1035). ``'.'`` is the root label."""
    name = (name or "").strip()
    if name in {".", ""}:
        return b"\x00"
    if name.endswith("."):
        name = name[:-1]
    labels = name.split(".")
    out = bytearray()
    for label in labels:
        if not label or len(label) > 63:
            raise ValueError(f"invalid DNS label in {name!r}")
        out.append(len(label))
        out.extend(label.encode("ascii"))
    out.append(0)
    return bytes(out)


def build_dns_query(
    qname: str,
    *,
    qtype: int = 1,
    qclass: int = 1,
    txid: int = 0x4D48,
    rd: bool = True,
    opcode: int = 0,
) -> bytes:
    """Standard query (opcode 0 by default) with QDCOUNT=1."""
    flags = ((opcode & 0xF) << 11) | (0x0100 if rd else 0x0000)
    header = struct.pack("!HHHHHH", txid & 0xFFFF, flags, 1, 0, 0, 0)
    return header + encode_qname(qname) + struct.pack("!HH", qtype, qclass)


def parse_dns_header(data: bytes) -> dict[str, int] | None:
    if len(data) < 12:
        return None
    txid, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", data[:12])
    return {
        "id": txid,
        "flags": flags,
        "qr": (flags >> 15) & 1,
        "opcode": (flags >> 11) & 0xF,
        "rcode": flags & 0xF,
        "qdcount": qd,
        "ancount": an,
        "nscount": ns,
        "arcount": ar,
        "rd": (flags >> 8) & 1,
    }


def _rcode_label(rcode: int) -> str:
    return _RCODE_NAMES.get(rcode, f"RCODE{rcode}")


def _detail_header(raw: bytes) -> str:
    hdr = parse_dns_header(raw)
    if hdr is None:
        return raw[:40].hex() if raw else "empty"
    return (
        f"id=0x{hdr['id']:04x} QR={hdr['qr']} "
        f"opcode={hdr['opcode']} {_rcode_label(hdr['rcode'])} "
        f"qd={hdr['qdcount']} an={hdr['ancount']}"
    )


def _score_malformed_reply(raw: bytes, err: str) -> tuple[float, bool, str]:
    """Score responses to malformed / inconsistent DNS datagrams."""
    if err:
        return 0.0, False, err
    if not raw:
        return 55.0, False, "no UDP reply (timeout; alert-only canary possible)"
    hdr = parse_dns_header(raw)
    if hdr is None:
        return 45.0, False, f"reply too short for DNS header ({len(raw)} bytes)"
    detail = _detail_header(raw)
    if hdr["qr"] == 1 and hdr["rcode"] == 1:
        return 100.0, True, detail
    if hdr["qr"] == 1 and hdr["rcode"] in (2, 5):
        return 85.0, True, detail
    if hdr["qr"] == 1 and hdr["rcode"] == 0:
        return 35.0, False, detail + " (NOERROR on malformed input)"
    if hdr["qr"] == 0:
        return 40.0, False, detail + " (response QR not set)"
    return 50.0, False, detail


def _score_valid_reply(raw: bytes, err: str, *, txid: int) -> tuple[float, bool, str]:
    if err:
        return 0.0, False, err
    if not raw:
        return 35.0, False, "no DNS reply (canary may be alert-only)"
    hdr = parse_dns_header(raw)
    if hdr is None:
        return 25.0, False, f"short reply ({len(raw)} bytes)"
    detail = _detail_header(raw)
    if hdr["id"] != (txid & 0xFFFF):
        return 30.0, False, detail + " (ID mismatch)"
    if hdr["qr"] != 1:
        return 30.0, False, detail + " (not a response)"
    if hdr["opcode"] != 0:
        return 40.0, False, detail + " (non-query opcode in response)"
    if hdr["rcode"] in (0, 3):
        return 100.0, True, detail
    if hdr["rcode"] in (1, 2, 5):
        return 75.0, True, detail
    return 60.0, hdr["rcode"] <= 5, detail


def tcp_dns_transact(
    host: str,
    port: int,
    query: bytes,
    *,
    timeout: float = 2.0,
) -> tuple[bytes, float, str]:
    """RFC 7766 length-prefixed DNS over TCP."""
    framed = struct.pack("!H", len(query)) + query
    raw, rtt, err = tcp_transact(host, port, framed, timeout=timeout)
    if err or len(raw) < 2:
        return raw, rtt, err
    msg_len = struct.unpack("!H", raw[:2])[0]
    body = raw[2 : 2 + msg_len] if msg_len <= len(raw) - 2 else raw[2:]
    return body, rtt, err


_NEGO_QNAME = "example.com"
_NEGO_TXID = 0x4D48
_STATE_TXID = 0x4D49
_UDP_PROBE = build_dns_query(_NEGO_QNAME, txid=0x0001)


class DNSPlugin(UdpProtocolPlugin):
    """DNS resolver-style UDP/TCP probes (port 53) — 10 Module A checks."""

    name = "dns"
    families = ("it",)
    udp_probe_payload = _UDP_PROBE

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []

        # 1) Truncated header
        truncated = b"\x00\x01"
        raw, _, err = udp_transact(host, port, truncated, timeout=1.5)
        score, passed, detail = _score_malformed_reply(raw, err)
        checks.append(
            CheckResult(
                id="dns.fsm.truncated_header",
                team="blue",
                passed=passed,
                detail=detail,
                score=score,
            )
        )

        # 2) QDCOUNT inconsistent with body
        bad_qd = struct.pack("!HHHHHH", 0xBEEF, 0x0100, 10, 0, 0, 0)
        raw2, _, err2 = udp_transact(host, port, bad_qd, timeout=1.5)
        score2, passed2, detail2 = _score_malformed_reply(raw2, err2)
        checks.append(
            CheckResult(
                id="dns.fsm.bad_qdcount",
                team="blue",
                passed=passed2,
                detail=detail2,
                score=score2,
            )
        )

        # 3) Incomplete QNAME (length claims bytes that never arrive)
        incomplete = struct.pack("!HHHHHH", 0xC0DE, 0x0100, 1, 0, 0, 0) + b"\x07exam"
        raw3, _, err3 = udp_transact(host, port, incomplete, timeout=1.5)
        score3, passed3, detail3 = _score_malformed_reply(raw3, err3)
        checks.append(
            CheckResult(
                id="dns.fsm.incomplete_qname",
                team="blue",
                passed=passed3,
                detail=detail3,
                score=score3,
            )
        )

        # 4) QDCOUNT=0 with otherwise-valid header
        zero_qd = struct.pack("!HHHHHH", 0x0A0A, 0x0100, 0, 0, 0, 0)
        raw4, _, err4 = udp_transact(host, port, zero_qd, timeout=1.5)
        score4, passed4, detail4 = _score_malformed_reply(raw4, err4)
        checks.append(
            CheckResult(
                id="dns.fsm.zero_qdcount",
                team="blue",
                passed=passed4,
                detail=detail4,
                score=score4,
            )
        )

        # 5) Non-query opcode (UPDATE=5) — prefer NOTIMP/FORMERR/REFUSED
        update_q = build_dns_query(_NEGO_QNAME, txid=0x5555, opcode=5)
        raw5, _, err5 = udp_transact(host, port, update_q, timeout=1.5)
        if err5:
            score5, passed5, detail5 = 0.0, False, err5
        elif not raw5:
            score5, passed5, detail5 = 50.0, False, "no reply to UPDATE opcode"
        else:
            hdr5 = parse_dns_header(raw5)
            detail5 = _detail_header(raw5)
            if hdr5 and hdr5["qr"] == 1 and hdr5["rcode"] in (1, 4, 5):
                score5, passed5 = 100.0, True
            elif hdr5 and hdr5["qr"] == 1 and hdr5["rcode"] in (0, 3):
                # Accepted UPDATE-shaped query as a normal lookup — soft fail
                score5, passed5 = 40.0, False
                detail5 += " (NOERROR/NXDOMAIN on UPDATE opcode)"
            elif hdr5 and hdr5["qr"] == 1:
                score5, passed5 = 55.0, False
                detail5 += " (unexpected RCODE on UPDATE)"
            else:
                score5, passed5 = 30.0, False
        checks.append(
            CheckResult(
                id="dns.fsm.opcode_update",
                team="red",
                passed=passed5,
                detail=detail5,
                score=score5,
            )
        )
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []

        # 6) UDP A query
        query = build_dns_query(_NEGO_QNAME, txid=_NEGO_TXID)
        raw, _, err = udp_transact(host, port, query, timeout=2.0)
        score, passed, detail = _score_valid_reply(raw, err, txid=_NEGO_TXID)
        checks.append(
            CheckResult(
                id="dns.nego.udp_a",
                team="blue",
                passed=passed,
                detail=detail,
                score=score,
            )
        )

        # 7) RFC 7766 TCP (optional)
        tcp_raw, _, tcp_err = tcp_dns_transact(host, port, query, timeout=2.0)
        if tcp_err and not tcp_raw:
            checks.append(
                CheckResult(
                    id="dns.nego.tcp_a",
                    team="blue",
                    outcome=CheckOutcome.NOT_TESTED,
                    detail=tcp_err or "no TCP DNS reply",
                    score=0.0,
                    mandatory=False,
                )
            )
        else:
            tcp_score, tcp_passed, tcp_detail = _score_valid_reply(
                tcp_raw, tcp_err, txid=_NEGO_TXID
            )
            checks.append(
                CheckResult(
                    id="dns.nego.tcp_a",
                    team="blue",
                    passed=tcp_passed,
                    detail=tcp_detail,
                    score=tcp_score,
                )
            )

        # 8) Transaction ID echo
        txid = 0xA11E
        q_id = build_dns_query(_NEGO_QNAME, txid=txid)
        raw_id, _, err_id = udp_transact(host, port, q_id, timeout=2.0)
        hdr_id = parse_dns_header(raw_id) if raw_id else None
        id_ok = bool(hdr_id) and hdr_id["id"] == txid and hdr_id["qr"] == 1
        checks.append(
            CheckResult(
                id="dns.nego.id_echo",
                team="blue",
                passed=id_ok,
                detail=_detail_header(raw_id) if raw_id else (err_id or "no reply"),
                score=100.0 if id_ok else 25.0,
            )
        )

        # 9) AAAA query still yields a DNS response
        q_aaaa = build_dns_query(_NEGO_QNAME, qtype=28, txid=_STATE_TXID)
        raw_aaaa, _, err_aaaa = udp_transact(host, port, q_aaaa, timeout=2.0)
        score_a, passed_a, detail_a = _score_valid_reply(
            raw_aaaa, err_aaaa, txid=_STATE_TXID
        )
        checks.append(
            CheckResult(
                id="dns.nego.aaaa",
                team="blue",
                passed=passed_a,
                detail=detail_a,
                score=score_a,
            )
        )

        # 10) RD bit preserved / response has QR
        q_rd = build_dns_query(_NEGO_QNAME, txid=0x0D00, rd=True)
        raw_rd, _, err_rd = udp_transact(host, port, q_rd, timeout=2.0)
        hdr_rd = parse_dns_header(raw_rd) if raw_rd else None
        rd_ok = bool(hdr_rd) and hdr_rd["qr"] == 1 and hdr_rd.get("rd") == 1
        checks.append(
            CheckResult(
                id="dns.nego.rd_echo",
                team="blue",
                passed=rd_ok,
                detail=_detail_header(raw_rd) if raw_rd else (err_rd or "no reply"),
                score=100.0 if rd_ok else 40.0,
            )
        )
        return checks

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        q1 = build_dns_query(_NEGO_QNAME, qtype=1, txid=_NEGO_TXID)
        q2 = build_dns_query(_NEGO_QNAME, qtype=28, txid=_STATE_TXID)
        raw1, _, err1 = udp_transact(host, port, q1, timeout=2.0)
        raw2, _, err2 = udp_transact(host, port, q2, timeout=2.0)
        score1, ok1, detail1 = _score_valid_reply(raw1, err1, txid=_NEGO_TXID)
        score2, ok2, detail2 = _score_valid_reply(raw2, err2, txid=_STATE_TXID)

        consistent = ok1 and ok2
        if ok1 and ok2:
            h1 = parse_dns_header(raw1) or {}
            h2 = parse_dns_header(raw2) or {}
            consistent = h1.get("opcode") == 0 and h2.get("opcode") == 0

        combined_score = min(score1, score2) if (raw1 or raw2) else 35.0
        if consistent:
            combined_score = max(combined_score, 85.0)

        return [
            CheckResult(
                id="dns.state.second_query",
                team="blue",
                passed=combined_score >= 70.0,
                detail=f"A: {detail1}; AAAA: {detail2}",
                score=combined_score,
            )
        ]
