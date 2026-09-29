"""PostgreSQL wire protocol plugin — 10 Module A checks + auth-deny state.

Client-speaks-first (unlike MySQL). Framing follows the PostgreSQL frontend/backend
protocol (v3): StartupMessage and SSLRequest have no type byte; typed messages are
``type (1) + int32 length (includes self) + payload``.
"""

from __future__ import annotations

import socket
import struct

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.netutil import tcp_transact
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.tps import TPS

_PG_PROTOCOL_3 = 196608
_SSL_REQUEST_CODE = 80877103
_CANCEL_REQUEST_CODE = 80877102


def build_startup_message(
    user: str = "uhbs",
    database: str = "postgres",
    *,
    protocol: int = _PG_PROTOCOL_3,
) -> bytes:
    """Build an untyped StartupMessage (length-prefixed)."""
    params = (
        f"user\x00{user}\x00"
        f"database\x00{database}\x00"
        "\x00"
    ).encode()
    body = struct.pack("!I", protocol) + params
    return struct.pack("!I", 4 + len(body)) + body


def build_ssl_request() -> bytes:
    """Build SSLRequest (length=8, code=80877103)."""
    return struct.pack("!II", 8, _SSL_REQUEST_CODE)


def build_cancel_request(pid: int = 1, secret: int = 1) -> bytes:
    """Build CancelRequest (length=16, code=80877102)."""
    return struct.pack("!IIII", 16, _CANCEL_REQUEST_CODE, pid, secret)


def build_password_message(password: str = "uhbs-bad") -> bytes:
    """Build PasswordMessage ('p')."""
    payload = password.encode() + b"\x00"
    return b"p" + struct.pack("!I", 4 + len(payload)) + payload


def _msg_type(raw: bytes) -> bytes:
    return raw[:1] if raw else b""


def _is_auth_message(raw: bytes) -> bool:
    """Authentication* backend message starts with 'R'."""
    return len(raw) >= 9 and raw[0:1] == b"R"


def _is_error_response(raw: bytes) -> bool:
    return len(raw) >= 5 and raw[0:1] == b"E"


def _auth_type(raw: bytes) -> int | None:
    if _is_auth_message(raw) and len(raw) >= 9:
        return struct.unpack("!I", raw[5:9])[0]
    return None


