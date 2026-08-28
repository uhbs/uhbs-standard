"""SSH (RFC 4253) identification-string probe."""
from __future__ import annotations

from uhbs_core.models import CheckResult

from .socket_util import _port_open, _transact
from .types import RFCSuiteResult


def probe_ssh_rfc4253(host: str, port: int) -> RFCSuiteResult:
    suite = RFCSuiteResult(protocol="ssh", rfc="RFC 4253")
    if not _port_open(host, port):
        suite.skipped = True
        suite.skip_reason = f"ssh port {port} closed"
        return suite

    # 1) Identification string MUST be SSH-2.0-... terminated by CR LF (§4.2)
    raw, _, err = _transact(host, port, b"", recv_first=True)
    crlf = False
    first_line = b""
    if raw.startswith(b"SSH-"):
        if b"\r\n" in raw:
            first_line = raw.split(b"\r\n", 1)[0]
            crlf = True
        else:
            first_line = raw.split(b"\n", 1)[0].rstrip(b"\r")
    ssh20 = first_line.startswith(b"SSH-2.0-")
    suite.checks.append(
        CheckResult(
            id="rfc4253.identification_crlf",
            team="blue",
            passed=ssh20 and crlf,
            detail=(
                first_line.decode("utf-8", "replace")
                if first_line
                else (err or "no banner")
            ),
            # Each check is 0–100 so geometric-mean aggregation stays meaningful.
            score=100.0 if (ssh20 and crlf) else (40.0 if ssh20 else 0.0),
            evidence=[raw[:120].hex()],
        )
    )

    # 2) Capability negotiation: after client ID, server should emit KEXINIT (SSH_MSG_KEXINIT=20)
    client_id = b"SSH-2.0-UHBSBench_1.0\r\n"
    raw2, _, err2 = _transact(host, port, client_id, recv_first=True)
    # Binary packet follows identification; look for msg type 20 in early binary
    after_id = raw2
    if b"\r\n" in raw2:
        after_id = raw2.split(b"\r\n", 1)[1]
    # SSH binary packet: uint32 packet_length, byte padding_length, byte msg_type
    kex = False
    if len(after_id) >= 6:
        # msg type is at offset 5 (after 4-byte len + 1-byte pad len)
        msg_type = after_id[5]
        kex = msg_type == 20
        # some stacks may include ignore/debug first — scan first 64 bytes for 0x14
        if not kex and b"\x14" in after_id[:64]:
            kex = True
    suite.checks.append(
        CheckResult(
            id="rfc4253.kexinit_after_id",
            team="blue",
            passed=kex,
            detail="KEXINIT observed after version exchange" if kex else (err2 or "no KEXINIT"),
            score=100.0 if kex else 0.0,
        )
    )

    # 3) Grammar: bare LF identification from client should be rejected or tolerated
    #    RFC requires CR LF; compliant servers often still accept LF-only clients.
    #    We score *server* banner strictness already; here check unknown proto version.
    raw3, _, err3 = _transact(host, port, b"SSH-1.5-Ancient\r\n", recv_first=True)
    # Server may disconnect or still send its 2.0 banner; must not crash (connection ok path)
    alive = raw3.startswith(b"SSH-") or err3 == ""
    suite.checks.append(
        CheckResult(
            id="rfc4253.legacy_version_handling",
            team="blue",
            passed=alive,
            detail="handled SSH-1.5 probe without hang" if alive else (err3 or "failed"),
            score=100.0 if alive else 0.0,
        )
    )

    # 4) Null byte in identification — MUST NOT be accepted as valid (§4.2)
    raw4, _, err4 = _transact(host, port, b"SSH-2.0-Bad\x00name\r\n", recv_first=True)
    # Pass if connection drops or no successful KEXINIT after null id
    after = raw4.split(b"\r\n", 1)[1] if b"\r\n" in raw4 else b""
    continued = len(after) >= 6 and after[5] == 20
    suite.checks.append(
        CheckResult(
            id="rfc4253.reject_null_in_id",
            team="red",
            passed=not continued,
            detail="null in client ID did not proceed to KEX" if not continued else "accepted null ID",
            score=100.0 if not continued else 0.0,
            evidence=[err4 or raw4[:40].hex()],
        )
    )
    return suite

