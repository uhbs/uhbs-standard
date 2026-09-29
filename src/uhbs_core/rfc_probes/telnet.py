"""Telnet (RFC 854) IAC / option probe — 10 Module A checks.

Stable check IDs use the ``telnet.*`` namespace (legacy ``telnet.fsm.iac_negotiation``
and ``telnet.state.login_prompt`` preserved) for longitudinal rescore compare.
"""
from __future__ import annotations

import socket

from uhbs_core.models import CheckResult

from .cache import cached_suite
from .socket_util import _port_open
from .types import RFCSuiteResult

IAC = 0xFF
WILL, WONT, DO, DONT = 0xFB, 0xFC, 0xFD, 0xFE
_LOGIN_KEYWORDS = (b"login", b"username", b"user:", b"user name", b"password")


def _negate_options(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(data) - 2:
        if data[i] == IAC and data[i + 1] in (DO, WILL) and i + 2 < len(data):
            opt = data[i + 2]
            reply = WONT if data[i + 1] == DO else DONT
            out += bytes([IAC, reply, opt])
            i += 3
        else:
            i += 1
    return bytes(out)


def _recv(sock: socket.socket, n: int = 1024) -> bytes:
    try:
        return sock.recv(n)
    except TimeoutError:
        return b""


def _probe_telnet_rfc854_uncached(host: str, port: int) -> RFCSuiteResult:
    """Ten RFC 854-oriented wire checks for Module A."""
    suite = RFCSuiteResult(protocol="telnet", rfc="RFC 854")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"telnet port {port} closed"
        return suite

    try:
        with socket.create_connection((host, port), timeout=3.0) as s:
            s.settimeout(2.0)
            first = _recv(s)
    except OSError as exc:
        suite.skipped = True
        suite.skip_reason = str(exc)
        return suite

    combined = first

    # 1. Literal IAC byte (legacy id: telnet.fsm.iac_negotiation)
    has_iac = IAC in first
    suite.checks.append(
        CheckResult(
            id="telnet.fsm.iac_negotiation",
            team="blue",
            critical=True,
            passed=has_iac,
            detail=(
                f"recv={first[:40]!r}"
                if has_iac
                else f"no IAC (0xFF) byte in response: recv={first[:40]!r}"
            ),
            score=100.0 if has_iac else 0.0,
            catalog_id="rfc854.iac_present",
        )
    )

    # 2. Known option verb (WILL/WONT/DO/DONT) after IAC
    opt_markers = (
        bytes([IAC, WILL]),
        bytes([IAC, WONT]),
        bytes([IAC, DO]),
        bytes([IAC, DONT]),
    )
    has_opt = any(b in first for b in opt_markers)
    if has_opt:
        opt_passed, opt_score = True, 100.0
    elif has_iac:
        # IAC present but no standard option verb yet (banner-only / delayed nego)
        opt_passed, opt_score = False, 40.0
    else:
        opt_passed, opt_score = False, 0.0
    suite.checks.append(
        CheckResult(
            id="telnet.fsm.option_verb",
            team="blue",
            passed=opt_passed,
            detail="WILL/WONT/DO/DONT after IAC" if has_opt else f"recv={first[:40]!r}",
            score=opt_score,
            catalog_id="rfc854.option_verb",
        )
    )

    # 3. Respond to DO/WILL with WONT/DONT — peer continues
    try:
        with socket.create_connection((host, port), timeout=3.0) as s:
            s.settimeout(2.0)
            first2 = _recv(s)
            reply = _negate_options(first2)
            second = b""
            if reply:
                s.sendall(reply)
                second = _recv(s)
            combined = first2 + second
            # Require a non-empty session (greeting and/or post-nego bytes)
            cont_ok = bool(first2) or bool(second)
            suite.checks.append(
                CheckResult(
                    id="telnet.nego.option_reply_continues",
                    team="blue",
                    passed=cont_ok,
                    detail=f"after_nego={second[:40]!r}",
                    score=100.0 if cont_ok else 30.0,
                    catalog_id="rfc854.option_reply_continues",
                )
            )
    except OSError as exc:
        suite.checks.append(
            CheckResult(
                id="telnet.nego.option_reply_continues",
                team="blue",
                passed=False,
                detail=str(exc),
                score=0.0,
                catalog_id="rfc854.option_reply_continues",
            )
        )

    # 4. Double IAC (255,255) as literal — must not hang the harness
    try:
        with socket.create_connection((host, port), timeout=3.0) as s:
            s.settimeout(2.0)
            _recv(s)
            s.sendall(bytes([IAC, IAC, ord("x")]))
            after = _recv(s)
        suite.checks.append(
            CheckResult(
                id="telnet.fsm.doubled_iac_literal",
                team="red",
                passed=True,
                detail=f"after={after[:40]!r}",
                score=100.0,
                catalog_id="rfc854.doubled_iac_literal",
            )
        )
    except OSError as exc:
        suite.checks.append(
            CheckResult(
                id="telnet.fsm.doubled_iac_literal",
                team="red",
                passed=False,
                detail=str(exc),
                score=0.0,
                catalog_id="rfc854.doubled_iac_literal",
            )
        )

    # 5. NOP (IAC 241) — tolerate without hang
    try:
        with socket.create_connection((host, port), timeout=3.0) as s:
            s.settimeout(2.0)
            _recv(s)
            s.sendall(bytes([IAC, 241]))
            after = _recv(s)
        suite.checks.append(
            CheckResult(
                id="telnet.fsm.nop_command",
                team="blue",
                passed=True,
                detail=f"after_nop={after[:40]!r}",
                score=100.0,
                catalog_id="rfc854.nop_command",
            )
        )
    except OSError as exc:
        suite.checks.append(
            CheckResult(
                id="telnet.fsm.nop_command",
                team="blue",
                passed=False,
                detail=str(exc),
                score=0.0,
                catalog_id="rfc854.nop_command",
            )
        )

    # 6. AYT (IAC 246) — optional reply; require successful exchange
    try:
        with socket.create_connection((host, port), timeout=3.0) as s:
            s.settimeout(2.0)
            _recv(s)
            s.sendall(bytes([IAC, 246]))
            after = _recv(s)
        suite.checks.append(
            CheckResult(
                id="telnet.nego.ayt_command",
                team="blue",
                passed=True,
                detail=f"after_ayt={after[:40]!r}",
                score=100.0 if after else 70.0,
                catalog_id="rfc854.ayt_command",
            )
        )
    except OSError as exc:
        suite.checks.append(
            CheckResult(
                id="telnet.nego.ayt_command",
                team="blue",
                passed=False,
                detail=str(exc),
                score=0.0,
                catalog_id="rfc854.ayt_command",
            )
        )

    # 7. Second connection independent — both sides must agree on IAC presence
    try:
        with socket.create_connection((host, port), timeout=3.0) as s1:
            s1.settimeout(2.0)
            a = _recv(s1)
        with socket.create_connection((host, port), timeout=3.0) as s2:
            s2.settimeout(2.0)
            b = _recv(s2)
        both_data = bool(a) and bool(b)
        iac_consistent = (IAC in a) == (IAC in b)
        indep = both_data and iac_consistent
        suite.checks.append(
            CheckResult(
                id="telnet.nego.second_connection_independent",
                team="blue",
                passed=indep,
                detail=f"c1={a[:20]!r} c2={b[:20]!r}",
                score=100.0 if indep else (40.0 if both_data else 0.0),
                catalog_id="rfc854.second_connection_independent",
            )
        )
    except OSError as exc:
        suite.checks.append(
            CheckResult(
                id="telnet.nego.second_connection_independent",
                team="blue",
                passed=False,
                detail=str(exc),
                score=0.0,
                catalog_id="rfc854.second_connection_independent",
            )
        )

    # 8. HTTP probe must not elicit an HTTP status line
    try:
        with socket.create_connection((host, port), timeout=3.0) as s:
            s.settimeout(2.0)
            _recv(s)
            s.sendall(b"GET / HTTP/1.1\r\n\r\n")
            after = _recv(s)
        httpish = after.startswith(b"HTTP/")
        suite.checks.append(
            CheckResult(
                id="telnet.fsm.reject_http_probe_shape",
                team="red",
                passed=not httpish,
                detail=f"after={after[:40]!r}",
                score=100.0 if not httpish else 20.0,
                catalog_id="rfc854.reject_http_probe_shape",
            )
        )
    except OSError as exc:
        suite.checks.append(
            CheckResult(
                id="telnet.fsm.reject_http_probe_shape",
                team="red",
                passed=False,
                detail=str(exc),
                score=0.0,
                catalog_id="rfc854.reject_http_probe_shape",
            )
        )

    # 9. Login-style prompt (realism; not vacuous on IAC alone)
    prompt = any(kw in combined.lower() for kw in _LOGIN_KEYWORDS)
    suite.checks.append(
        CheckResult(
            id="telnet.state.login_prompt",
            team="blue",
            passed=prompt,
            detail=f"combined={combined[:80]!r}",
            score=100.0 if prompt else (35.0 if has_iac else 0.0),
            catalog_id="rfc854.login_prompt_signal",
        )
    )

    # 10. Connect + recv yielded bytes (already have first)
    suite.checks.append(
        CheckResult(
            id="telnet.nego.connect_recv",
            team="blue",
            passed=bool(first),
            detail=f"first_len={len(first)}",
            score=100.0 if first else 0.0,
            catalog_id="rfc854.connect_recv",
        )
    )

    assert len(suite.checks) == 10, f"expected 10 telnet RFC checks, got {len(suite.checks)}"
    return suite


def probe_telnet_rfc854(host: str, port: int) -> RFCSuiteResult:
    """Cached wrapper — fsm/nego/state share one suite within the TTL window."""
    return cached_suite(
        ("telnet_rfc854", host, int(port)),
        lambda: _probe_telnet_rfc854_uncached(host, port),
    )
