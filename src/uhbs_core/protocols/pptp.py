"""PPTP control-channel probes — RFC 2637 Start-Control-Connection / Outgoing-Call."""

from __future__ import annotations

import struct

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.netutil import tcp_transact
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.tps import TPS

PPTP_MAGIC = 0x1A2B3C4D
PPTP_MSG_CONTROL = 1
PPTP_SCCRQ = 1
PPTP_SCCRP = 2
PPTP_OCRQ = 7

_SCCRQ_LEN = 156
_OCRQ_LEN = 168


def build_start_control_connection_request(
    hostname: str = "uhbs",
    vendor: str = "UHBS",
    *,
    protocol_version: int = 0x0100,
    framing: int = 1,
    bearer: int = 1,
    max_channels: int = 0,
    firmware: int = 1,
) -> bytes:
    """RFC 2637 Start-Control-Connection-Request (156 octets)."""
    host_b = hostname.encode("ascii", "replace")[:64].ljust(64, b"\x00")
    vend_b = vendor.encode("ascii", "replace")[:64].ljust(64, b"\x00")
    header = struct.pack(
        "!HHIHHHHIIHH",
        _SCCRQ_LEN,
        PPTP_MSG_CONTROL,
        PPTP_MAGIC,
        PPTP_SCCRQ,
        0,
        protocol_version & 0xFFFF,
        0,
        framing & 0xFFFFFFFF,
        bearer & 0xFFFFFFFF,
        max_channels & 0xFFFF,
        firmware & 0xFFFF,
    )
    return header + host_b + vend_b


def build_outgoing_call_request(
    *,
    call_id: int = 1,
    call_serial: int = 1,
    min_bps: int = 300,
    max_bps: int = 100_000_000,
) -> bytes:
    """RFC 2637 Outgoing-Call-Request (168 octets)."""
    phone = b"\x00" * 64
    subaddr = b"\x00" * 64
    header = struct.pack(
        "!HHIHHHHIIIIHHHH",
        _OCRQ_LEN,
        PPTP_MSG_CONTROL,
        PPTP_MAGIC,
        PPTP_OCRQ,
        0,
        call_id & 0xFFFF,
        call_serial & 0xFFFF,
        min_bps & 0xFFFFFFFF,
        max_bps & 0xFFFFFFFF,
        1,  # BearerType
        1,  # FramingType
        10,  # PacketWindowSize
        0,  # PacketProcessingDelay
        0,  # PhoneNumberLength
        0,  # Reserved
    )
    return header + phone + subaddr


def is_sccrp(raw: bytes) -> bool:
    """True when ``raw`` starts with a Start-Control-Connection-Reply."""
    if len(raw) < 12:
        return False
    _length, msg_type, magic, ctrl = struct.unpack_from("!HHIH", raw, 0)
    return magic == PPTP_MAGIC and msg_type == PPTP_MSG_CONTROL and ctrl == PPTP_SCCRP


def is_pptp_control(raw: bytes, *, control_type: int | None = None) -> bool:
    if len(raw) < 12:
        return False
    _length, msg_type, magic, ctrl = struct.unpack_from("!HHIH", raw, 0)
    if magic != PPTP_MAGIC or msg_type != PPTP_MSG_CONTROL:
        return False
    if control_type is None:
        return True
    return ctrl == control_type


class PPTPPlugin(ProtocolPlugin):
    """PPTP TCP/1723 control channel (SCCRQ/SCCRP + Outgoing-Call)."""

    name = "pptp"
    families = ("it", "vpn")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        # Wrong magic cookie — honest stack should not emit SCCRP.
        bad = struct.pack("!HHIHH", 12, PPTP_MSG_CONTROL, 0xDEADBEEF, PPTP_SCCRQ, 0)
        raw, _, err = tcp_transact(host, port, bad, timeout=2.0)
        if is_sccrp(raw):
            score = 20.0
            detail = "SCCRP to invalid magic (over-accepting)"
        elif raw == b"" or bool(err):
            score = 80.0
            detail = err or "connection closed / no reply to bad magic"
        else:
            score = 55.0
            detail = f"non-SCCRP reply len={len(raw)}"
        return [
            CheckResult(
                id="pptp.fsm.bad_magic",
                team="blue",
                passed=score >= 70.0,
                detail=detail,
                score=score,
            )
        ]

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        sccrq = build_start_control_connection_request()
        raw, _, err = tcp_transact(host, port, sccrq, timeout=3.0)
        ok = is_sccrp(raw)
        return [
            CheckResult(
                id="pptp.nego.sccrq",
                team="blue",
                passed=ok,
                detail=(
                    f"SCCRP len={len(raw)}"
                    if ok
                    else (err or f"no SCCRP (len={len(raw)})")
                ),
                score=100.0 if ok else (25.0 if raw and not err else 0.0),
            )
        ]

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        # One TCP session: SCCRQ then OCRQ (Dionaea ESTABLISHED path).
        script = build_start_control_connection_request() + build_outgoing_call_request()
        raw, _, err = tcp_transact(host, port, script, timeout=4.0)
        has_sccrp = is_sccrp(raw)
        # After SCCRP (156 octets typical), look for further control traffic.
        rest = raw[156:] if len(raw) >= 156 else raw[12:] if has_sccrp else b""
        has_call = is_pptp_control(rest) or (
            has_sccrp and len(raw) > 156 and is_pptp_control(raw[12:])
        )
        # Dionaea OutgoingCall_Reply is 0x20 bytes; accept any post-SCCRP control.
        if has_sccrp and len(raw) > 156:
            has_call = True
        ok = has_sccrp and (has_call or len(raw) >= 156)
        score = 100.0 if (has_sccrp and has_call) else (70.0 if has_sccrp else 0.0)
        return [
            CheckResult(
                id="pptp.state.outgoing_call",
                team="blue",
                passed=ok,
                detail=(
                    f"SCCRP+call replies len={len(raw)}"
                    if has_sccrp
                    else (err or "no PPTP control replies")
                ),
                score=score,
            )
        ]
