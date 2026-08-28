"""HTTP/1.1 (RFC 9110 / 9112) request/response probe."""
from __future__ import annotations

import re

from uhbs_core.models import CheckResult

from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

_HTTP_STATUS = re.compile(rb"^HTTP/1\.[01] (\d{3})", re.MULTILINE)


def probe_http_rfc9110(host: str, port: int) -> RFCSuiteResult:
    suite = RFCSuiteResult(protocol="http", rfc="RFC 9110/9112")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"http port {port} closed"
        return suite

    # Valid GET — expect HTTP/1.x status
    req = b"GET / HTTP/1.1\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    m = _HTTP_STATUS.search(raw)
    suite.checks.append(
        CheckResult(
            id="rfc9110.valid_get_status",
            team="blue",
            passed=m is not None,
            detail=(m.group(0).decode() if m else (err or raw[:80].decode("utf-8", "replace"))),
            score=100.0 if m else 0.0,
        )
    )

    # Payload / body bytes before request line (out-of-order) — expect 400 or close, not 200
    junk = b"{'oops':true}\r\nGET / HTTP/1.1\r\nHost: x\r\n\r\n"
    raw, _, err = _transact(host, port, junk, recv_first=False)
    m = _HTTP_STATUS.search(raw)
    code = int(m.group(1)) if m else None
    # RFC-friendly: 400/405/501 or connection close without 2xx
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

    # Bare LF framing (RFC 9112 prefers CRLF)
    req = b"GET / HTTP/1.1\nHost: bench.invalid\nConnection: close\n\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    m = _HTTP_STATUS.search(raw)
    # Either parse and answer, or reject — must not hang/crash
    suite.checks.append(
        CheckResult(
            id="rfc9112.bare_lf_framing",
            team="blue",
            passed=m is not None or err == "",
            detail=(m.group(0).decode() if m else "accepted/closed without HTTP status"),
            score=100.0 if (m is not None or raw == b"") else 20.0,
        )
    )

    # Invalid header formatting (space before colon — obsolete line folding / invalid)
    req = (
        b"GET / HTTP/1.1\r\n"
        b"Host : bench.invalid\r\n"
        b"X-Bad\x00Header: 1\r\n"
        b"Connection: close\r\n\r\n"
    )
    raw, _, err = _transact(host, port, req, recv_first=False)
    m = _HTTP_STATUS.search(raw)
    code = int(m.group(1)) if m else None
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

    # Unknown / invalid version
    req = b"GET / HTTP/9.9\r\nHost: bench.invalid\r\nConnection: close\r\n\r\n"
    raw, _, err = _transact(host, port, req, recv_first=False)
    m = _HTTP_STATUS.search(raw)
    code = int(m.group(1)) if m else None
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
    return suite

