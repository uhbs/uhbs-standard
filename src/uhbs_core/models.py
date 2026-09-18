"""UHBS v5 — Universal Honeypot Benchmarking Standard shared types.

Check outcomes: PASS | FAIL | NOT_APPLICABLE | NOT_TESTED | ERROR.
Only NOT_APPLICABLE leaves the scoring denominator. Incomplete mandatory
applicable checks yield an Ungraded assessment (uhqs=null, no letter grade).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from uhbs_core._version import __version__
from uhbs_core.outcomes import CheckOutcome, outcome_from_passed
from uhbs_core.uhqs_math import (
    PROFILE_WEIGHTS as _LETTER_WEIGHTS,
)
from uhbs_core.uhqs_math import (
    SCORING_MODEL_ID,
    AssessmentStatus,
    CriticalControlVerdict,
    grade_for,
    weights_for_class_dims,
)
from uhbs_core.uhqs_math import (
    compute_uhqs as _shared_compute_uhqs,
)

# Module letter ↔ dimension keys (stable internal IDs)
DIM_A = "protocol"  # Module A — Protocol & Syntax Fidelity
DIM_B = "behavior"  # Module B — Behavioral & Stateful Realism
DIM_C = "telemetry"  # Module C — Telemetry Quality
DIM_D = "containment"  # Module D — Safety gate (critical controls)
DIM_E = "scale"  # Module E — Scalability & Latency
DIM_F = "static"  # Module F — White-Box Static Audit

# Backward-compatible aliases used by older module code
DIM_STEALTH = DIM_A
DIM_REALISM = DIM_B
DIM_TELEMETRY = DIM_C
DIM_CONTAINMENT = DIM_D
DIM_EFFICIENCY = DIM_E
DIM_STATIC = DIM_F

DIMS = (DIM_A, DIM_B, DIM_C, DIM_D, DIM_E, DIM_F)

WEIGHTS_POSIX = weights_for_class_dims("POSIX-Shell")
PROFILE_WEIGHTS: dict[str, dict[str, float]] = {
    name: weights_for_class_dims(name) for name in _LETTER_WEIGHTS
}

DIM_LABELS = {
    DIM_A: "Module A: Protocol Fidelity",
    DIM_B: "Module B: Behavioral Realism",
    DIM_C: "Module C: Telemetry Assurance",
    DIM_D: "Module D: Safety & Containment (C)",
    DIM_E: "Module E: Scalability & Latency",
    DIM_F: "Module F: Static Code Audit",
}

# Scorecard attribute names
UHQS_ATTR = {
    DIM_A: "S_A",
    DIM_B: "S_B",
    DIM_C: "S_C",
    DIM_D: "C",
    DIM_E: "S_E",
    DIM_F: "S_F",
}


@dataclass
class CheckResult:
    """Single check result with an explicit outcome.

    Constructors SHOULD pass ``outcome=`` explicitly. Legacy ``passed=`` is
    accepted and mapped to PASS/FAIL so existing plugins keep compiling; new
    plugins must not rely on implicit measurement credit.
    """

    id: str
    team: str  # blue | red | white
    passed: bool = False
    detail: str = ""
    score: float = 0.0
    evidence: list[str] = field(default_factory=list)
    critical: bool = False
    outcome: CheckOutcome | None = None
    mandatory: bool = True
    applicability_rationale: str | None = None
    catalog_id: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    evidence_hashes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.outcome is None:
            self.outcome = outcome_from_passed(bool(self.passed))
        elif isinstance(self.outcome, str):
            self.outcome = CheckOutcome(self.outcome)
        # Keep passed synchronized for legacy consumers.
        self.passed = self.outcome is CheckOutcome.PASS

        if self.outcome in {
            CheckOutcome.NOT_TESTED,
            CheckOutcome.ERROR,
            CheckOutcome.NOT_APPLICABLE,
        } and self.score > 0.0:
            # Untested / error / NA never earn credit.
            self.score = 0.0

    @property
    def earns_credit(self) -> bool:
        return self.outcome is CheckOutcome.PASS

    @property
    def in_denominator(self) -> bool:
        return self.outcome is not CheckOutcome.NOT_APPLICABLE

    @property
    def blocks_completeness(self) -> bool:
        """True when this mandatory applicable check prevents a graded module."""
        if not self.mandatory:
            return False
        if self.outcome is CheckOutcome.NOT_APPLICABLE:
            return False
        return self.outcome in {CheckOutcome.NOT_TESTED, CheckOutcome.ERROR}

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["outcome"] = self.outcome.value if self.outcome else None
        return d

    @classmethod
    def make(
        cls,
        *,
        id: str,
        team: str,
        outcome: CheckOutcome,
        detail: str = "",
        score: float = 0.0,
        evidence: list[str] | None = None,
        critical: bool = False,
        applicability_rationale: str | None = None,
        evidence_refs: list[str] | None = None,
        catalog_id: str | None = None,
        mandatory: bool = True,
        criterion: str | None = None,
    ) -> CheckResult:
        """Explicit-outcome constructor (preferred for new code)."""
        _ = criterion  # reserved for evidence-pack criterion text
        return cls(
            id=id,
            team=team,
            passed=outcome is CheckOutcome.PASS,
            detail=detail,
            score=score,
            evidence=evidence or [],
            critical=critical,
            outcome=outcome,
            applicability_rationale=applicability_rationale,
            evidence_refs=evidence_refs or [],
            catalog_id=catalog_id,
            mandatory=mandatory,
        )


@dataclass
class ModuleResult:
    module: str  # A|B|C|D|E|F|SOURCE
    dimension: str
    score: float
    status: str
    checks: list[CheckResult] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    error: str | None = None
    complete: bool = True
    applicable_checks: int = 0
    scored_checks: int = 0
    critical_control_verdict: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "dimension": self.dimension,
            "score": self.score,
            "status": self.status,
            "checks": [c.to_dict() for c in self.checks],
            "metrics": self.metrics,
            "notes": self.notes,
            "error": self.error,
            "complete": self.complete,
            "applicable_checks": self.applicable_checks,
            "scored_checks": self.scored_checks,
            "critical_control_verdict": self.critical_control_verdict,
        }


@dataclass
class TargetSpec:
    """Runtime binding of a decoy instance (+ optional TPS)."""

    name: str
    kind: str = "generic"
    source_root: str | None = None
    host: str | None = None
    port: int = 2222
    user: str = "root"
    password: str = "root"
    telemetry_dir: str | None = None
    profile: str | None = None  # signals profile stem OR path to TPS
    baseline_native_host: str | None = None
    container_image: str | None = None
    smtp_port: int | None = None
    http_port: int | None = None
    ssh_port: int | None = None
    # UHBS v4/v5
    tps_path: str | None = None
    protocol: str | None = None  # primary protocol id
    protocols: list[str] = field(default_factory=list)  # multi-protocol
    profile_class: str = "POSIX-Shell"
    ports_map: dict[str, int] = field(default_factory=dict)
    # Lab inventory annotations (mcp_path, mcp_transport, mcp_custom_allowlist_tools, …)
    annotations: dict[str, Any] = field(default_factory=dict)
    native_event_format: str | None = None
    export_formats: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return self.name or self.host or self.source_root or "unknown"

    def effective_ssh_port(self) -> int:
        """Legacy helper — prefer ``shell_exec_port()`` for Module D.

        Only returns an explicit SSH listener. Does **not** invent SSH on the
        primary application port (e.g. PJL :9100 or HTTP :9200).
        """
        port = self.shell_exec_port()
        if port is not None:
            return port
        raise ValueError(
            "no explicit SSH listener configured "
            "(set ports.ssh / ssh_port, or --protocol ssh --port …)"
        )

    def shell_exec_port(self) -> int | None:
        """Port for remote shell / containment probes (Module D).

        Protocol-agnostic rule: shell probes run **only** when SSH is
        explicitly configured. Never treat the primary decoy port as SSH
        just because a TPS mentioned ssh elsewhere.
        """
        if "ssh" in self.ports_map:
            return int(self.ports_map["ssh"])
        if self.ssh_port is not None:
            return int(self.ssh_port)
        return None

    def port_for(self, protocol: str) -> int | None:
        p = protocol.lower()
        if p in self.ports_map:
            return int(self.ports_map[p])
        if p == "ssh":
            return self.shell_exec_port()
        if p == "smtp":
            if self.smtp_port is not None:
                return self.smtp_port
            if self.protocol and self.protocol.lower() == "smtp":
                return int(self.port)
            return None
        if p in {"http", "https"}:
            if self.http_port is not None:
                return self.http_port
            if self.protocol and self.protocol.lower() in {"http", "https"}:
                return int(self.port)
            return None
        # Unknown / custom protocols (pjl, redis, …): map primary port when it matches
        if self.protocol and self.protocol.lower() == p:
            return int(self.port)
        return None

    def protocol_list(self) -> list[str]:
        if self.protocols:
            return [x.lower() for x in self.protocols if x]
        if self.protocol:
            return [self.protocol.lower()]
        # Infer from configured ports — never invent SSH by default
        found: list[str] = []
        for key in sorted(self.ports_map.keys()):
            found.append(key.lower())
        if not found and self.shell_exec_port() is not None:
            found.append("ssh")
        if not found and self.http_port is not None:
            found.append("http")
        if not found and self.smtp_port is not None:
            found.append("smtp")
        return found

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UHQSResult:
    target: str
    S_A: float
    S_B: float
    S_C: float
    C: float
    S_E: float
    S_F: float
    delta_c: float
    uhqs: float | None
    weights: dict[str, float]
    profile_class: str
    grade: str | None
    phase: str = "combined"
    version: str = __version__
    containment_measured: bool = True
    assessment_status: str = AssessmentStatus.COMPLETE.value
    critical_control_verdict: str = CriticalControlVerdict.GATE_PASSED.value
    scoring_model_id: str = SCORING_MODEL_ID
    graded: bool = True

    # Compat with older report code expecting .hqs / .S/.R/...
    @property
    def hqs(self) -> float | None:
        return self.uhqs

    @property
    def S(self) -> float:
        return self.S_A

    @property
    def R(self) -> float:
        return self.S_B

    @property
    def Q(self) -> float:
        return self.S_C

    @property
    def E(self) -> float:
        return self.S_E

    @property
    def F(self) -> float:
        return self.S_F

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def weights_for_class(profile_class: str) -> dict[str, float]:
    return weights_for_class_dims(profile_class)


def compute_uhqs(
    scores: dict[str, float],
    target: str,
    profile_class: str = "POSIX-Shell",
    phase: str = "combined",
    *,
    containment_measured: bool = True,
    assessment_status: AssessmentStatus | str = AssessmentStatus.COMPLETE,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
) -> UHQSResult:
    """UHQS under scoring_model_id (critical-gate + diagnostic modules).

    Missing module scores raise ``KeyError`` (never silently default to 0.0).
    Math is delegated to ``uhbs_core.uhqs_math`` (shared with the CLI).
    """
    result = _shared_compute_uhqs(
        scores,
        profile_class=profile_class,
        containment_measured=containment_measured,
        assessment_status=assessment_status,
        critical_control_verdict=critical_control_verdict,
    )
    s = result.scores
    uhqs_val = result.uhqs
    return UHQSResult(
        target=target,
        S_A=round(s["A"], 2),
        S_B=round(s["B"], 2),
        S_C=round(s["C"], 2),
        C=round(s["D"], 2),
        S_E=round(s["E"], 2),
        S_F=round(s["F"], 2),
        delta_c=round(result.delta_c, 4),
        uhqs=uhqs_val,
        weights=weights_for_class(profile_class),
        profile_class=profile_class,
        grade=grade_for(uhqs_val) if uhqs_val is not None else None,
        phase=phase,
        version=__version__,
        containment_measured=containment_measured,
        assessment_status=result.assessment_status.value,
        critical_control_verdict=result.critical_control_verdict.value,
        scoring_model_id=result.scoring_model_id,
        graded=result.graded,
    )


# Backward-compatible name
HQSResult = UHQSResult


def compute_hqs(
    scores: dict[str, float],
    target: str,
    phase: str = "combined",
    profile_class: str = "POSIX-Shell",
) -> UHQSResult:
    return compute_uhqs(scores, target=target, profile_class=profile_class, phase=phase)


def average_scores(*score_maps: dict[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    for dim in DIMS:
        vals = [m[dim] for m in score_maps if dim in m]
        out[dim] = round(sum(vals) / len(vals), 2) if vals else 0.0
    return out


def module_completeness(checks: list[CheckResult]) -> dict[str, Any]:
    """Summarize applicability / completeness for a module check list."""
    applicable = [c for c in checks if c.in_denominator]
    scored = [
        c
        for c in applicable
        if c.outcome in {CheckOutcome.PASS, CheckOutcome.FAIL}
    ]
    blockers = [c for c in checks if c.blocks_completeness]
    complete = len(blockers) == 0
    return {
        "complete": complete,
        "applicable_checks": len(applicable),
        "scored_checks": len(scored),
        "not_applicable": sum(1 for c in checks if c.outcome is CheckOutcome.NOT_APPLICABLE),
        "not_tested": sum(1 for c in checks if c.outcome is CheckOutcome.NOT_TESTED),
        "errors": sum(1 for c in checks if c.outcome is CheckOutcome.ERROR),
        "blocker_ids": [c.id for c in blockers],
    }