class PostgresPlugin(ProtocolPlugin):
    """PostgreSQL frontend/backend protocol — 10 Module A checks."""

    name = "postgres"
    families = ("it", "database")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []

        # 1) Truncated Startup length claim — must not hang
        junk = b"\x00\x00\x00\x10\x00\x03"
        raw, _, err = tcp_transact(host, port, junk, timeout=3.0, recv_first=False)
        ok = bool(raw) or not err or (err and "timed out" not in err.lower())
        if err and not raw and "timed out" in err.lower():
            ok = False
        if not raw and not err:
            ok = True
        checks.append(
            CheckResult(
                id="postgres.fsm.truncated_startup",
                team="blue",
                passed=ok,
                detail=(
                    f"type={_msg_type(raw)!r} len={len(raw)}"
                    if raw
                    else (err or "closed")
                ),
                score=80.0 if ok else 0.0,
            )
        )

        # 2) Completely garbage bytes
        raw2, _, err2 = tcp_transact(host, port, b"\xff\xfe\xfd\xfcXXXX", timeout=3.0)
        ok2 = bool(raw2) or not err2 or (err2 and "timed out" not in err2.lower())
        if err2 and not raw2 and "timed out" in err2.lower():
            ok2 = False
        if not raw2 and not err2:
            ok2 = True
        checks.append(
            CheckResult(
                id="postgres.fsm.garbage_bytes",
                team="red",
                passed=ok2,
                detail=(raw2[:40].hex() if raw2 else (err2 or "closed")),
                score=80.0 if ok2 else 0.0,
            )
        )

        # 3) Zero-length claim
        raw3, _, err3 = tcp_transact(host, port, b"\x00\x00\x00\x00", timeout=3.0)
        ok3 = bool(raw3) or not err3 or (err3 and "timed out" not in err3.lower())
        if err3 and not raw3 and "timed out" in err3.lower():
            ok3 = False
        if not raw3 and not err3:
            ok3 = True
        checks.append(
            CheckResult(
                id="postgres.fsm.zero_length",
                team="blue",
                passed=ok3,
                detail=(raw3[:40].hex() if raw3 else (err3 or "closed")),
                score=70.0 if ok3 else 0.0,
            )
        )

        # 4) CancelRequest shape — ErrorResponse, close, or ignore without hang
        raw4, _, err4 = tcp_transact(host, port, build_cancel_request(), timeout=3.0)
        ok4 = True
        if err4 and not raw4 and "timed out" in err4.lower():
            ok4 = False
        checks.append(
            CheckResult(
                id="postgres.fsm.cancel_request",
                team="blue",
                passed=ok4,
                detail=(
                    f"type={_msg_type(raw4)!r}"
                    if raw4
                    else (err4 or "closed/no reply")
                ),
                score=100.0 if ok4 else 0.0,
            )
        )

        # 5) HTTP-shaped probe — must not look like HTTP
        raw5, _, err5 = tcp_transact(
            host, port, b"GET / HTTP/1.0\r\n\r\n", timeout=3.0
        )
        httpish = raw5.startswith(b"HTTP/") or b"HTTP/1" in raw5[:32]
        checks.append(
            CheckResult(
                id="postgres.fsm.reject_http_shape",
                team="red",
                passed=not httpish,
                detail=(raw5[:40].hex() if raw5 else (err5 or "closed")),
                score=100.0 if not httpish else 20.0,
            )
        )
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        checks: list[CheckResult] = []

        # 6) SSLRequest → 'N' or 'S'
        ssl_raw, _, ssl_err = tcp_transact(
            host, port, build_ssl_request(), timeout=3.0, recv_first=False
        )
        ssl_ok = bool(ssl_raw) and ssl_raw[:1] in (b"N", b"S")
        checks.append(
            CheckResult(
                id="postgres.nego.ssl_request",
                team="blue",
                passed=ssl_ok,
                detail=(
                    f"reply={ssl_raw[:8]!r}"
                    if ssl_raw
                    else (ssl_err or "no SSLRequest reply")
                ),
                score=100.0 if ssl_ok else 0.0,
            )
        )

        # 7) StartupMessage → Authentication* or ErrorResponse
        raw, _, err = tcp_transact(
            host, port, build_startup_message(), timeout=3.0, recv_first=False
        )
        nego_ok = _is_auth_message(raw) or _is_error_response(raw)
        detail = ""
        auth_t = _auth_type(raw)
        if auth_t is not None:
            detail = f"Authentication type={auth_t}"
        elif _is_error_response(raw):
            detail = raw[5:80].decode("utf-8", "replace")
        else:
            detail = err or f"unexpected type={_msg_type(raw)!r} len={len(raw)}"
        checks.append(
            CheckResult(
                id="postgres.nego.startup",
                team="blue",
                passed=nego_ok,
                detail=detail,
                score=100.0 if nego_ok else 0.0,
            )
        )

        # 8) Auth type is a known code (0=ok, 3=cleartext, 5=md5, 10=sasl, …)
        known = auth_t in (0, 2, 3, 5, 7, 8, 9, 10, 11, 12) if auth_t is not None else False
        # ErrorResponse instead of auth still counts as protocol-valid negotiation
        if _is_error_response(raw):
            known = True
            auth_detail = "ErrorResponse (no auth challenge)"
        else:
            auth_detail = f"auth_type={auth_t!r}"
        checks.append(
            CheckResult(
                id="postgres.nego.auth_type_known",
                team="blue",
                passed=known,
                detail=auth_detail,
                score=100.0 if known else 30.0,
            )
        )

        # 9) Second Startup still yields Auth/Error (connection independence)
        raw2, _, err2 = tcp_transact(
            host, port, build_startup_message(user="uhbs2"), timeout=3.0
        )
        ok9 = _is_auth_message(raw2) or _is_error_response(raw2)
        checks.append(
            CheckResult(
                id="postgres.nego.second_startup",
                team="blue",
                passed=ok9,
                detail=(
                    f"type={_msg_type(raw2)!r}"
                    if raw2
                    else (err2 or "no second startup reply")
                ),
                score=100.0 if ok9 else 30.0,
            )
        )

        # 10) Parameter-less / empty-user startup still framed as Auth or Error
        empty_user = build_startup_message(user="", database="postgres")
        raw3, _, err3 = tcp_transact(host, port, empty_user, timeout=3.0)
        ok10 = _is_auth_message(raw3) or _is_error_response(raw3)
        checks.append(
            CheckResult(
                id="postgres.nego.empty_user_startup",
                team="blue",
                passed=ok10,
                detail=(
                    f"type={_msg_type(raw3)!r}"
                    if raw3
                    else (err3 or "no empty-user reply")
                ),
                score=100.0 if ok10 else 40.0,
            )
        )
        return checks

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        """B1 — rejected authentication (ErrorResponse / 28P01)."""
        strict = tps is None or tps.strict_rfc_enforcement
        last_err = "no reply after StartupMessage"
        for _attempt in range(2):
            try:
                with socket.create_connection((host, int(port)), timeout=15.0) as s:
                    s.settimeout(15.0)
                    s.sendall(build_startup_message(user="uhbs_no_such_user"))
                    first = s.recv(65535)
                    if not first:
                        last_err = "no reply after StartupMessage"
                        continue
                    if _is_error_response(first):
                        return [
                            CheckResult(
                                id="postgres.state.auth_deny",
                                team="blue",
                                critical=strict,
                                passed=True,
                                detail=first[5:120].decode("utf-8", "replace"),
                                score=100.0,
                            )
                        ]
                    if _is_auth_message(first):
                        s.sendall(build_password_message("definitely-wrong-password"))
                        second = s.recv(65535)
                        denied = False
                        if _is_error_response(second):
                            denied = True
                            text = second[5:120].decode("utf-8", "replace")
                        elif second[:1] == b"R" and len(second) >= 9:
                            auth_type = struct.unpack("!I", second[5:9])[0]
                            denied = auth_type != 0
                            text = (
                                "AuthenticationOk (accepted bad password)"
                                if auth_type == 0
                                else f"Authentication type={auth_type} after PasswordMessage"
                            )
                        else:
                            text = (
                                second[:80].hex()
                                if second
                                else f"post-auth len={len(second)}"
                            )
                        return [
                            CheckResult(
                                id="postgres.state.auth_deny",
                                team="blue",
                                critical=strict,
                                passed=denied,
                                detail=(
                                    text
                                    + (
                                        ""
                                        if (denied or strict)
                                        else " (Canary/Alert mode: not hard-failed)"
                                    )
                                ),
                                score=100.0 if denied else (0.0 if strict else 35.0),
                            )
                        ]
                    last_err = f"unexpected after Startup: type={_msg_type(first)!r}"
            except OSError as exc:
                last_err = str(exc)[:160]
                continue
        return [
            CheckResult(
                id="postgres.state.auth_deny",
                team="blue",
                critical=strict,
                passed=False,
                detail=last_err,
                score=0.0 if strict else 35.0,
            )
        ]
