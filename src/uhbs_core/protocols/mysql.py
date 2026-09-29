"""MySQL wire protocol plugin — 10 Module A checks + auth-deny state."""

from __future__ import annotations

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.netutil import tcp_transact
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.tps import TPS


def _pkt_payload(raw: bytes) -> bytes:
    """Strip 4-byte MySQL packet header when present."""
    if len(raw) >= 4:
        claimed = int.from_bytes(raw[0:3], "little")
        if claimed + 4 <= len(raw):
            return raw[4 : 4 + claimed]
        return raw[4:]
    return raw


def _greeting_fields(raw: bytes) -> dict[str, object]:
    """Best-effort parse of Initial Handshake Packet fields."""
    out: dict[str, object] = {"ok": False}
    payload = _pkt_payload(raw)
    if not payload:
        return out
    out["protocol"] = payload[0]
    if payload[0] != 0x0A:
        return out
    # version string NUL-terminated
    try:
        end = payload.index(b"\x00", 1)
    except ValueError:
        return out
    out["version"] = payload[1:end].decode("utf-8", "replace")
    rest = payload[end + 1 :]
    if len(rest) < 4:
        return out
    out["thread_id"] = int.from_bytes(rest[0:4], "little")
    # auth plugin data part 1 (8) + filler (1) + capability lower (2)
    if len(rest) >= 15:
        out["capability_low"] = int.from_bytes(rest[13:15], "little")
        out["ok"] = True
    # optional: auth plugin name at end of modern greetings
    if b"mysql_native_password" in payload or b"caching_sha2_password" in payload:
        out["auth_plugin"] = True
    return out


