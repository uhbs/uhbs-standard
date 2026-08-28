"""POP3 (RFC 1939) dialogue probe."""
from __future__ import annotations

import re

from uhbs_core.models import CheckResult

from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

_POP3_STATUS = re.compile(rb"(?m)^(\+OK|-ERR)\b")


def _pop3_status(data: bytes) -> list[str]:
    return [m.group(1).decode("ascii") for m in _POP3_STATUS.finditer(data)]


def probe_pop3_rfc1939(host: str, port: int) -> RFCSuiteResult:
    """RFC 1939 POP3 basic conformance for Module A.

    Checks: greeting ``+OK``, pre-auth transaction verbs rejected, unknown
    command ``-ERR``, optional ``CAPA``, bare-LF tolerance.
    """
    suite = RFCSuiteResult(protocol="pop3", rfc="RFC 1939")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"pop3 port {port} closed"
        return suite

    # Greeting must be +OK (§3 / AUTHORIZATION state)
    greet, _, err = _transact(host, port, b"", recv_first=True)
    statuses = _pop3_status(greet)
    greet_ok = bool(statuses) and statuses[0] == "+OK"
    suite.checks.append(
        CheckResult(
            id="rfc1939.greeting_ok",
            team="blue",
            passed=greet_ok,
            detail=(greet[:120].decode("utf-8", "replace") if greet else err or "no greeting"),
            score=100.0 if greet_ok else 0.0,
        )
    )

    # Transaction verbs before auth must fail (§4 — STAT only in TRANSACTION)
    script = b"STAT\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    statuses = _pop3_status(raw)
    # After greeting +OK, STAT should be -ERR while still AUTHORIZATION
    preauth_rejected = "-ERR" in statuses
    suite.checks.append(
        CheckResult(
            id="rfc1939.preauth_stat",
            team="blue",
            passed=preauth_rejected,
            detail="-ERR on STAT before auth" if preauth_rejected else f"statuses={statuses}",
            score=100.0 if preauth_rejected else 0.0,
            evidence=[raw[:300].decode("utf-8", "replace")],
        )
    )

    script = b"LIST\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    statuses = _pop3_status(raw)
    preauth_list = "-ERR" in statuses
    suite.checks.append(
        CheckResult(
            id="rfc1939.preauth_list",
            team="blue",
            passed=preauth_list,
            detail="-ERR on LIST before auth" if preauth_list else f"statuses={statuses}",
            score=100.0 if preauth_list else 0.0,
        )
    )

    # CAPA (RFC 2449) — optional but common; partial credit if missing
    script = b"CAPA\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    text = raw.decode("utf-8", "replace")
    capa_ok = bool(re.search(r"(?mi)^\+OK", text)) and (
        "capa" in text.lower() or "UIDL" in text.upper() or "TOP" in text.upper()
        or ".\r\n" in text or ".\n" in text
    )
    # Accept +OK multiline capa list OR explicit -ERR (honest non-support)
    statuses = _pop3_status(raw)
    capa_honest = capa_ok or "-ERR" in statuses
    suite.checks.append(
        CheckResult(
            id="rfc1939.capa",
            team="blue",
            passed=capa_honest,
            detail=(
                "CAPA answered (+OK list or -ERR)"
                if capa_honest
                else "CAPA negotiation weak/missing"
            ),
            score=100.0 if capa_ok else (70.0 if capa_honest else 20.0),
            evidence=[text[:300]],
        )
    )

    # Bare LF tolerance
    script = b"NOOP\nQUIT\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    statuses = _pop3_status(raw)
    suite.checks.append(
        CheckResult(
            id="rfc1939.bare_lf_tolerance",
            team="red",
            passed=bool(statuses),
            detail=f"statuses={statuses}" if statuses else (err or "no response to bare LF"),
            score=100.0 if statuses else 0.0,
        )
    )

    # Unknown command → -ERR
    script = b"FOOBAR baz\r\nQUIT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    statuses = _pop3_status(raw)
    unknown_ok = "-ERR" in statuses
    suite.checks.append(
        CheckResult(
            id="rfc1939.unknown_command",
            team="blue",
            passed=unknown_ok,
            detail="-ERR on unknown verb" if unknown_ok else f"statuses={statuses}",
            score=100.0 if unknown_ok else 0.0,
        )
    )
    return suite

