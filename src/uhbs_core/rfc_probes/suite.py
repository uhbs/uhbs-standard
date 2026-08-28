"""Run and aggregate multi-protocol RFC probe suites."""
from __future__ import annotations

from uhbs_core.models import CheckResult

from .http_probe import probe_http_rfc9110
from .pop3 import probe_pop3_rfc1939
from .smtp import probe_smtp_rfc5321
from .ssh import probe_ssh_rfc4253
from .types import ProtoPorts, RFCSuiteResult


def run_rfc_suites(host: str, ports: ProtoPorts) -> list[RFCSuiteResult]:
    suites: list[RFCSuiteResult] = []
    if ports.ssh:
        suites.append(probe_ssh_rfc4253(host, ports.ssh))
    if ports.smtp:
        suites.append(probe_smtp_rfc5321(host, ports.smtp))
    if ports.pop3:
        suites.append(probe_pop3_rfc1939(host, ports.pop3))
    if ports.http:
        suites.append(probe_http_rfc9110(host, ports.http))
    return suites


def aggregate_rfc_score(suites: list[RFCSuiteResult]) -> tuple[float, list[CheckResult], dict]:
    """Average P_RFC across non-skipped protocol suites (0–100)."""
    active = [s for s in suites if not s.skipped]
    checks: list[CheckResult] = []
    for s in suites:
        if s.skipped:
            checks.append(
                CheckResult(
                    id=f"rfc.{s.protocol}.skipped",
                    team="blue",
                    passed=True,
                    detail=s.skip_reason or "skipped",
                    score=100.0,  # N/A skip — not a fidelity failure
                )
            )
            continue
        checks.extend(s.checks)
    if not active:
        return 0.0, checks, {"protocols_tested": 0}
    scores = [s.score for s in active]
    avg = sum(scores) / len(scores)
    metrics = {
        "protocols_tested": len(active),
        "per_protocol": {s.protocol: round(s.score, 2) for s in active},
        "rfcs": {s.protocol: s.rfc for s in active},
    }
    return round(avg, 2), checks, metrics
