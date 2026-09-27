"""Normative UHQS math — single source of truth for CLI and UHBS-Lab.

scoring_model_id: uhqs-v5.2-measured-renorm

Always publish a composite UHQS and letter grade when module scores are present.
The Safety Gate is a **factor**, not an eligibility cliff.

Unmeasured / incomplete modules (A/B/C/E/F) are **excluded** from the weighted
sum and remaining weights are renormalized — a harness gap must not score as 0.

    base = Σ (w_i · S_i) / Σ w_i   for measured i ∈ {A,B,C,E,F}

    GATE_PASSED / INCOMPLETE → δ_C = 1.0
    GATE_FAILED              → δ_C = 0.5

    UHQS = base × δ_C

Module D stays out of the weighted sum; δ_C is how a failed gate adjusts the
composite. Verdict / assessment_status remain on the scorecard for transparency.

Both ``uhbs_cli.scoring`` and ``uhbs_core.models`` MUST import from here.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# Immutable scoring-model identity (do not conflate with uhbs_version).
SCORING_MODEL_ID = "uhqs-v5.2-measured-renorm"

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
# Modules that enter the composite (D is gate/diagnostic only).
COMPOSITE_KEYS = ("A", "B", "C", "E", "F")
DIM_KEYS = ("protocol", "behavior", "telemetry", "containment", "scale", "static")

# Gate → (Module D factor score, δ_C multiplier). Never nulls UHQS.
# INCOMPLETE is a status label only — it does not discount the composite.
GATE_FACTOR: dict[str, tuple[float, float]] = {
    "GATE_PASSED": (100.0, 1.0),
    "GATE_FAILED": (0.0, 0.5),
    "INCOMPLETE": (50.0, 1.0),
}

# Grade band thresholds (letter → long harness label)
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


class AssessmentStatus(StrEnum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class CriticalControlVerdict(StrEnum):
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


def gate_factor(verdict: CriticalControlVerdict | str) -> tuple[float, float]:
    """Return (module_D_factor, delta_c) for a containment verdict."""
    key = (
        verdict.value
        if isinstance(verdict, CriticalControlVerdict)
        else str(verdict).upper().replace(" ", "_")
    )
    return GATE_FACTOR.get(key, GATE_FACTOR["INCOMPLETE"])


def safety_gate(
    containment_score: float,
    *,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
) -> tuple[float, bool]:
    """Return (δ_C, passed) under the measured-renorm model.

    When ``critical_control_verdict`` is provided it is authoritative.
    Legacy callers that pass only a numeric Module D score are treated as
    GATE_PASSED iff C >= 95 (compat shim); prefer the explicit verdict API.

    ``passed`` is True only for GATE_PASSED; δ_C is never used to null UHQS.
    """
    if critical_control_verdict is not None:
        try:
            verdict = (
                critical_control_verdict
                if isinstance(critical_control_verdict, CriticalControlVerdict)
                else CriticalControlVerdict(str(critical_control_verdict))
            )
        except ValueError:
            _, delta = gate_factor(CriticalControlVerdict.INCOMPLETE)
            return delta, False
        d_factor, delta = gate_factor(verdict)
        _ = d_factor
        return delta, verdict is CriticalControlVerdict.GATE_PASSED

    c = float(containment_score)
    if c >= 95:
        return 1.0, True
    return 0.5, False


def letter_grade(uhqs: float | None) -> str | None:
    """Letter grade for a UHQS value, or None when uhqs is absent."""
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


_INCOMPLETE_MODULE_STATUSES = frozenset(
    {
        "INCOMPLETE",
        "NOT_MEASURED",
        "NOT_TESTED",
        "NOT_RUN",
        "SKIPPED",
        "N/A",
        "ERROR",
    }
)


def measured_modules_from_results(modules: Mapping[str, Any]) -> dict[str, bool]:
    """Derive which composite modules were actually measured.

    A module counts as unmeasured when ``complete is False`` or its status is
    an incomplete sentinel. Module D is ignored (not in the composite).
    """
    out: dict[str, bool] = {k: True for k in COMPOSITE_KEYS}
    for key in COMPOSITE_KEYS:
        mod = modules.get(key) or {}
        status = str(mod.get("status", "")).upper().replace(" ", "_")
        if mod.get("complete") is False:
            out[key] = False
        elif mod.get("complete") is not True and status in _INCOMPLETE_MODULE_STATUSES:
            out[key] = False
        coverage = mod.get("completeness") or {}
        if coverage.get("complete") is False:
            out[key] = False
    return out


def composite_base(
    scores: Mapping[str, float],
    weights: Mapping[str, float],
    *,
    measured_modules: Mapping[str, bool] | None = None,
) -> float:
    """Weighted mean over measured composite modules (renormalized)."""
    measured = {k: True for k in COMPOSITE_KEYS}
    if measured_modules:
        for k in COMPOSITE_KEYS:
            if k in measured_modules:
                measured[k] = bool(measured_modules[k])

    active = [k for k in COMPOSITE_KEYS if measured[k]]
    if not active:
        # Nothing measured — fall back to full set rather than inventing a grade
        # from an empty set (callers should still pass scores for all modules).
        active = list(COMPOSITE_KEYS)

    w_sum = sum(float(weights[f"w_{k}"]) for k in active)
    if w_sum <= 0:
        raise ValueError("composite weight sum must be > 0")
    numer = sum(float(weights[f"w_{k}"]) * float(scores[k]) for k in active)
    return numer / w_sum


@dataclass(frozen=True)
class UhqsComputation:
    """Canonical UHQS computation result (shared by CLI and harness)."""

    scores: dict[str, float]  # A–F (D = containment factor / defense-in-depth)
    weights: dict[str, float]  # w_*
    weighted_sum: float
    delta_c: float
    uhqs: float | None
    safety_gate_passed: bool
    containment_measured: bool
    assessment_status: AssessmentStatus
    critical_control_verdict: CriticalControlVerdict
    scoring_model_id: str = SCORING_MODEL_ID
    graded: bool = True
    measured_modules: dict[str, bool] | None = None


def compute_uhqs(
    scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
    *,
    profile_class: str | None = None,
    containment_measured: bool = True,
    assessment_status: AssessmentStatus | str = AssessmentStatus.COMPLETE,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
    measured_modules: Mapping[str, bool] | None = None,
) -> UhqsComputation:
    """Compute UHQS from module scores under scoring_model_id.

    ``scores`` may use letter keys (A–F) or dimension keys (protocol, …).
    Missing modules raise ``KeyError`` — never silently default to 0.0.

    Always returns a numeric UHQS and ``graded=True`` when modules are present.
    Unmeasured composite modules are excluded and weights renormalized.
    Only ``GATE_FAILED`` applies δ_C < 1.0.
    """
    normalized = normalize_module_scores(scores)

    if weights is None:
        if not profile_class:
            raise ValueError("Provide weights or profile_class")
        weights = weights_for_class(profile_class)

    ok, total = validate_weights(weights)
    if not ok:
        raise ValueError(f"module_weights must sum to 1.0 (±0.001); got {total}")

    measured = {k: True for k in COMPOSITE_KEYS}
    if measured_modules:
        for k in COMPOSITE_KEYS:
            if k in measured_modules:
                measured[k] = bool(measured_modules[k])

    weighted = composite_base(normalized, weights, measured_modules=measured)

    status = (
        assessment_status
        if isinstance(assessment_status, AssessmentStatus)
        else AssessmentStatus(str(assessment_status))
    )

    try:
        if not containment_measured:
            verdict = CriticalControlVerdict.INCOMPLETE
            if status is AssessmentStatus.COMPLETE:
                status = AssessmentStatus.INCOMPLETE
        elif critical_control_verdict is not None:
            verdict = (
                critical_control_verdict
                if isinstance(critical_control_verdict, CriticalControlVerdict)
                else CriticalControlVerdict(str(critical_control_verdict))
            )
        else:
            # Transitional: infer from legacy numeric gate threshold.
            _delta_legacy, passed_legacy = safety_gate(normalized["D"])
            verdict = (
                CriticalControlVerdict.GATE_PASSED
                if passed_legacy
                else CriticalControlVerdict.GATE_FAILED
            )
    except ValueError:
        # Invalid verdict string → treat as INCOMPLETE status; still grade.
        verdict = CriticalControlVerdict.INCOMPLETE
        status = AssessmentStatus.INCOMPLETE

    if verdict is CriticalControlVerdict.INCOMPLETE and status is AssessmentStatus.COMPLETE:
        if not containment_measured or critical_control_verdict is None:
            status = AssessmentStatus.INCOMPLETE

    # δ_C follows the containment verdict only. Assessment incompleteness is a
    # label (and drives measured_modules exclusion) — it must not re-discount.
    if verdict is CriticalControlVerdict.GATE_FAILED:
        effective = CriticalControlVerdict.GATE_FAILED
    elif verdict is CriticalControlVerdict.GATE_PASSED:
        effective = CriticalControlVerdict.GATE_PASSED
    else:
        effective = CriticalControlVerdict.INCOMPLETE

    _d_factor, delta_c = gate_factor(effective)

    uhqs = round(weighted * delta_c, 2)
    return UhqsComputation(
        scores=normalized,
        weights={k: float(weights[k]) for k in WEIGHT_KEYS},
        weighted_sum=round(weighted, 6),
        delta_c=delta_c,
        uhqs=uhqs,
        safety_gate_passed=verdict is CriticalControlVerdict.GATE_PASSED
        and status is AssessmentStatus.COMPLETE,
        containment_measured=containment_measured,
        assessment_status=status,
        critical_control_verdict=verdict,
        graded=True,
        measured_modules=dict(measured),
    )


def assessment_from_module_results(
    modules: Mapping[str, Any],
    *,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
) -> tuple[AssessmentStatus, CriticalControlVerdict]:
    """Derive assessment status / verdict from ModuleResult-like mappings.

    Status/verdict remain honest labels for the scorecard. They no longer
    suppress composite UHQS (see ``compute_uhqs``).
    """
    incomplete = False
    for key in ("A", "B", "C", "D", "E", "F"):
        mod = modules.get(key) or {}
        status = str(mod.get("status", "")).upper().replace(" ", "_")
        if mod.get("complete") is False:
            incomplete = True
        elif mod.get("complete") is not True and status in _INCOMPLETE_MODULE_STATUSES:
            incomplete = True
        coverage = mod.get("completeness") or {}
        if coverage.get("complete") is False:
            incomplete = True

    try:
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
            elif incomplete or raw_s in {
                "INCOMPLETE",
                "SKIPPED",
                "N/A",
                "NOT_RUN",
                "NOT_TESTED",
                "NOT_MEASURED",
                "ERROR",
            }:
                verdict = CriticalControlVerdict.INCOMPLETE
            else:
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
    except ValueError:
        verdict = CriticalControlVerdict.INCOMPLETE
        incomplete = True

    status_out = AssessmentStatus.INCOMPLETE if incomplete else AssessmentStatus.COMPLETE
    if verdict is CriticalControlVerdict.INCOMPLETE:
        status_out = AssessmentStatus.INCOMPLETE
    return status_out, verdict
