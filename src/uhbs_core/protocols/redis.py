"""Redis honeypot grading plugin — Module A/B fidelity beyond PING/SET stubs.

Focus: discriminate shallow decoys (always-+PONG / always-+OK) from servers
that look real enough to engage (RESP errors, arity checks, INFO, exact
SET/GET, and cross-connection key persistence). RESP2 over TCP.
"""

from __future__ import annotations

import socket
import time

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.tps import TPS

_MARKER_KEY = "uhbs_marker"
_ECHO_PAYLOAD = "uhbs-echo"


def _ot_timeout(tps: TPS | None, default: float = 3.0) -> float:
    if tps and isinstance(tps.raw, dict):
        for block in (tps.raw.get("performance_baseline"), tps.raw.get("experimental"), tps.raw):
            if isinstance(block, dict) and "probe_timeout_sec" in block:
                try:
                    return float(block["probe_timeout_sec"])
                except (TypeError, ValueError):
                    pass
    return default


def encode_command(*parts: str | bytes) -> bytes:
    """Encode a Redis command as a RESP Array."""
    out = [f"*{len(parts)}\r\n".encode()]
    for part in parts:
        raw = part if isinstance(part, bytes) else str(part).encode("utf-8")
        out.append(f"${len(raw)}\r\n".encode())
        out.append(raw)
        out.append(b"\r\n")
    return b"".join(out)


def is_resp_error(raw: bytes) -> bool:
    text = raw.decode("utf-8", "replace")
    return text.startswith("-") or "ERR" in text.upper()


def is_simple_string(raw: bytes, expected: str) -> bool:
    return raw.decode("utf-8", "replace").startswith(f"+{expected}")


def is_pong(raw: bytes) -> bool:
    return is_simple_string(raw, "PONG") or b"PONG" in raw.upper()


def is_ok(raw: bytes) -> bool:
    return is_simple_string(raw, "OK") or b"+OK" in raw


def parse_bulk_string(raw: bytes) -> str | None:
    """Parse the first RESP bulk string (``$N\\r\\n...``) if present."""
    text = raw.decode("utf-8", "replace")
    if "$" not in text:
        return None
    try:
        start = text.index("$")
        line_end = text.index("\r\n", start)
        n = int(text[start + 1 : line_end])
        if n < 0:
            return None
        body_start = line_end + 2
        return text[body_start : body_start + n]
    except (ValueError, IndexError):
        return None


def looks_like_info_server(raw: bytes) -> bool:
    lower = raw.lower()
    return b"redis_version" in lower or b"# server" in lower or b"tcp_port" in lower


def _recv_some(sock: socket.socket, max_bytes: int = 65535) -> bytes:
    try:
        return sock.recv(max_bytes)
    except TimeoutError:
        return b""


def _close(sock: socket.socket | None) -> None:
    if sock is None:
        return
    try:
        sock.close()
    except OSError:
        pass


def _open(host: str, port: int, timeout: float) -> socket.socket:
    sock = socket.create_connection((host, port), timeout=timeout)
    sock.settimeout(timeout)
    return sock


def _transact(
    host: str, port: int, payload: bytes, *, timeout: float
) -> tuple[bytes, str]:
    try:
        with _open(host, port, timeout) as sock:
            sock.sendall(payload)
            return _recv_some(sock), ""
    except OSError as exc:
        return b"", str(exc)


def _session_commands(
    host: str, port: int, commands: list[bytes], *, timeout: float
) -> tuple[list[bytes], str]:
    """Run multiple RESP commands on one TCP session; return one reply blob per send."""
    replies: list[bytes] = []
    try:
        sock = _open(host, port, timeout)
    except OSError as exc:
        return [], str(exc)
    try:
        for cmd in commands:
            sock.sendall(cmd)
            replies.append(_recv_some(sock))
        return replies, ""
    except OSError as exc:
        return replies, str(exc)
    finally:
        _close(sock)


