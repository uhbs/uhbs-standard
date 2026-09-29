"""HTTP/1.1 (RFC 9110 / 9112) request/response probe — 10 Module A checks."""
from __future__ import annotations

import re

from uhbs_core.models import CheckResult

from .cache import cached_suite
from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

_HTTP_STATUS = re.compile(rb"^HTTP/1\.[01] (\d{3})", re.MULTILINE)


def _status(raw: bytes) -> int | None:
    m = _HTTP_STATUS.search(raw)
    return int(m.group(1)) if m else None


def _probe_http_rfc9110_uncached(host: str, port: int) -> RFCSuiteResult:
    """Ten RFC 9110/9112 wire checks for Module A."""
    suite = RFCSuiteResult(protocol="http", rfc="RFC 9110/9112")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"http port {port} closed"
        return suite

    # 1. Valid GET — expect HTTP/1.x status
    req = b"GET / HTTP/1.1\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    suite.checks.append(
        CheckResult(
            id="rfc9110.valid_get_status",
            team="blue",
            passed=code is not None,
            detail=(
                f"HTTP {code}"
                if code is not None
                else (err or raw[:80].decode("utf-8", "replace"))
            ),
            score=100.0 if code is not None else 0.0,
        )
    )

    # 2. Body bytes before request line — expect 4xx or close, not 2xx
    junk = b"{'oops':true}\r\nGET / HTTP/1.1\r\nHost: x\r\n\r\n"
    raw, _, err = _transact(host, port, junk, recv_first=False)
    code = _status(raw)
    ok = code is None or code >= 400
    suite.checks.append(
        CheckResult(
            id="rfc9110.reject_body_before_headers",
            team="red",
            passed=ok,
            detail=f"status={code}" if code is not None else (err or "connection closed"),
            score=100.0 if ok else 0.0,
            evidence=[raw[:200].decode("utf-8", "replace")],
        )
    )

    # 3. Bare LF framing (RFC 9112 prefers CRLF)
    req = b"GET / HTTP/1.1\nHost: bench.invalid\nConnection: close\n\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    suite.checks.append(
        CheckResult(
            id="rfc9112.bare_lf_framing",
            team="blue",
            passed=code is not None or err == "",
            detail=(f"HTTP {code}" if code is not None else "accepted/closed without HTTP status"),
            score=100.0 if (code is not None or raw == b"") else 20.0,
        )
    )

    # 4. Invalid header formatting
    req = (
        b"GET / HTTP/1.1\r\n"
        b"Host : bench.invalid\r\n"
        b"X-Bad\x00Header: 1\r\n"
        b"Connection: close\r\n\r\n"
    )
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    ok = code is None or code >= 400
    suite.checks.append(
        CheckResult(
            id="rfc9110.invalid_header_syntax",
            team="red",
            passed=ok,
            detail=f"status={code}" if code is not None else "rejected/closed",
            score=100.0 if ok else 0.0,
        )
    )

    # 5. Unknown / invalid version
    req = b"GET / HTTP/9.9\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    ok = code in (400, 505) or code is None
    suite.checks.append(
        CheckResult(
            id="rfc9110.unknown_http_version",
            team="blue",
            passed=ok,
            detail=f"status={code} (want 400/505 or close)" if code is not None else "closed",
            score=100.0 if ok else 20.0,
        )
    )

    # 6. HTTP/1.1 without Host — SHOULD 400 (RFC 9112 §3.2)
    req = b"GET / HTTP/1.1\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    ok = code is None or code >= 400
    suite.checks.append(
        CheckResult(
            id="rfc9112.missing_host_header",
            team="red",
            passed=ok,
            detail=f"status={code}" if code is not None else "closed (acceptable)",
            score=100.0 if ok else 20.0,
        )
    )

    # 7. HEAD — status line, no requirement for body
    req = b"HEAD / HTTP/1.1\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    suite.checks.append(
        CheckResult(
            id="rfc9110.head_status_line",
            team="blue",
            passed=code is not None,
            detail=f"HEAD → HTTP {code}" if code is not None else (err or "no status"),
            score=100.0 if code is not None else 0.0,
        )
    )

    # 8. OPTIONS * — answer or 4xx/5xx, not hang
    req = b"OPTIONS * HTTP/1.1\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    ok = code is not None or raw == b""
    suite.checks.append(
        CheckResult(
            id="rfc9110.options_asterisk",
            team="blue",
            passed=ok,
            detail=f"status={code}" if code is not None else "closed",
            score=100.0 if code is not None else (70.0 if ok else 0.0),
        )
    )

    # 9. Absolute-form request-target (proxy style) on origin server
    req = (
        b"GET http://bench.invalid/ HTTP/1.1\r\n"
        b"Host: bench.invalid\r\n"
        b"Connection: close\r\n\r\n"
    )
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    # Origin servers may 200, 400, or 501 — must produce an HTTP status or close
    ok = code is not None or raw == b""
    suite.checks.append(
        CheckResult(
            id="rfc9112.absolute_form_request_target",
            team="blue",
            passed=ok,
            detail=f"status={code}" if code is not None else "closed",
            score=100.0 if code is not None else (60.0 if ok else 0.0),
        )
    )

    # 10. Nonsense method — 4xx/5xx or close (not silent 200 on garbage verb)
    req = b"FOOBAR / HTTP/1.1\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    code = _status(raw)
    ok = code is None or code >= 400
    suite.checks.append(
        CheckResult(
            id="rfc9110.unknown_method",
            team="red",
            passed=ok,
            detail=f"status={code}" if code is not None else "closed",
            score=100.0 if ok else 0.0,
        )
    )

    assert len(suite.checks) == 10, f"expected 10 HTTP RFC checks, got {len(suite.checks)}"
    return suite


def probe_http_rfc9110(host: str, port: int) -> RFCSuiteResult:
    return cached_suite(
        ("http_rfc9110", host, int(port)),
        lambda: _probe_http_rfc9110_uncached(host, port),
    )
