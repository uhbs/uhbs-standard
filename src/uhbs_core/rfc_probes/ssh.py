"""SSH (RFC 4253) basic wire-conformance probes for Module A.

These are intentionally *basic* smoke checks (banner, version exchange, early
binary packet hygiene, reject/ tolerate edge cases). They are not a full
RFC 4253 certification suite.
"""
from __future__ import annotations

from uhbs_core.models import CheckOutcome, CheckResult

from .cache import cached_suite
from .socket_util import _port_open, _transact
from .types import RFCSuiteResult

# RFC 4253 §4.2 — identification string maximum length (octets).
_ID_MAX = 255
_CLIENT_ID = b"SSH-2.0-UHBSBench_1.0\r\n"


def _split_banner_line(raw: bytes) -> tuple[bytes, bytes]:
    """Return (first_line_without_eol, remainder_after_first_eol)."""
    if b"\r\n" in raw:
        line, rest = raw.split(b"\r\n", 1)
        return line, rest
    if b"\n" in raw:
        line, rest = raw.split(b"\n", 1)
        return line.rstrip(b"\r"), rest
    return raw, b""


def _find_ssh_banner(raw: bytes) -> tuple[bytes, bytes, bytes]:
    """Locate SSH identification among optional ``#`` comment lines.

    Returns ``(preamble, id_line, after_id)``.
    """
    remaining = raw
    preamble = b""
    while remaining:
        line, rest = _split_banner_line(remaining)
        if not line and not rest:
            break
        if line.startswith(b"#"):
            preamble += line + b"\r\n"
            remaining = rest
            continue
        if line.startswith(b"SSH-"):
            return preamble, line, rest
        # Non-comment junk before banner
        return preamble + line, b"", rest if rest else remaining[len(line) :]
    return preamble, b"", b""


def _kexinit_info(after_id: bytes) -> tuple[bool, int | None, int | None]:
    """Detect SSH_MSG_KEXINIT (20) in early binary; return (found, msg_type, pkt_len)."""
    if len(after_id) < 6:
        # IGNORE/DEBUG may precede KEXINIT — scan a short window for type 20
        if b"\x14" in after_id[:64]:
            return True, 20, None
        return False, None, None
    pkt_len = int.from_bytes(after_id[0:4], "big")
    msg_type = after_id[5]
    if msg_type == 20:
        return True, msg_type, pkt_len
    if b"\x14" in after_id[:64]:
        return True, 20, pkt_len
    return False, msg_type, pkt_len


def _chk(
    cid: str,
    *,
    passed: bool,
    detail: str,
    score: float | None = None,
    team: str = "blue",
    evidence: list[str] | None = None,
) -> CheckResult:
    ok = bool(passed)
    return CheckResult(
        id=cid,
        team=team,
        passed=ok,
        outcome=CheckOutcome.PASS if ok else CheckOutcome.FAIL,
        detail=detail,
        score=100.0 if score is None and ok else (0.0 if score is None else float(score)),
        evidence=evidence or [],
    )


