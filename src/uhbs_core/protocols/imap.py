from __future__ import annotations

import re

from uhbs_core.protocols.base import ProtocolPlugin

from ..models import CheckResult, TargetSpec
from ..rfc_probes import RFCSuiteResult, _port_open, _transact
from ..rfc_probes.cache import cached_suite
from ..tps import TPS

_IMAP_TAGGED = re.compile(rb"(?m)^(\S+) (OK|NO|BAD)\b")
_IMAP_UNTAGGED_OK = re.compile(rb"(?m)^\* OK\b")


def _imap_tagged_codes(data: bytes) -> list[str]:
    return [m.group(2).decode("ascii") for m in _IMAP_TAGGED.finditer(data)]


def _imap_greeting_ok(data: bytes) -> bool:
    return bool(_IMAP_UNTAGGED_OK.search(data))


def _probe_imap_rfc3501_uncached(host: str, port: int) -> RFCSuiteResult:
    """Ten RFC 3501 / 9051 IMAP4 wire checks for Module A."""
    suite = RFCSuiteResult(protocol="imap", rfc="RFC 3501 / RFC 9051")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"imap port {port} closed"
        return suite

    # 1. Greeting
    greet, _, err = _transact(host, port, b"", recv_first=True)
    greet_ok = _imap_greeting_ok(greet)
    suite.checks.append(
        CheckResult(
            id="rfc3501.greeting_ok",
            team="blue",
            passed=greet_ok,
            detail=(greet[:160].decode("utf-8", "replace") if greet else err or "no greeting"),
            score=100.0 if greet_ok else 0.0,
        )
    )

    # 2. CAPABILITY
    script = b"A001 CAPABILITY\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    text = raw.decode("utf-8", "replace")
    tagged = _imap_tagged_codes(raw)
    capa_ok = _imap_greeting_ok(raw) and bool(
        re.search(r"(?mi)^\* CAPABILITY\b", text) or re.search(r"IMAP4", text, re.I)
    )
    capa_tag_ok = "OK" in tagged
    capa_pass = capa_ok and capa_tag_ok
    suite.checks.append(
        CheckResult(
            id="rfc3501.capability",
            team="blue",
            passed=capa_pass,
            detail=(
                "untagged CAPABILITY + tagged OK"
                if capa_pass
                else f"capa_ok={capa_ok} tagged={tagged}"
            ),
            score=100.0 if capa_pass else (40.0 if capa_ok or capa_tag_ok else 0.0),
            evidence=[text[:400]],
        )
    )

    # 3. SELECT before auth
    script = b"A001 SELECT INBOX\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    tagged = _imap_tagged_codes(raw)
    preauth_select = "NO" in tagged or "BAD" in tagged
    closed = raw == b"" and bool(err)
    score = 100.0 if preauth_select else (60.0 if closed else 0.0)
    suite.checks.append(
        CheckResult(
            id="rfc3501.preauth_select",
            team="blue",
            passed=score >= 70.0,
            detail=(
                "SELECT rejected before auth (NO/BAD or close)"
                if (preauth_select or closed)
                else f"tagged={tagged}"
            ),
            score=score,
            evidence=[raw[:300].decode("utf-8", "replace")],
        )
    )

    # 4. FETCH before auth
    script = b"A001 FETCH 1 (FLAGS)\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    tagged = _imap_tagged_codes(raw)
    preauth_fetch = "NO" in tagged or "BAD" in tagged
    closed = raw == b"" and bool(err)
    score = 100.0 if preauth_fetch else (60.0 if closed else 0.0)
    suite.checks.append(
        CheckResult(
            id="rfc3501.preauth_fetch",
            team="blue",
            passed=score >= 70.0,
            detail=(
                "FETCH rejected before SELECT/auth (NO/BAD or close)"
                if (preauth_fetch or closed)
                else f"tagged={tagged}"
            ),
            score=score,
        )
    )

    # 5. Unknown command
    script = b"A001 FOOBAR\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    tagged = _imap_tagged_codes(raw)
    unknown_ok = "BAD" in tagged or "NO" in tagged
    closed = raw == b"" and bool(err)
    score = 100.0 if unknown_ok else (60.0 if closed else 20.0)
    suite.checks.append(
        CheckResult(
            id="rfc3501.unknown_command",
            team="blue",
            passed=score >= 70.0,
            detail=(
                "unknown verb → BAD/NO or close"
                if (unknown_ok or closed)
                else f"tagged={tagged}"
            ),
            score=score,
        )
    )

    # 6. CREATE before auth
    script = b"A001 CREATE UhbsBox\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    tagged = _imap_tagged_codes(raw)
    create_rej = "NO" in tagged or "BAD" in tagged
    closed = raw == b"" and bool(err)
    score = 100.0 if create_rej else (60.0 if closed else 0.0)
    suite.checks.append(
        CheckResult(
            id="rfc3501.preauth_create",
            team="blue",
            passed=score >= 70.0,
            detail=f"tagged={tagged}" if not (create_rej or closed) else "CREATE gated before auth",
            score=score,
        )
    )

    # 7. STORE before auth
    script = b"A001 STORE 1 +FLAGS (\\Seen)\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    tagged = _imap_tagged_codes(raw)
    store_rej = "NO" in tagged or "BAD" in tagged
    closed = raw == b"" and bool(err)
    score = 100.0 if store_rej else (60.0 if closed else 0.0)
    suite.checks.append(
        CheckResult(
            id="rfc3501.preauth_store",
            team="blue",
            passed=score >= 70.0,
            detail=f"tagged={tagged}" if not (store_rej or closed) else "STORE gated before auth",
            score=score,
        )
    )

    # 8. Bare LF tagged command
    script = b"A001 NOOP\nA002 LOGOUT\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    tagged = _imap_tagged_codes(raw)
    bare_ok = bool(tagged) or (raw == b"" and bool(err))
    suite.checks.append(
        CheckResult(
            id="rfc3501.bare_lf_tolerance",
            team="red",
            passed=bare_ok,
            detail=f"tagged={tagged}" if tagged else (err or "no tagged reply to bare LF"),
            score=100.0 if tagged else (60.0 if bare_ok else 0.0),
        )
    )

    # 9. NOOP tagged OK
    script = b"A001 NOOP\r\nA002 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    text = raw.decode("utf-8", "replace")
    noop_ok = bool(re.search(r"(?m)^A001 OK\b", text))
    suite.checks.append(
        CheckResult(
            id="rfc3501.noop_ok",
            team="blue",
            passed=noop_ok,
            detail="A001 OK NOOP" if noop_ok else text[:120],
            score=100.0 if noop_ok else 30.0,
        )
    )

    # 10. LOGOUT — tagged OK and/or untagged BYE
    script = b"A001 LOGOUT\r\n"
    raw, _, err = _transact(host, port, script, recv_first=True)
    text = raw.decode("utf-8", "replace")
    logout_ok = bool(re.search(r"(?mi)^\* BYE\b", text)) or bool(
        re.search(r"(?m)^A001 OK\b", text)
    )
    suite.checks.append(
        CheckResult(
            id="rfc3501.logout_bye",
            team="blue",
            passed=logout_ok,
            detail="LOGOUT → BYE/OK" if logout_ok else text[:120],
            score=100.0 if logout_ok else 40.0,
        )
    )

    assert len(suite.checks) == 10, f"expected 10 IMAP RFC checks, got {len(suite.checks)}"
    return suite


