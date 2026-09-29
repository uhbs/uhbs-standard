"""FTP (RFC 959) control-channel probe — 10 Module A checks.

Stable IDs keep ``ftp.fsm.retr_before_auth`` / ``ftp.nego.banner_220`` for
longitudinal compare; ``catalog_id`` retains the RFC 959 label.
"""
from __future__ import annotations

import re

from uhbs_core.models import CheckResult

from .cache import cached_suite
from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

_FTP_CODE = re.compile(rb"(?m)^(\d{3})[\s-]")


def _ftp_codes(data: bytes) -> list[int]:
    return [int(m.group(1)) for m in _FTP_CODE.finditer(data)]


def _probe_ftp_rfc959_uncached(host: str, port: int) -> RFCSuiteResult:
    """Ten RFC 959 control-channel checks for Module A."""
    suite = RFCSuiteResult(protocol="ftp", rfc="RFC 959")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"ftp port {port} closed"
        return suite

    # 1. Banner 220 (legacy id)
    greet, _, err = _transact(host, port, b"", recv_first=True)
    codes = _ftp_codes(greet)
    banner_ok = bool(codes) and codes[0] == 220
    suite.checks.append(
        CheckResult(
            id="ftp.nego.banner_220",
            team="blue",
            passed=banner_ok,
            detail=(greet[:120].decode("utf-8", "replace") if greet else err or "no banner"),
            score=100.0 if banner_ok else 0.0,
            catalog_id="rfc959.banner_220",
        )
    )

    # 2. RETR before auth → 530/503/550 (legacy id)
    raw, _, err = _transact(host, port, b"RETR secret\r\nQUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    retr_rej = any(c in (530, 503, 550) for c in codes)
    suite.checks.append(
        CheckResult(
            id="ftp.fsm.retr_before_auth",
            team="blue",
            critical=True,
            passed=retr_rej,
            detail=f"codes={codes}",
            score=100.0 if retr_rej else 0.0,
            catalog_id="rfc959.retr_before_auth",
        )
    )

    # 3. STOR before auth
    raw, _, err = _transact(host, port, b"STOR evil.bin\r\nQUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    stor_rej = any(c in (530, 503, 550) for c in codes)
    suite.checks.append(
        CheckResult(
            id="ftp.fsm.stor_before_auth",
            team="blue",
            passed=stor_rej,
            detail=f"codes={codes}",
            score=100.0 if stor_rej else 0.0,
            catalog_id="rfc959.stor_before_auth",
        )
    )

    # 4. Unknown verb → 500/502
    raw, _, err = _transact(host, port, b"FOOBAR\r\nQUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    unknown_ok = any(c in (500, 502) for c in codes)
    suite.checks.append(
        CheckResult(
            id="ftp.fsm.unknown_command",
            team="blue",
            passed=unknown_ok,
            detail=f"codes={codes}",
            score=100.0 if unknown_ok else 0.0,
            catalog_id="rfc959.unknown_command",
        )
    )

    # 5. Bare LF NOOP
    raw, _, err = _transact(host, port, b"NOOP\nQUIT\n", recv_first=True)
    codes = _ftp_codes(raw)
    suite.checks.append(
        CheckResult(
            id="ftp.fsm.bare_lf_tolerance",
            team="red",
            passed=bool(codes),
            detail=f"codes={codes}" if codes else (err or "no reply"),
            score=100.0 if codes else 0.0,
            catalog_id="rfc959.bare_lf_tolerance",
        )
    )

    # 6. SYST — 215 or 530
    raw, _, err = _transact(host, port, b"SYST\r\nQUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    syst_ok = any(c in (215, 530, 502) for c in codes)
    suite.checks.append(
        CheckResult(
            id="ftp.nego.syst_reply",
            team="blue",
            passed=syst_ok,
            detail=f"codes={codes}",
            score=100.0 if syst_ok else 40.0,
            catalog_id="rfc959.syst_reply",
        )
    )

    # 7. TYPE I — 200/530/504
    raw, _, err = _transact(host, port, b"TYPE I\r\nQUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    type_ok = any(c in (200, 530, 504, 501) for c in codes)
    suite.checks.append(
        CheckResult(
            id="ftp.nego.type_i_reply",
            team="blue",
            passed=type_ok,
            detail=f"codes={codes}",
            score=100.0 if type_ok else 40.0,
            catalog_id="rfc959.type_i_reply",
        )
    )

    # 8. PASV / EPSV shaped reply or auth reject
    raw, _, err = _transact(host, port, b"PASV\r\nQUIT\r\n", recv_first=True)
    text = raw.decode("utf-8", "replace")
    codes = _ftp_codes(raw)
    pasv_ok = (
        any(c in (227, 229, 530, 502, 425) for c in codes)
        or "Entering Passive" in text
        or "EPSV" in text.upper()
    )
    suite.checks.append(
        CheckResult(
            id="ftp.nego.pasv_reply",
            team="blue",
            passed=pasv_ok,
            detail=f"codes={codes}",
            score=100.0 if pasv_ok else 30.0,
            catalog_id="rfc959.pasv_reply",
        )
    )

    # 9. USER — 331/230/530
    raw, _, err = _transact(host, port, b"USER anonymous\r\nQUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    user_ok = any(c in (331, 230, 530, 332) for c in codes)
    suite.checks.append(
        CheckResult(
            id="ftp.nego.user_reply",
            team="blue",
            passed=user_ok,
            detail=f"codes={codes}",
            score=100.0 if user_ok else 0.0,
            catalog_id="rfc959.user_reply",
        )
    )

    # 10. QUIT — 221
    raw, _, err = _transact(host, port, b"QUIT\r\n", recv_first=True)
    codes = _ftp_codes(raw)
    quit_ok = 221 in codes or raw == b""
    suite.checks.append(
        CheckResult(
            id="ftp.nego.quit_221",
            team="blue",
            passed=quit_ok,
            detail=f"codes={codes}",
            score=100.0 if 221 in codes else (70.0 if quit_ok else 0.0),
            catalog_id="rfc959.quit_221",
        )
    )

    assert len(suite.checks) == 10, f"expected 10 FTP RFC checks, got {len(suite.checks)}"
    return suite


def probe_ftp_rfc959(host: str, port: int) -> RFCSuiteResult:
    return cached_suite(
        ("ftp_rfc959", host, int(port)),
        lambda: _probe_ftp_rfc959_uncached(host, port),
    )