def _probe_ssh_rfc4253_uncached(host: str, port: int) -> RFCSuiteResult:
    """Run ~20 basic RFC 4253 wire checks against an SSH listener."""
    suite = RFCSuiteResult(protocol="ssh", rfc="RFC 4253")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"ssh port {port} closed"
        return suite

    # --- Passive 1: unsolicited server identification ---
    raw, _, err = _transact(host, port, b"", recv_first=True)
    preamble, id_line, after = _find_ssh_banner(raw)
    # Identification line itself terminated with CR LF (§4.2)
    id_crlf = False
    if b"SSH-" in raw:
        idx = raw.find(b"SSH-")
        nl = raw.find(b"\n", idx)
        if (nl > idx and raw[nl - 1 : nl + 1] == b"\r\n") or (
            b"\r\n" in raw[idx : idx + _ID_MAX + 2]
        ):
            id_crlf = True

    ssh20 = id_line.startswith(b"SSH-2.0-")
    soft = id_line.decode("utf-8", "replace") if id_line else (err or "no banner")

    suite.checks.append(
        _chk(
            "rfc4253.identification_ssh20_prefix",
            passed=ssh20,
            detail=soft,
            score=100.0 if ssh20 else 0.0,
            evidence=[raw[:120].hex()],
        )
    )
    suite.checks.append(
        _chk(
            "rfc4253.identification_crlf",
            passed=ssh20 and id_crlf,
            detail=soft if (ssh20 and id_crlf) else (soft + " (missing CR LF)" if ssh20 else soft),
            score=100.0 if (ssh20 and id_crlf) else (40.0 if ssh20 else 0.0),
        )
    )
    suite.checks.append(
        _chk(
            "rfc4253.identification_max_255",
            passed=bool(id_line) and len(id_line) <= _ID_MAX,
            detail=f"id_len={len(id_line)}" if id_line else "no banner",
            score=100.0 if (id_line and len(id_line) <= _ID_MAX) else 0.0,
        )
    )
    null_ok = bool(id_line) and b"\x00" not in id_line
    suite.checks.append(
        _chk(
            "rfc4253.identification_no_null",
            passed=null_ok,
            detail="no NUL in server ID" if null_ok else "NUL in ID or missing",
            team="red",
        )
    )
    printable = bool(id_line) and all(32 <= b < 127 for b in id_line)
    suite.checks.append(
        _chk(
            "rfc4253.identification_printable_ascii",
            passed=printable,
            detail="printable ASCII ID" if printable else "non-printable bytes in ID",
        )
    )
    # SSH-2.0-<softwareversion> [SP comments]
    software_ok = False
    if ssh20 and len(id_line) > len(b"SSH-2.0-"):
        rest = id_line[len(b"SSH-2.0-") :]
        software_ok = bool(rest.split(b" ", 1)[0])
    suite.checks.append(
        _chk(
            "rfc4253.identification_software_token",
            passed=software_ok,
            detail=soft if software_ok else "empty softwareversion after SSH-2.0-",
        )
    )
    # Preamble may only be RFC comment lines ('#') before the identification string
    preamble_ok = (not preamble) or all(
        ln.startswith(b"#") or ln == b"" for ln in preamble.split(b"\r\n") if ln
    )
    suite.checks.append(
        _chk(
            "rfc4253.no_noncomment_preamble",
            passed=bool(id_line) and preamble_ok,
            detail="clean preamble" if preamble_ok and id_line else "junk before identification",
        )
    )

    # --- Passive 2: client ID → KEXINIT ---
    raw2, _, err2 = _transact(host, port, _CLIENT_ID, recv_first=True)
    _p2, _id2, after2 = _find_ssh_banner(raw2)
    if not after2 and b"\r\n" in raw2:
        after2 = raw2.split(b"\r\n", 1)[1]
    kex, msg_type, pkt_len = _kexinit_info(after2)
    suite.checks.append(
        _chk(
            "rfc4253.kexinit_after_id",
            passed=kex,
            detail="KEXINIT observed after version exchange" if kex else (err2 or "no KEXINIT"),
        )
    )
    suite.checks.append(
        _chk(
            "rfc4253.kexinit_msg_type_20",
            passed=kex and (msg_type in (20, None) or msg_type == 20),
            detail=(
                f"msg_type={msg_type}"
                if msg_type is not None
                else ("KEXINIT seen" if kex else "no KEXINIT")
            ),
            score=100.0 if kex else 0.0,
        )
    )
    # Packet length should be plausible for an unencrypted KEXINIT
    length_ok = bool(kex) and (pkt_len is None or 16 <= pkt_len <= 65535)
    if pkt_len is not None:
        length_detail = f"pkt_len={pkt_len}"
    elif kex:
        length_detail = "length n/a (scanned)"
    else:
        length_detail = "no packet"
    suite.checks.append(
        _chk(
            "rfc4253.kexinit_length_field_sane",
            passed=length_ok,
            detail=length_detail,
            score=100.0 if length_ok else (50.0 if kex else 0.0),
        )
    )

    # --- Passive 3: version / grammar edge cases ---
    raw3, _, err3 = _transact(host, port, b"SSH-1.5-Ancient\r\n", recv_first=True)
    alive_legacy = raw3.startswith(b"SSH-") or (err3 == "" and len(raw3) > 0)
    if alive_legacy or err3 == "":
        legacy_detail = "handled SSH-1.5 probe without hang"
    else:
        legacy_detail = err3 or "failed"
    suite.checks.append(
        _chk(
            "rfc4253.legacy_version_handling",
            passed=alive_legacy or err3 == "",
            detail=legacy_detail,
        )
    )

    raw_null, _, err_null = _transact(host, port, b"SSH-2.0-Bad\x00name\r\n", recv_first=True)
    after_null = raw_null.split(b"\r\n", 1)[1] if b"\r\n" in raw_null else b""
    continued_null = _kexinit_info(after_null)[0]
    suite.checks.append(
        _chk(
            "rfc4253.reject_null_in_id",
            passed=not continued_null,
            detail=(
                "null in client ID did not proceed to KEX"
                if not continued_null
                else "accepted null ID"
            ),
            team="red",
            evidence=[err_null or raw_null[:40].hex()],
        )
    )

    huge = b"SSH-2.0-" + (b"A" * 400) + b"\r\n"
    raw_huge, _, err_huge = _transact(host, port, huge, recv_first=True)
    after_huge = raw_huge.split(b"\r\n", 1)[1] if b"\r\n" in raw_huge else b""
    continued_huge = _kexinit_info(after_huge)[0]
    suite.checks.append(
        _chk(
            "rfc4253.reject_oversized_client_id",
            passed=not continued_huge,
            detail=(
                "oversized client ID did not reach KEX"
                if not continued_huge
                else "accepted oversized ID"
            ),
            team="red",
            evidence=[err_huge or f"after_len={len(after_huge)}"],
        )
    )

    raw_empty, _, err_empty = _transact(host, port, b"\r\n", recv_first=True)
    after_empty = raw_empty.split(b"\r\n", 1)[1] if b"\r\n" in raw_empty else b""
    # Empty/minimal client line should not cleanly complete version exchange to KEXINIT
    continued_empty = _kexinit_info(after_empty)[0]
    suite.checks.append(
        _chk(
            "rfc4253.reject_empty_client_id",
            passed=not continued_empty,
            detail=(
                "empty client ID did not reach KEX"
                if not continued_empty
                else "KEXINIT after empty client ID"
            ),
            team="red",
            evidence=[err_empty or raw_empty[:40].hex()],
        )
    )

    raw_http, _, err_http = _transact(
        host, port, b"GET / HTTP/1.1\r\nHost: x\r\n\r\n", recv_first=True
    )
    httpish = b"HTTP/" in raw_http[:200]
    kex_http = _kexinit_info(
        raw_http.split(b"\r\n", 1)[1] if b"\r\n" in raw_http else raw_http
    )[0]
    # Pass if we don't get a clean HTTP response pretending to be a web server
    # after SSH banner — decoy should stay in SSH world or drop.
    suite.checks.append(
        _chk(
            "rfc4253.reject_http_probe_as_ssh",
            passed=(not httpish) and (not kex_http),
            detail=(
                "HTTP probe did not yield HTTP response or SSH KEX"
                if (not httpish and not kex_http)
                else ("spoke HTTP" if httpish else "KEXINIT after HTTP probe")
            ),
            team="red",
            evidence=[err_http or raw_http[:60].hex()],
        )
    )

    raw_bin, _, err_bin = _transact(host, port, b"\x00\xff\xfeSSH-2.0-X\r\n", recv_first=True)
    after_bin = raw_bin.split(b"\r\n", 1)[1] if b"\r\n" in raw_bin else b""
    continued_bin = _kexinit_info(after_bin)[0]
    suite.checks.append(
        _chk(
            "rfc4253.reject_binary_prologue",
            passed=not continued_bin,
            detail=(
                "binary prologue did not reach KEX"
                if not continued_bin
                else "accepted binary prologue before ID"
            ),
            team="red",
            evidence=[err_bin or raw_bin[:40].hex()],
        )
    )

    raw21, _, err21 = _transact(host, port, b"SSH-2.1-Experimental\r\n", recv_first=True)
    alive21 = raw21.startswith(b"SSH-") or err21 == ""
    suite.checks.append(
        _chk(
            "rfc4253.ssh21_version_handling",
            passed=alive21,
            detail="handled SSH-2.1 probe without hang" if alive21 else (err21 or "failed"),
        )
    )

    # LF-only client ID: RFC requires CR LF; many servers still accept. Must not hang.
    raw_lf, _, err_lf = _transact(host, port, b"SSH-2.0-UHBSBench_LF\n", recv_first=True)
    alive_lf = raw_lf.startswith(b"SSH-") or err_lf == ""
    suite.checks.append(
        _chk(
            "rfc4253.lf_only_client_id_no_hang",
            passed=alive_lf,
            detail="LF-only client ID handled" if alive_lf else (err_lf or "hang/fail"),
            score=100.0 if alive_lf else 0.0,
        )
    )

    # --- Phase 4: connection hygiene ---
    raw_a, _, err_a = _transact(host, port, b"", recv_first=True)
    raw_b, _, err_b = _transact(host, port, b"", recv_first=True)
    two_ok = (
        raw_a.startswith(b"SSH-")
        and raw_b.startswith(b"SSH-")
        and not err_a
        and not err_b
    )
    suite.checks.append(
        _chk(
            "rfc4253.second_connection_independent",
            passed=two_ok,
            detail="two sequential connections both received SSH banners"
            if two_ok
            else f"conn_a={err_a or raw_a[:20]!r} conn_b={err_b or raw_b[:20]!r}",
        )
    )

    # After a hostile null-ID probe, a fresh connection should still banner
    _transact(host, port, b"SSH-2.0-X\x00Y\r\n", recv_first=True)
    raw_rec, _, err_rec = _transact(host, port, b"", recv_first=True)
    recover_ok = raw_rec.startswith(b"SSH-") and not err_rec
    suite.checks.append(
        _chk(
            "rfc4253.reconnect_after_bad_id",
            passed=recover_ok,
            detail="fresh connection ok after bad ID" if recover_ok else (err_rec or "no banner"),
        )
    )

    assert len(suite.checks) == 20, f"expected 20 SSH RFC checks, got {len(suite.checks)}"
    return suite


def probe_ssh_rfc4253(host: str, port: int) -> RFCSuiteResult:
    return cached_suite(
        ("ssh_rfc4253", host, int(port)),
        lambda: _probe_ssh_rfc4253_uncached(host, port),
    )