def probe_imap_rfc3501(host: str, port: int) -> RFCSuiteResult:
    return cached_suite(
        ("imap_rfc3501", host, int(port)),
        lambda: _probe_imap_rfc3501_uncached(host, port),
    )


class IMAPPlugin(ProtocolPlugin):
    """RFC 3501 / 9051 IMAP4 — tagged commands, untagged OK greeting, CAPABILITY."""

    name = "imap"
    families = ("it", "mail")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_imap_rfc3501(host, port)
        if suite.skipped:
            return [
                CheckResult(
                    id="imap.fsm.skipped",
                    team="blue",
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        return [
            c
            for c in suite.checks
            if any(
                key in c.id
                for key in ("preauth", "unknown", "bare_lf", "store", "create")
            )
        ]

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_imap_rfc3501(host, port)
        if suite.skipped:
            return [
                CheckResult(
                    id="imap.nego.skipped",
                    team="blue",
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        return [
            c
            for c in suite.checks
            if any(key in c.id for key in ("greeting", "capability", "noop", "logout"))
        ]

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        user = (target.user or "uhbs").replace("\\", "\\\\").replace('"', '\\"')
        password = (target.password or "uhbs").replace("\\", "\\\\").replace('"', '\\"')
        # LOGIN — document auth gate: invalid creds must not yield tagged OK LOGIN.
        script = (
            f'A001 LOGIN "{user}" "{password}"\r\n'
            f"A002 CAPABILITY\r\n"
            f"A003 LOGOUT\r\n"
        ).encode("ascii", "replace")
        raw, _, err = _transact(host, port, script, recv_first=True)
        text = raw.decode("utf-8", "replace")
        login_m = re.search(r"(?m)^A001 (OK|NO|BAD)\b", text)
        if login_m:
            code = login_m.group(1)
            score = 100.0
            if code == "OK":
                detail = "LOGIN tagged OK (auth transition)"
            else:
                detail = f"LOGIN auth gate: tagged {code}"
            passed = True
        elif raw == b"" and err:
            score = 70.0
            passed = True
            detail = "connection closed on LOGIN (auth gate)"
        else:
            score = 30.0
            passed = False
            detail = text[:120] if text else (err or "no tagged LOGIN response")
        return [
            CheckResult(
                id="imap.state.login_gate",
                team="blue",
                passed=passed and score >= 70.0,
                detail=detail,
                score=score,
                evidence=[text[:400]] if text else [],
            )
        ]
