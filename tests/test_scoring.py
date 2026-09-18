"""Unit tests for UHQS v5 scoring."""

from uhbs_cli.scoring import compute_uhqs, letter_grade, safety_gate, validate_weights
from uhbs_core.uhqs_math import SCORING_MODEL_ID, CriticalControlVerdict


def test_posix_weights_sum() -> None:
    weights = {"w_A": 0.20, "w_B": 0.25, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20}
    ok, total = validate_weights(weights)
    assert ok
    assert abs(total - 1.0) < 1e-9


def test_safety_gate_pass_with_verdict() -> None:
    delta, passed = safety_gate(
        40, critical_control_verdict=CriticalControlVerdict.GATE_PASSED
    )
    assert passed
    assert delta == 1.0


def test_safety_gate_fail_binary() -> None:
    delta, passed = safety_gate(
        70, critical_control_verdict=CriticalControlVerdict.GATE_FAILED
    )
    assert not passed
    assert delta == 0.0


def test_gate_passed_uhqs_is_weighted_sum() -> None:
    weights = {"w_A": 0.20, "w_B": 0.25, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20}
    scores = {"A": 88, "B": 94, "C": 98, "D": 97, "E": 88, "F": 91}
    result = compute_uhqs(
        scores,
        weights,
        critical_control_verdict=CriticalControlVerdict.GATE_PASSED,
    )
    assert result.safety_gate_passed
    assert result.delta_c == 1.0
    assert result.uhqs == 92.1
    assert letter_grade(result.uhqs) == "A"
    assert result.graded
    assert result.scoring_model_id == SCORING_MODEL_ID


def test_gate_failed_is_ungraded() -> None:
    weights = {"w_A": 0.20, "w_B": 0.25, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20}
    scores = {"A": 100, "B": 100, "C": 100, "D": 70, "E": 100, "F": 100}
    result = compute_uhqs(
        scores,
        weights,
        critical_control_verdict=CriticalControlVerdict.GATE_FAILED,
    )
    assert result.uhqs is None
    assert letter_grade(result.uhqs) is None
    assert not result.graded


def test_incomplete_is_ungraded() -> None:
    weights = {"w_A": 0.20, "w_B": 0.25, "w_C": 0.20, "w_E": 0.15, "w_F": 0.20}
    scores = {"A": 100, "B": 100, "C": 100, "D": 100, "E": 100, "F": 100}
    result = compute_uhqs(
        scores,
        weights,
        assessment_status="INCOMPLETE",
        critical_control_verdict=CriticalControlVerdict.GATE_PASSED,
    )
    assert result.uhqs is None
    assert not result.graded
