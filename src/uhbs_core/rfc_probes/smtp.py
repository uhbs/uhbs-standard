"""SMTP (RFC 5321) dialogue probe — 10 Module A checks."""
from __future__ import annotations

import re

from uhbs_core.models import CheckResult

from .cache import cached_suite
from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

_SMTP_CODE = re.compile(rb"(?m)^(\d{3})[\s-]")


def _smtp_codes(data: bytes) -> list[int]:
    return [int(m.group(1)) for m in _SMTP_CODE.finditer(data)]


def _probe_smtp_rfc5321_uncached(host: str, port: int) -> RFCSuiteResult:
    """Ten RFC 5321 wire checks for Module A."""
    suite = RFCSuiteResult(protocol="smtp", rfc="RFC 5321")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"smtp port {port} closed"
        return suite

    # 1. Greeting 220
    greet, _, err = _transact(host, port, b"", recv_first=True)
    codes = _smtp_codes(greet)
    suite.checks.append(
        CheckResult(
            id="rfc5321.greeting_220",
            team="blue",
            passed=bool(codes) and codes[0] == 220,
            detail=(greet[:120].decode("utf-8", "replace") if greet else err or "no greeting"),
            score=100.0 if (codes and codes[0] == 220) else 0.0,
        )
    )

    # 2. DATA before MAIL FROM → 503
    script = b"DATA\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    has_503 = 503 in codes
    suite.checks.append(
        CheckResult(
            id="rfc5321.bad_sequence_data",
            team="blue",
            passed=has_503,
            detail="503 on DATA before MAIL" if has_503 else f"codes={codes} (want 503)",
            score=100.0 if has_503 else 0.0,
            evidence=[raw[:300].decode("utf-8", "replace")],
        )
    )

    # 3. RCPT before MAIL → 503
    script = b"RCPT TO:<a@b.c>\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    has_503 = 503 in codes
    suite.checks.append(
        CheckResult(
            id="rfc5321.bad_sequence_rcpt",
            team="blue",
            passed=has_503,
            detail="503 on RCPT before MAIL" if has_503 else f"codes={codes} (want 503)",
            score=100.0 if has_503 else 0.0,
        )
    )

    # 4. EHLO capabilities
    script = b"EHLO bench.invalid\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    text = raw.decode("utf-8", "replace")
    ehlo_ok = bool(re.search(r"(?m)^250[\s-]", text))
    suite.checks.append(
        CheckResult(
            id="rfc5321.ehlo_capabilities",
            team="blue",
            passed=ehlo_ok,
            detail="EHLO returned 250 capabilities" if ehlo_ok else "EHLO negotiation weak/missing",
            score=100.0 if ehlo_ok else 0.0,
            evidence=[text[:300]],
        )
    )

    # 5. Bare LF tolerance
    script = b"NOOP\nQUIT\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    suite.checks.append(
        CheckResult(
            id="rfc5321.bare_lf_tolerance",
            team="red",
            passed=bool(codes),
            detail=f"codes={codes}" if codes else (err or "no response to bare LF"),
            score=100.0 if codes else 0.0,
        )
    )

    # 6. Unknown command → 500/502
    script = b"FOOBAR baz\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    unknown_ok = any(c in (500, 502) for c in codes)
    suite.checks.append(
        CheckResult(
            id="rfc5321.unknown_command",
            team="blue",
            passed=unknown_ok,
            detail="500/502 on unknown verb" if unknown_ok else f"codes={codes}",
            score=100.0 if unknown_ok else 0.0,
        )
    )

    # 7. HELO (§4.1.1.1) — 250
    script = b"HELO bench.invalid\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    helo_ok = 250 in codes
    suite.checks.append(
        CheckResult(
            id="rfc5321.helo_250",
            team="blue",
            passed=helo_ok,
            detail="HELO → 250" if helo_ok else f"codes={codes}",
            score=100.0 if helo_ok else 0.0,
        )
    )

    # 8. RSET after HELO — 250 (§4.1.1.5)
    script = b"HELO bench.invalid\r\nRSET\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    rset_ok = codes.count(250) >= 2 or (250 in codes and 221 in codes)
    suite.checks.append(
        CheckResult(
            id="rfc5321.rset_250",
            team="blue",
            passed=rset_ok,
            detail=f"codes={codes}",
            score=100.0 if rset_ok else 40.0,
        )
    )

    # 9. MAIL FROM syntax — accept 250/550/553 shaped reply (not crash)
    script = b"HELO bench.invalid\r\nMAIL FROM:<uhbs@bench.invalid>\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    mail_ok = any(c in (250, 251, 550, 553, 555, 501) for c in codes)
    suite.checks.append(
        CheckResult(
            id="rfc5321.mail_from_reply",
            team="blue",
            passed=mail_ok,
            detail=f"codes={codes}",
            score=100.0 if mail_ok else 0.0,
        )
    )

    # 10. NOOP — 250 (§4.1.1.9)
    script = b"NOOP\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    noop_ok = 250 in codes
    suite.checks.append(
        CheckResult(
            id="rfc5321.noop_250",
            team="blue",
            passed=noop_ok,
            detail="NOOP → 250" if noop_ok else f"codes={codes}",
            score=100.0 if noop_ok else 0.0,
        )
    )

    assert len(suite.checks) == 10, f"expected 10 SMTP RFC checks, got {len(suite.checks)}"
    return suite


def probe_smtp_rfc5321(host: str, port: int) -> RFCSuiteResult:
    return cached_suite(
        ("smtp_rfc5321", host, int(port)),
        lambda: _probe_smtp_rfc5321_uncached(host, port),
    )