class MySQLPlugin(ProtocolPlugin):
    """MySQL wire protocol (handshake / auth deny) — 10 Module A checks."""

    name = "mysql"
    families = ("it", "database")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []

        # 1) Truncated/garbage client packet after greeting
        raw, _, err = tcp_transact(
            host, port, b"\x01\x00\x00\x01\xff", timeout=3.0, recv_first=True
        )
        ok = bool(raw) or not err
        checks.append(
            CheckResult(
                id="mysql.fsm.truncated_auth",
                team="blue",
                passed=ok,
                detail=(raw[:80].hex() if raw else (err or "closed")),
                score=80.0 if ok else 0.0,
            )
        )

        # 2) Oversize length claim — must not hang
        huge = b"\xff\xff\xff\x01" + b"\x00" * 8
        raw2, _, err2 = tcp_transact(host, port, huge, timeout=3.0, recv_first=True)
        ok2 = bool(raw2) or not err2 or (err2 and "timed out" not in err2.lower())
        if err2 and not raw2 and "timed out" in err2.lower():
            ok2 = False
        checks.append(
            CheckResult(
                id="mysql.fsm.oversize_length",
                team="red",
                passed=ok2,
                detail=(raw2[:40].hex() if raw2 else (err2 or "closed")),
                score=80.0 if ok2 else 0.0,
            )
        )

        # 3) Zero-length client packet (header only nonsense)
        raw3, _, err3 = tcp_transact(
            host, port, b"\x00\x00\x00\x01", timeout=3.0, recv_first=True
        )
        ok3 = bool(raw3) or not err3
        checks.append(
            CheckResult(
                id="mysql.fsm.zero_length_pkt",
                team="blue",
                passed=ok3,
                detail=(raw3[:40].hex() if raw3 else (err3 or "closed")),
                score=70.0 if ok3 else 0.0,
            )
        )

        # 4) HTTP-shaped probe after greeting — should not look like HTTP
        raw4, _, err4 = tcp_transact(
            host, port, b"GET / HTTP/1.0\r\n\r\n", timeout=3.0, recv_first=True
        )
        httpish = raw4.upper().startswith(b"HTTP/") or b"HTTP/1" in raw4[:40]
        # Greeting bytes before our send still count; fail only if whole reply is HTTP
        if len(raw4) > 5 and raw4[4] == 0x0A:
            httpish = False
        checks.append(
            CheckResult(
                id="mysql.fsm.reject_http_shape",
                team="red",
                passed=not httpish,
                detail=(raw4[:60].hex() if raw4 else (err4 or "closed")),
                score=100.0 if not httpish else 20.0,
            )
        )

        # 5) Second connection still greets (independence)
        g1, _, e1 = tcp_transact(host, port, b"", timeout=3.0, recv_first=True)
        g2, _, e2 = tcp_transact(host, port, b"", timeout=3.0, recv_first=True)
        ok5 = (len(g1) >= 5 and g1[4] == 0x0A) and (len(g2) >= 5 and g2[4] == 0x0A)
        checks.append(
            CheckResult(
                id="mysql.fsm.second_connection",
                team="blue",
                passed=ok5,
                detail=f"c1={len(g1)} c2={len(g2)} e1={e1!r} e2={e2!r}",
                score=100.0 if ok5 else 30.0,
            )
        )
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []
        raw, _, err = tcp_transact(host, port, b"", timeout=3.0, recv_first=True)
        fields = _greeting_fields(raw)
        banner_ok = len(raw) >= 5 and (
            raw[4] == 0x0A or b"mysql" in raw.lower() or b"mariadb" in raw.lower()
        )

        # 6) Handshake present
        checks.append(
            CheckResult(
                id="mysql.nego.handshake",
                team="blue",
                passed=banner_ok,
                detail=(
                    raw[5:40].decode("utf-8", "replace")
                    if len(raw) > 5
                    else (err or "no greeting")
                ),
                score=100.0 if banner_ok else 0.0,
            )
        )

        # 7) Protocol version 0x0a
        proto_ok = fields.get("protocol") == 0x0A
        checks.append(
            CheckResult(
                id="mysql.nego.protocol_version",
                team="blue",
                passed=bool(proto_ok),
                detail=f"protocol={fields.get('protocol')!r}",
                score=100.0 if proto_ok else 0.0,
            )
        )

        # 8) Version string present
        version = str(fields.get("version") or "")
        ver_ok = bool(version) and any(ch.isdigit() for ch in version)
        checks.append(
            CheckResult(
                id="mysql.nego.version_string",
                team="blue",
                passed=ver_ok,
                detail=f"version={version!r}" if version else (err or "no version"),
                score=100.0 if ver_ok else 20.0,
            )
        )

        # 9) Thread / connection id
        tid = fields.get("thread_id")
        tid_ok = isinstance(tid, int)
        checks.append(
            CheckResult(
                id="mysql.nego.thread_id",
                team="blue",
                passed=tid_ok,
                detail=f"thread_id={tid!r}",
                score=100.0 if tid_ok else 20.0,
            )
        )

        # 10) Capability flags lower 16 bits present
        caps = fields.get("capability_low")
        caps_ok = isinstance(caps, int) and caps != 0
        checks.append(
            CheckResult(
                id="mysql.nego.capability_flags",
                team="blue",
                passed=caps_ok,
                detail=f"capability_low={caps!r} auth_plugin={fields.get('auth_plugin')}",
                score=100.0 if caps_ok else 25.0,
            )
        )
        return checks

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        """B1 — after the handshake, an unrecognized user must be denied."""
        strict = tps is None or tps.strict_rfc_enforcement
        greeting, _, err = tcp_transact(host, port, b"", timeout=3.0, recv_first=True)
        if err and not greeting:
            return [
                CheckResult(
                    id="mysql.state.auth_deny",
                    team="blue",
                    critical=strict,
                    passed=False,
                    detail=err,
                    score=0.0 if strict else 35.0,
                )
            ]
        user = b"uhbs\x00"
        auth = (
            b"\x85\xa2\x1a\x00"
            + b"\x00\x00\x00\x01"
            + b"\x21"
            + (b"\x00" * 23)
            + user
            + b"\x00"
        )
        pkt = len(auth).to_bytes(3, "little") + b"\x01" + auth
        raw, _, err2 = tcp_transact(host, port, pkt, timeout=3.0, recv_first=True)
        text = raw.decode("utf-8", "replace")
        denied = (
            (len(raw) > 4 and raw[4] == 0xFF)
            or b"Access denied" in raw
            or b"28000" in raw
        )
        return [
            CheckResult(
                id="mysql.state.auth_deny",
                team="blue",
                critical=strict,
                passed=denied,
                detail=(
                    (text[:120] if text else (err2 or f"greet={len(greeting)}"))
                    + ("" if (denied or strict) else " (Canary/Alert mode: not hard-failed)")
                ),
                score=100.0 if denied else (0.0 if strict else 35.0),
            )
        ]
