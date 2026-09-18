"""UHQS scoring helpers for UHBS v5 (CLI / scorecard validation).

Normative math lives in ``uhbs_core.uhqs_math`` — this module re-exports the
CLI-facing API and adds scorecard integrity checks.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from uhbs_core.uhqs_math import (
    PROFILE_WEIGHTS,
    SCORE_KEYS,
    SCORING_MODEL_ID,
    WEIGHT_KEYS,
    AssessmentStatus,
    CriticalControlVerdict,
    assessment_from_module_results,
    letter_grade,
    safety_gate,
    validate_weights,
    weights_for_class,
)
from uhbs_core.uhqs_math import (
    compute_uhqs as _compute_uhqs,
)

__all__ = [
    "PROFILE_WEIGHTS",
    "SCORE_KEYS",
    "SCORING_MODEL_ID",
    "WEIGHT_KEYS",
    "AssessmentStatus",
    "CriticalControlVerdict",
    "UhqsResult",
    "assert_scorecard_integrity",
    "compute_uhqs",
    "letter_grade",
    "safety_gate",
    "validate_weights",
    "weights_for_class",
]

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


@dataclass(frozen=True)
class UhqsResult:
    weighted_sum: float
    delta_c: float
    uhqs: float | None
    safety_gate_passed: bool
    assessment_status: str = AssessmentStatus.INCOMPLETE.value
    critical_control_verdict: str = CriticalControlVerdict.INCOMPLETE.value
    scoring_model_id: str = SCORING_MODEL_ID
    graded: bool = False


def compute_uhqs(
    scores: Mapping[str, float],
    weights: Mapping[str, float],
    *,
    assessment_status: AssessmentStatus | str = AssessmentStatus.COMPLETE,
    critical_control_verdict: CriticalControlVerdict | str | None = None,
    containment_measured: bool = True,
) -> UhqsResult:
    result = _compute_uhqs(
        scores,
        weights,
        assessment_status=assessment_status,
        critical_control_verdict=critical_control_verdict,
        containment_measured=containment_measured,
    )
    return UhqsResult(
        weighted_sum=result.weighted_sum,
        delta_c=result.delta_c,
        uhqs=result.uhqs,
        safety_gate_passed=result.safety_gate_passed,
        assessment_status=result.assessment_status.value,
        critical_control_verdict=result.critical_control_verdict.value,
        scoring_model_id=result.scoring_model_id,
        graded=result.graded,
    )


def assert_scorecard_integrity(
    scorecard: Mapping,
    *,
    uhqs_tol: float = 0.01,
    delta_tol: float = 0.0001,
) -> list[str]:
    """Recompute UHQS/δ_C/grade; return list of integrity errors (empty = OK)."""
    errors: list[str] = []
    modules = scorecard.get("modules") or {}
    weights = scorecard.get("weights")
    target = scorecard.get("target") or {}
    profile_class = target.get("class")

    if not weights and profile_class:
        weights = weights_for_class(str(profile_class))
    if not weights:
        return ["missing weights and target.class"]

    try:
        scores = {
            "A": float(modules["A"]["score"]),
            "B": float(modules["B"]["score"]),
            "C": float(modules["C"]["score"]),
            "D": float(modules["D"]["score"]),
            "E": float(modules["E"]["score"]),
            "F": float(modules["F"]["score"]),
        }
    except (KeyError, TypeError, ValueError) as exc:
        return [f"modules incomplete: {exc}"]

    model_id = scorecard.get("scoring_model_id")
    if model_id and model_id != SCORING_MODEL_ID:
        errors.append(
            f"scoring_model_id={model_id!r} != normative {SCORING_MODEL_ID!r}"
        )

    declared_status = scorecard.get("assessment_status")
    declared_verdict = scorecard.get("critical_control_verdict") or (
        (scorecard.get("safety_gate") or {}).get("critical_control_verdict")
    ) or ((modules.get("D") or {}).get("critical_control_verdict"))

    d_mod = modules.get("D") or {}
    containment_measured = bool(scorecard.get("containment_measured", True))
    if str(d_mod.get("status", "")).upper().replace(" ", "_") in {
        "SKIPPED",
        "N/A",
        "NOT_RUN",
        "INCOMPLETE",
        "NOT_TESTED",
        "NOT_MEASURED",
    }:
        containment_measured = False
    if scorecard.get("containment_measured") is False:
        containment_measured = False

    derived_status, verdict = assessment_from_module_results(
        modules, critical_control_verdict=declared_verdict
    )
    status = derived_status
    if declared_status:
        try:
            declared_as = AssessmentStatus(str(declared_status))
        except ValueError:
            errors.append(f"invalid assessment_status={declared_status!r}")
        else:
            if (
                declared_as is AssessmentStatus.COMPLETE
                and derived_status is AssessmentStatus.INCOMPLETE
            ):
                errors.append(
                    "assessment_status=COMPLETE but modules/verdict imply INCOMPLETE"
                )
            elif declared_as != derived_status:
                errors.append(
                    f"assessment_status={declared_as.value} != derived "
                    f"{derived_status.value}"
                )
            # Fail closed: any INCOMPLETE signal wins for recomputation.
            if (
                declared_as is AssessmentStatus.INCOMPLETE
                or derived_status is AssessmentStatus.INCOMPLETE
            ):
                status = AssessmentStatus.INCOMPLETE
            else:
                status = declared_as

    # Class→weight enforcement when both present
    if profile_class and profile_class in PROFILE_WEIGHTS:
        expected = PROFILE_WEIGHTS[profile_class]
        for k in WEIGHT_KEYS:
            if abs(float(weights[k]) - expected[k]) > 0.001:
                errors.append(
                    f"weights.{k}={weights[k]} does not match class {profile_class} "
                    f"(expected {expected[k]})"
                )

    result = _compute_uhqs(
        scores,
        weights,
        containment_measured=containment_measured,
        assessment_status=status,
        critical_control_verdict=verdict,
    )

    if "uhqs" in scorecard:
        declared_uhqs = scorecard.get("uhqs")
    else:
        declared_uhqs = None if result.uhqs is None else -1

    if result.uhqs is None:
        # Ungraded: INCOMPLETE or GATE_FAILED — uhqs/grade must be null or omitted.
        if "uhqs" in scorecard and declared_uhqs is not None:
            errors.append(f"uhqs={declared_uhqs!r} but recomputed ungraded (null)")
        declared_grade = scorecard.get("grade", None)
        if declared_grade is not None:
            errors.append(
                f"grade={declared_grade!r} present but assessment is ungraded "
                f"(status={result.assessment_status.value}, "
                f"verdict={result.critical_control_verdict.value})"
            )
    else:
        if "uhqs" not in scorecard:
            errors.append("uhqs missing for graded UHQS")
        else:
            try:
                declared_f = float(declared_uhqs)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                errors.append(f"uhqs={declared_uhqs!r} is not numeric")
            else:
                if abs(declared_f - result.uhqs) > uhqs_tol:
                    errors.append(f"uhqs={declared_f} != recomputed {result.uhqs}")

        declared_grade = scorecard.get("grade", None)
        expected_grade = letter_grade(result.uhqs)
        if declared_grade is None:
            errors.append(f"grade missing for graded UHQS (expected {expected_grade})")
        elif expected_grade and str(declared_grade) != expected_grade:
            errors.append(f"grade={declared_grade} != recomputed {expected_grade}")

    gate = scorecard.get("safety_gate") or {}
    if "delta_c" in gate and abs(float(gate["delta_c"]) - result.delta_c) > delta_tol:
        errors.append(f"safety_gate.delta_c={gate['delta_c']} != recomputed {result.delta_c}")
    if "passed" in gate and bool(gate["passed"]) != result.safety_gate_passed:
        errors.append(
            f"safety_gate.passed={gate['passed']} != recomputed {result.safety_gate_passed}"
        )
    if (
        result.graded
        and "containment_score" in gate
        and abs(float(gate["containment_score"]) - scores["D"]) > 0.01
    ):
        errors.append("safety_gate.containment_score != modules.D.score")

    gate_verdict = gate.get("critical_control_verdict")
    if gate_verdict and str(gate_verdict) != result.critical_control_verdict.value:
        errors.append(
            f"safety_gate.critical_control_verdict={gate_verdict!r} != "
            f"recomputed {result.critical_control_verdict.value}"
        )

    # Graded scorecards must not claim a grade while modules / critical verdict are incomplete.
    if result.graded:
        if result.critical_control_verdict is CriticalControlVerdict.INCOMPLETE:
            errors.append("graded scorecard with INCOMPLETE critical_control_verdict")
        if result.assessment_status is AssessmentStatus.INCOMPLETE:
            errors.append("graded scorecard with assessment_status=INCOMPLETE")
        for key in SCORE_KEYS:
            mod = modules.get(key) or {}
            status_s = str(mod.get("status", "")).upper().replace(" ", "_")
            if mod.get("complete") is False or status_s in _INCOMPLETE_MODULE_STATUSES:
                errors.append(f"graded scorecard with incomplete module {key}")
                break
        if str(d_mod.get("critical_control_verdict", "")).upper() == "INCOMPLETE":
            errors.append("graded scorecard with Module D critical_control_verdict=INCOMPLETE")

    return errors
