"""UPnP / SSDP discovery probes — M-SEARCH on UDP/1900 (RFC 8415 / UPnP Device Arch)."""

from __future__ import annotations

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.netutil import udp_transact
from uhbs_core.protocols.udp_base import UdpProtocolPlugin
from uhbs_core.tps import TPS


def build_msearch(
    *,
    st: str = "ssdp:all",
    mx: int = 1,
    host: str = "239.255.255.250:1900",
) -> bytes:
    """SSDP M-SEARCH discovery datagram."""
    return (
        b"M-SEARCH * HTTP/1.1\r\n"
        + f"HOST: {host}\r\n".encode("ascii")
        + b'MAN: "ssdp:discover"\r\n'
        + f"MX: {mx}\r\n".encode("ascii")
        + f"ST: {st}\r\n".encode("ascii")
        + b"\r\n"
    )


def is_ssdp_ok_reply(raw: bytes) -> bool:
    """True when the datagram looks like an SSDP HTTP 200 discovery response."""
    if not raw:
        return False
    upper = raw.upper()
    if not (upper.startswith(b"HTTP/1.") and b" 200" in upper[:32]):
        return False
    # Typical SSDP headers (Dionaea emits ST/USN/SERVER/LOCATION/CACHE-CONTROL).
    markers = (b"ST:", b"USN:", b"SERVER:", b"LOCATION:", b"CACHE-CONTROL:")
    return sum(1 for m in markers if m in upper) >= 2


_MSEARCH = build_msearch()


class UPnPPlugin(UdpProtocolPlugin):
    """UPnP SSDP (UDP/1900) M-SEARCH probe. ``ssdp`` is a registry alias."""

    name = "upnp"
    families = ("it", "iot")
    udp_probe_payload = _MSEARCH

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        raw, _, err = udp_transact(
            host, port, b"NOTUPNP garbage\r\n\r\n", timeout=1.5
        )
        ok = not err
        # Honest stacks ignore unknown methods; 200 OK here is weak.
        replied_ok = is_ssdp_ok_reply(raw)
        if replied_ok:
            score = 25.0
            detail = "HTTP 200 to non-M-SEARCH (over-accepting)"
        elif raw:
            score = 70.0
            detail = raw[:80].decode("utf-8", "replace")
        else:
            score = 80.0 if ok else 0.0
            detail = err or "no reply (udp accepted)"
        return [
            CheckResult(
                id="upnp.fsm.invalid",
                team="blue",
                passed=score >= 70.0,
                detail=detail,
                score=score,
            )
        ]

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        raw, _, err = udp_transact(host, port, _MSEARCH, timeout=2.0)
        replied = is_ssdp_ok_reply(raw)
        ok = not err
        return [
            CheckResult(
                id="upnp.nego.msearch",
                team="blue",
                passed=ok,
                detail=(
                    raw[:120].decode("utf-8", "replace")
                    if raw
                    else (err or "no SSDP reply (canary may be alert-only)")
                ),
                score=100.0 if replied else (35.0 if ok else 0.0),
            )
        ]

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        # Root-device ST — Dionaea default personality answers upnp:rootdevice.
        payload = build_msearch(st="upnp:rootdevice")
        raw, _, err = udp_transact(host, port, payload, timeout=2.0)
        replied = is_ssdp_ok_reply(raw)
        ok = not err
        return [
            CheckResult(
                id="upnp.state.rootdevice",
                team="blue",
                passed=ok,
                detail=(
                    raw[:120].decode("utf-8", "replace")
                    if raw
                    else (err or "rootdevice M-SEARCH sent")
                ),
                score=100.0 if replied else (50.0 if ok else 0.0),
            )
        ]
