"""Shared types for RFC protocol probe suites."""
from __future__ import annotations

from dataclasses import dataclass, field

from uhbs_core.models import CheckResult


@dataclass
class ProtoPorts:
    """Per-protocol decoy ports on a target host."""

    ssh: int | None = None
    smtp: int | None = None
    pop3: int | None = None
    http: int | None = None


@dataclass
class RFCSuiteResult:
    protocol: str
    rfc: str
    checks: list[CheckResult] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""

    @property
    def score(self) -> float:
        """Suite score on a 0–100 scale.

        Each check is itself 0–100 (see probe_* below). Aggregation uses the
        shared Module A/B geometric-mean helper so a perfect suite scores
        ~100 and a single hard fail still visibly drags the result — the
        prior ``sum(c.score)`` path assumed partial-point checks that added
        up to 100 and silently capped a perfect multi-check suite once
        scores were normalized.
        """
        if self.skipped or not self.checks:
            return 0.0
        from uhbs_core.check_scoring import score_checks

        return score_checks(self.checks)

    @property
    def max_score(self) -> float:
        return 100.0

