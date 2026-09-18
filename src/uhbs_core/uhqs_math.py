"""Normative UHQS 5.0 math — single source of truth for CLI and UHBS-Lab.

scoring_model_id: uhqs-v5.0-critical-gate-diagnostic

When the assessment is COMPLETE and critical_control_verdict is GATE_PASSED:

    UHQS = w_A·S_A + w_B·S_B + w_C·S_C + w_E·S_E + w_F·S_F
    δ_C  = 1.0

Otherwise UHQS is null (no letter grade). Module D defense-in-depth remains
diagnostic and is never averaged into the weighted sum.

Both ``uhbs_cli.scoring`` and ``uhbs_core.models`` MUST import from here.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Immutable scoring-model identity (do not conflate with uhbs_version).
SCORING_MODEL_ID = "uhqs-v5.0-critical-gate-diagnostic"

# Letter keys (scorecards / CLI) ↔ dimension keys (harness)
LETTER_TO_DIM = {
    "A": "protocol",
    "B": "behavior",
    "C": "telemetry",
    "D": "containment",
    "E": "scale",
    "F": "static",
}
DIM_TO_LETTER = {v: k for k, v in LETTER_TO_DIM.items()}

# Legacy aliases accepted when normalizing harness score maps
DIM_ALIASES = {
    "protocol": "protocol",
    "behavior": "behavior",
    "telemetry": "telemetry",
    "containment": "containment",
    "scale": "scale",
    "static": "static",
    "stealth": "protocol",
    "realism": "behavior",
    "efficiency": "scale",
    "A": "protocol",
    "B": "behavior",
    "C": "telemetry",
    "D": "containment",
    "E": "scale",
    "F": "static",
}

WEIGHT_KEYS = ("w_A", "w_B", "w_C", "w_E", "w_F")
SCORE_KEYS = ("A", "B", "C", "D", "E", "F")
DIM_KEYS = ("protocol", "behavior", "telemetry", "containment", "scale", "static")

# Grade band thresholds (letter → long harness label) — only for COMPLETE graded results
GRADE_BANDS: tuple[tuple[float, str, str], ...] = (
    (90.0, "A", "GRADE A (Enterprise Grade)"),
    (80.0, "B", "GRADE B (Production Baseline)"),
    (70.0, "C", "GRADE C (Conditional — not approved for production)"),
    (50.0, "D", "GRADE D (Needs Remediation)"),
    (0.0, "F", "GRADE F (Fail)"),
)

# Profile-adaptive weights (§5.3) — letter-key form (normative for scorecards)
PROFILE_WEIGHTS: dict[str, dict[str, float]] = {
    "POSIX-Shell": {"w_A": 0.20, "w_B": 0.25, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20},
    "GenAI-Shell": {"w_A": 0.20, "w_B": 0.25, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20},
    "Low-Interaction": {"w_A": 0.30, "w_B": 0.15, "w_C": 0.25, "w_E": 0.10, "w_F": 0.20},
    "ICS-SCADA": {"w_A": 0.35, "w_B": 0.20, "w_C": 0.15, "w_E": 0.10, "w_F": 0.20},
    "Web-API": {"w_A": 0.25, "w_B": 0.20, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20},
    "Database": {"w_A": 0.25, "w_B": 0.25, "w_C": 0.20, "w_E": 0.10, "w_F": 0.20},
}


class AssessmentStatus(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class CriticalControlVerdict(str, Enum):
    GATE_PASSED = "GATE_PASSED"
    GATE_FAILED = "GATE_FAILED"
    INCOMPLETE = "INCOMPLETE"


def weights_for_class(profile_class: str) -> dict[str, float]:
    return dict(PROFILE_WEIGHTS.get(profile_class, PROFILE_WEIGHTS["POSIX-Shell"]))


def weights_for_class_dims(profile_class: str) -> dict[str, float]:
    """Weights keyed by dimension names for harness report code."""
    letter = weights_for_class(profile_class)
    return {
        "protocol": letter["w_A"],
        "behavior": letter["w_B"],
        "telemetry": letter["w_C"],
        "scale": letter["w_E"],
        "static": letter["w_F"],
    }


def validate_weights(weights: Mapping[str, float], tol: float = 0.001) -> tuple[bool, float]:
    total = float(sum(float(weights[k]) for k in WEIGHT_KEYS))
    return abs(total - 1.0) <= tol, total


def safety_gate(
    containment_score: float,
    *,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
) -> tuple[float, bool]:
    """Return (δ_C, passed) under the v5 critical-gate model.

    When ``critical_control_verdict`` is provided it is authoritative:
    only ``GATE_PASSED`` yields δ_C=1.0 / passed=True. Defense-in-depth
    ``containment_score`` alone never clears the gate.

    Legacy callers that pass only a numeric Module D score are treated as
    GATE_PASSED iff C >= 95 (compat shim for transitional tests); prefer
    the explicit verdict API.
    """
    if critical_control_verdict is not None:
        verdict = CriticalControlVerdict(str(critical_control_verdict))
        if verdict is CriticalControlVerdict.GATE_PASSED:
            return 1.0, True
        return 0.0, False

    c = float(containment_score)
    if c >= 95:
        return 1.0, True
    return 0.0, False


def letter_grade(uhqs: float | None) -> str | None:
    """Letter grade for a completed UHQS, or None when ungraded."""
    if uhqs is None:
        return None
    for threshold, letter, _long in GRADE_BANDS:
        if uhqs >= threshold:
            return letter
    return "F"


def grade_for(uhqs: float | None) -> str | None:
    """Long-form grade string used by harness SCORECARD.txt, or None."""
    if uhqs is None:
        return None
    for threshold, _letter, long in GRADE_BANDS:
        if uhqs >= threshold:
            return long
    return "GRADE F (Fail)"


def normalize_module_scores(scores: Mapping[str, float]) -> dict[str, float]:
    """Normalize letter or dimension keys to A–F. Raises KeyError if any module missing."""
    by_dim: dict[str, float] = {}
    for key, value in scores.items():
        dim = DIM_ALIASES.get(str(key))
        if dim is None:
            continue
        by_dim[dim] = float(value)

    missing = [DIM_TO_LETTER[d] for d in DIM_KEYS if d not in by_dim]
    if missing:
        raise KeyError(f"Missing module scores: {', '.join(missing)}")

    return {DIM_TO_LETTER[d]: by_dim[d] for d in DIM_KEYS}


@dataclass(frozen=True)
class UhqsComputation:
    """Canonical UHQS computation result (shared by CLI and harness)."""

    scores: dict[str, float]  # A–F (D = defense-in-depth diagnostic)
    weights: dict[str, float]  # w_*
    weighted_sum: float
    delta_c: float
    uhqs: float | None
    safety_gate_passed: bool
    containment_measured: bool
    assessment_status: AssessmentStatus
    critical_control_verdict: CriticalControlVerdict
    scoring_model_id: str = SCORING_MODEL_ID
    graded: bool = False


def compute_uhqs(
    scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
    *,
    profile_class: str | None = None,
    containment_measured: bool = True,
    assessment_status: AssessmentStatus | str = AssessmentStatus.COMPLETE,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
) -> UhqsComputation:
    """Compute UHQS from module scores under scoring_model_id.

    ``scores`` may use letter keys (A–F) or dimension keys (protocol, …).
    Missing modules raise ``KeyError`` — never silently default to 0.0.

    Incomplete assessments and failed/incomplete critical-control verdicts
    yield ``uhqs=None`` (no letter grade).
    """
    normalized = normalize_module_scores(scores)

    if weights is None:
        if not profile_class:
            raise ValueError("Provide weights or profile_class")
        weights = weights_for_class(profile_class)

    ok, total = validate_weights(weights)
    if not ok:
        raise ValueError(f"module_weights must sum to 1.0 (±0.001); got {total}")

    weighted = (
        float(weights["w_A"]) * normalized["A"]
        + float(weights["w_B"]) * normalized["B"]
        + float(weights["w_C"]) * normalized["C"]
        + float(weights["w_E"]) * normalized["E"]
        + float(weights["w_F"]) * normalized["F"]
    )

    status = AssessmentStatus(str(assessment_status))

    if not containment_measured:
        verdict = CriticalControlVerdict.INCOMPLETE
    elif critical_control_verdict is not None:
        verdict = CriticalControlVerdict(str(critical_control_verdict))
    else:
        # Transitional: infer from legacy numeric gate threshold.
        delta_legacy, passed_legacy = safety_gate(normalized["D"])
        verdict = (
            CriticalControlVerdict.GATE_PASSED
            if passed_legacy
            else CriticalControlVerdict.GATE_FAILED
        )
        _ = delta_legacy

    if status is AssessmentStatus.INCOMPLETE or verdict is CriticalControlVerdict.INCOMPLETE:
        return UhqsComputation(
            scores=normalized,
            weights={k: float(weights[k]) for k in WEIGHT_KEYS},
            weighted_sum=round(weighted, 6),
            delta_c=0.0,
            uhqs=None,
            safety_gate_passed=False,
            containment_measured=containment_measured,
            assessment_status=AssessmentStatus.INCOMPLETE,
            critical_control_verdict=CriticalControlVerdict.INCOMPLETE
            if verdict is CriticalControlVerdict.INCOMPLETE
            else verdict,
            graded=False,
        )

    if verdict is CriticalControlVerdict.GATE_FAILED:
        return UhqsComputation(
            scores=normalized,
            weights={k: float(weights[k]) for k in WEIGHT_KEYS},
            weighted_sum=round(weighted, 6),
            delta_c=0.0,
            uhqs=None,
            safety_gate_passed=False,
            containment_measured=containment_measured,
            assessment_status=status,
            critical_control_verdict=verdict,
            graded=False,
        )

    # GATE_PASSED + COMPLETE
    uhqs = round(weighted, 2)
    return UhqsComputation(
        scores=normalized,
        weights={k: float(weights[k]) for k in WEIGHT_KEYS},
        weighted_sum=round(weighted, 6),
        delta_c=1.0,
        uhqs=uhqs,
        safety_gate_passed=True,
        containment_measured=containment_measured,
        assessment_status=status,
        critical_control_verdict=verdict,
        graded=True,
    )


def assessment_from_module_results(
    modules: Mapping[str, Any],
    *,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
) -> tuple[AssessmentStatus, CriticalControlVerdict]:
    """Derive assessment status / verdict from ModuleResult-like mappings."""
    incomplete = False
    for key in ("A", "B", "C", "D", "E", "F"):
        mod = modules.get(key) or {}
        status = str(mod.get("status", "")).upper()
        if status in {"INCOMPLETE", "NOT_MEASURED", "ERROR"}:
            incomplete = True
        if mod.get("complete") is False:
            incomplete = True
        coverage = mod.get("completeness") or {}
        if coverage.get("complete") is False:
            incomplete = True

    if critical_control_verdict is not None:
        verdict = CriticalControlVerdict(str(critical_control_verdict))
    else:
        d_mod = modules.get("D") or {}
        raw = d_mod.get("critical_control_verdict") or d_mod.get("status")
        raw_s = str(raw or "").upper().replace(" ", "_")
        if raw_s in {"GATE_PASSED", "GATEPASSED"}:
            verdict = CriticalControlVerdict.GATE_PASSED
        elif raw_s in {"GATE_FAILED", "GATEFAILED", "FAILED"}:
            verdict = CriticalControlVerdict.GATE_FAILED
        elif incomplete or raw_s in {"INCOMPLETE", "SKIPPED", "N/A", "NOT_RUN", "NOT_TESTED"}:
            verdict = CriticalControlVerdict.INCOMPLETE
        else:
            # Fall back to numeric D score if present
            try:
                score = float(d_mod.get("score", 0))
            except (TypeError, ValueError):
                score = 0.0
            _, passed = safety_gate(score)
            verdict = (
                CriticalControlVerdict.GATE_PASSED
                if passed
                else CriticalControlVerdict.GATE_FAILED
            )

    status = AssessmentStatus.INCOMPLETE if incomplete else AssessmentStatus.COMPLETE
    if verdict is CriticalControlVerdict.INCOMPLETE:
        status = AssessmentStatus.INCOMPLETE
    return status, verdict