class RedisPlugin(ProtocolPlugin):
    name = "redis"
    families = ("it", "database")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        checks: list[CheckResult] = []

        # 1) Unknown verb → real RESP error (not +OK / +PONG).
        raw, err = _transact(host, port, b"Garbage\r\n", timeout=timeout)
        text = raw.decode("utf-8", "replace")
        if is_resp_error(raw):
            score = 100.0
            detail = text[:120]
        elif raw == b"" or bool(err):
            score = 60.0
            detail = err or "connection closed on invalid verb (no RESP error)"
        else:
            score = 20.0
            detail = text[:120] or "non-error reply to invalid verb"
        checks.append(
            CheckResult(
                id="redis.fsm.invalid_verb",
                team="blue",
                passed=score >= 70.0,
                detail=detail,
                score=score,
            )
        )

        # 2) Wrong arity — GET with no key must error (shallow stubs often +OK/+PONG).
        raw, err = _transact(host, port, encode_command("GET"), timeout=timeout)
        text = raw.decode("utf-8", "replace")
        ok = is_resp_error(raw)
        stub_smell = is_ok(raw) or is_pong(raw)
        if ok:
            score = 100.0
            detail = text[:120]
        elif stub_smell:
            score = 15.0
            detail = f"stub-like success on wrong arity: {text[:80]}"
        elif raw == b"" or bool(err):
            score = 55.0
            detail = err or "closed on wrong-arity GET"
        else:
            score = 25.0
            detail = text[:120]
        checks.append(
            CheckResult(
                id="redis.fsm.wrong_arity",
                team="red",
                passed=ok,
                detail=detail,
                score=score,
            )
        )

        # 3) Truncated RESP array — must not hang the harness.
        ok = False
        detail = "hang/timeout"
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(b"*3\r\n$3\r\nSET\r\n")
                raw = _recv_some(sock)
                ok = True
                detail = f"truncated RESP handled recv={raw[:24]!r}"
        except OSError as exc:
            ok = True
            detail = str(exc)
        checks.append(
            CheckResult(
                id="redis.fsm.truncated_array",
                team="red",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 20.0,
            )
        )
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        strict = bool(tps and tps.strict_rfc_enforcement)
        checks: list[CheckResult] = []

        raw, err = _transact(host, port, encode_command("PING"), timeout=timeout)
        text = raw.decode("utf-8", "replace")
        ok = is_pong(raw)
        checks.append(
            CheckResult(
                id="redis.nego.ping",
                team="blue",
                passed=ok,
                detail=text[:80] if text else (err or "no PONG"),
                score=100.0 if ok else 0.0,
                critical=strict,
            )
        )

        raw, err = _transact(
            host, port, encode_command("ECHO", _ECHO_PAYLOAD), timeout=timeout
        )
        echoed = parse_bulk_string(raw)
        ok = echoed == _ECHO_PAYLOAD or _ECHO_PAYLOAD.encode() in raw
        checks.append(
            CheckResult(
                id="redis.nego.echo",
                team="blue",
                passed=ok,
                detail=(
                    f"echoed={echoed!r}"
                    if echoed is not None
                    else (raw[:80].decode("utf-8", "replace") or err or "no ECHO body")
                ),
                score=100.0 if ok else 20.0,
            )
        )

        raw, err = _transact(host, port, encode_command("INFO", "server"), timeout=timeout)
        ok = looks_like_info_server(raw)
        checks.append(
            CheckResult(
                id="redis.nego.info_server",
                team="blue",
                passed=ok,
                detail=(
                    raw[:100].decode("utf-8", "replace")
                    if raw
                    else (err or "no INFO server body")
                ),
                score=100.0 if ok else 25.0,
            )
        )
        return checks

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        checks: list[CheckResult] = []
        marker = "1"

        replies, err = _session_commands(
            host,
            port,
            [
                encode_command("SET", _MARKER_KEY, marker),
                encode_command("GET", _MARKER_KEY),
            ],
            timeout=timeout,
        )
        set_raw = replies[0] if replies else b""
        get_raw = replies[1] if len(replies) > 1 else b""
        got = parse_bulk_string(get_raw)
        ok = is_ok(set_raw) and (got == marker or marker.encode() in get_raw)
        checks.append(
            CheckResult(
                id="redis.state.set_get",
                team="blue",
                passed=ok,
                detail=(
                    f"SET={set_raw[:40]!r} GET={got!r}"
                    if set_raw or get_raw
                    else (err or "SET/GET failed")
                ),
                score=100.0 if ok else 20.0,
                critical=True,
            )
        )

        replies, err = _session_commands(
            host,
            port,
            [
                encode_command("SET", "uhbs_incr", "0"),
                encode_command("INCR", "uhbs_incr"),
                encode_command("GET", "uhbs_incr"),
            ],
            timeout=timeout,
        )
        incr_raw = replies[1] if len(replies) > 1 else b""
        get_raw = replies[2] if len(replies) > 2 else b""
        # INCR returns an integer reply ":1\r\n"
        incr_ok = incr_raw.startswith(b":1") or b":1" in incr_raw
        get_ok = parse_bulk_string(get_raw) == "1" or b"1" in get_raw
        ok = incr_ok and get_ok
        checks.append(
            CheckResult(
                id="redis.state.incr",
                team="blue",
                passed=ok,
                detail=(
                    f"incr={incr_raw[:20]!r} get={get_raw[:20]!r}"
                    if incr_raw or get_raw
                    else (err or "INCR failed")
                ),
                score=100.0 if ok else 25.0,
            )
        )

        replies, err = _session_commands(
            host,
            port,
            [
                encode_command("SET", "uhbs_del", "x"),
                encode_command("DEL", "uhbs_del"),
                encode_command("EXISTS", "uhbs_del"),
            ],
            timeout=timeout,
        )
        del_raw = replies[1] if len(replies) > 1 else b""
        exists_raw = replies[2] if len(replies) > 2 else b""
        del_ok = del_raw.startswith(b":1") or b":1" in del_raw
        exists_ok = exists_raw.startswith(b":0") or b":0" in exists_raw
        ok = del_ok and exists_ok
        checks.append(
            CheckResult(
                id="redis.state.del_exists",
                team="blue",
                passed=ok,
                detail=(
                    f"del={del_raw[:20]!r} exists={exists_raw[:20]!r}"
                    if del_raw or exists_raw
                    else (err or "DEL/EXISTS failed")
                ),
                score=100.0 if ok else 25.0,
            )
        )
        return checks

    def probe_payload(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        """Cross-connection SET→GET — strongest shallow-stub discriminator."""
        timeout = _ot_timeout(tps)
        key = "uhbs_cross"
        value = f"uhbs-{int(time.time())}"

        set_raw, err = _transact(
            host, port, encode_command("SET", key, value), timeout=timeout
        )
        if not is_ok(set_raw):
            return [
                CheckResult(
                    id="redis.payload.cross_conn_get",
                    team="red",
                    passed=False,
                    detail=(
                        set_raw[:80].decode("utf-8", "replace")
                        if set_raw
                        else (err or "SET failed before cross-conn GET")
                    ),
                    score=10.0,
                    critical=True,
                )
            ]

        get_raw, err2 = _transact(host, port, encode_command("GET", key), timeout=timeout)
        got = parse_bulk_string(get_raw)
        ok = got == value
        return [
            CheckResult(
                id="redis.payload.cross_conn_get",
                team="red",
                passed=ok,
                detail=(
                    f"cross-conn GET returned {got!r}"
                    if got is not None
                    else (
                        get_raw[:80].decode("utf-8", "replace")
                        if get_raw
                        else (err2 or "no GET body on second connection")
                    )
                ),
                score=100.0 if ok else 10.0,
                critical=True,
                evidence=[get_raw[:40].hex()] if get_raw else [],
            )
        ]
