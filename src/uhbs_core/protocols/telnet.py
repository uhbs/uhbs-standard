from __future__ import annotations

from uhbs_core.protocols.base import ProtocolPlugin

from ..models import CheckResult, TargetSpec
from ..rfc_probes.telnet import _negate_options, probe_telnet_rfc854
from ..tps import TPS

__all__ = ["TelnetPlugin", "_negate_options"]


class TelnetPlugin(ProtocolPlugin):
    """Telnet (RFC 854) — 10-check suite via rfc_probes.telnet."""

    name = "telnet"
    families = ("it", "posix")

    @staticmethod
    def _strict(tps: TPS | None) -> bool:
        return tps is None or tps.strict_rfc_enforcement

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_telnet_rfc854(host, port)
        strict = self._strict(tps)
        if suite.skipped:
            return [
                CheckResult(
                    id="telnet.fsm.connect",
                    team="blue",
                    critical=strict,
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        checks: list[CheckResult] = []
        for c in suite.checks:
            if not c.id.startswith("telnet.fsm."):
                continue
            if c.id == "telnet.fsm.iac_negotiation":
                passed = c.passed
                score = float(c.score)
                detail = c.detail or ""
                if not passed and not strict:
                    score = 35.0
                    detail += " (Canary/Alert mode: not hard-failed)"
                checks.append(
                    CheckResult(
                        id=c.id,
                        team=c.team,
                        passed=passed,
                        detail=detail,
                        score=score,
                        critical=strict,
                        evidence=list(c.evidence or []),
                        catalog_id=c.catalog_id,
                    )
                )
            else:
                checks.append(c)
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_telnet_rfc854(host, port)
        if suite.skipped:
            return [
                CheckResult(
                    id="telnet.nego.skipped",
                    team="blue",
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        # A2 only — login_prompt stays in probe_state (B1) to avoid double-weight.
        return [c for c in suite.checks if c.id.startswith("telnet.nego.")]

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        suite = probe_telnet_rfc854(host, port)
        if suite.skipped:
            return [
                CheckResult(
                    id="telnet.state.login_prompt",
                    team="blue",
                    passed=False,
                    detail=suite.skip_reason,
                    score=0.0,
                )
            ]
        return [c for c in suite.checks if c.id == "telnet.state.login_prompt"]
