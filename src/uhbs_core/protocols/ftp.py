from __future__ import annotations

import socket

from uhbs_core.protocols.base import ProtocolPlugin

from ..models import CheckResult, TargetSpec
from ..rfc_probes.ftp import probe_ftp_rfc959
from ..tps import TPS


def _recv_line(s: socket.socket, timeout: float = 2.0) -> str:
    s.settimeout(timeout)
    try:
        return s.recv(512).decode("utf-8", "replace")
    except TimeoutError:
        return ""


class FTPPlugin(ProtocolPlugin):
    """RFC 959 FTP control-channel probe (10-check suite + login state walk)."""

    name = "ftp"
    families = ("it",)

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_ftp_rfc959(host, port)
        if suite.skipped:
            return [
                CheckResult(
                    id="ftp.fsm.skipped",
                    team="blue",
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        return [c for c in suite.checks if c.id.startswith("ftp.fsm.")]

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_ftp_rfc959(host, port)
        if suite.skipped:
            return [
                CheckResult(
                    id="ftp.nego.skipped",
                    team="blue",
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        return [c for c in suite.checks if c.id.startswith("ftp.nego.")]

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        """USER -> PASS -> PWD on one connection (fail-fast)."""
        try:
            with socket.create_connection((host, port), timeout=3.0) as s:
                _recv_line(s)

                s.sendall(b"USER anonymous\r\n")
                user_resp = _recv_line(s)
                if "230" in user_resp:
                    pass_resp = user_resp
                elif "331" in user_resp:
                    s.sendall(b"PASS guest@\r\n")
                    pass_resp = _recv_line(s)
                    if "230" not in pass_resp:
                        return [
                            CheckResult(
                                id="ftp.state.login_pwd",
                                team="blue",
                                passed=False,
                                detail=f"PASS step failed: {pass_resp[:120] or 'no response'}",
                                score=30.0,
                            )
                        ]
                else:
                    return [
                        CheckResult(
                            id="ftp.state.login_pwd",
                            team="blue",
                            passed=False,
                            detail=f"USER step failed: {user_resp[:120] or 'no response'}",
                            score=30.0,
                        )
                    ]

                s.sendall(b"PWD\r\n")
                pwd_resp = _recv_line(s)
                s.sendall(b"QUIT\r\n")
                ok = "257" in pwd_resp
                return [
                    CheckResult(
                        id="ftp.state.login_pwd",
                        team="blue",
                        passed=ok,
                        detail=(
                            f"USER={user_resp.strip()[:60]!r} PASS={pass_resp.strip()[:60]!r} "
                            f"PWD={pwd_resp.strip()[:60]!r}"
                        ),
                        score=100.0 if ok else 60.0,
                    )
                ]
        except OSError as exc:
            return [
                CheckResult(
                    id="ftp.state.login_pwd",
                    team="blue",
                    passed=False,
                    detail=str(exc),
                    score=0.0,
                )
            ]
