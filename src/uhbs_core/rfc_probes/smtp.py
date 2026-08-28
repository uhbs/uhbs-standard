"""SMTP (RFC 5321) dialogue probe."""
from __future__ import annotations

import re

from uhbs_core.models import CheckResult

from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

_SMTP_CODE = re.compile(rb"(?m)^(\d{3})[\s-]")


def _smtp_codes(data: bytes) -> list[int]:
    return [int(m.group(1)) for m in _SMTP_CODE.finditer(data)]


def probe_smtp_rfc5321(host: str, port: int) -> RFCSuiteResult:
    suite = RFCSuiteResult(protocol="smtp", rfc="RFC 5321")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"smtp port {port} closed"
        return suite

    # Greeting 220
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

    # State machine: DATA before MAIL FROM → 503 (§3.3 / §4.3.2)
    script = b"DATA\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    # Look for 503 among responses after greeting
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

    # RCPT before MAIL → 503
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

    # EHLO capability negotiation (§3.2 / §4.1.1.1)
    script = b"EHLO bench.invalid\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    text = raw.decode("utf-8", "replace")
    ehlo_ok = "250" in text and (
        "EHLO" in text.upper()
        or "PIPELINING" in text.upper()
        or "SIZE" in text.upper()
        or "\n250-" in text
        or "\n250 " in text
    )
    # Accept multiline 250- capabilities
    ehlo_ok = ehlo_ok or bool(re.search(r"(?m)^250[\s-]", text))
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

    # Grammar: bare LF (non-conforming client). Server should still answer safely.
    script = b"NOOP\nQUIT\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    codes = _smtp_codes(raw)
    safe = bool(codes) and not any(
        c >= 500 and c not in (500, 501, 502, 503, 504) for c in codes if c != 221
    )
    # Pass if we got any SMTP-shaped reply and no crash
    suite.checks.append(
        CheckResult(
            id="rfc5321.bare_lf_tolerance",
            team="red",
            passed=bool(codes),
            detail=f"codes={codes}" if codes else (err or "no response to bare LF"),
            score=100.0 if codes else 0.0,
        )
    )

    # Unknown command → 500/502 (§4.2.4)
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
    _ = safe
    return suite

