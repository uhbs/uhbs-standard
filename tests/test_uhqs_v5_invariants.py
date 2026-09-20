"""UHQS v5 scoring integrity invariants and regression guards."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from uhbs_core.check_scoring import score_checks, summarize_checks
from uhbs_core.models import CheckOutcome, CheckResult
from uhbs_core.telemetry.attack import validate_technique_id
from uhbs_core.telemetry.formats import validate_stix21
from uhbs_core.uhqs_math import (
    SCORING_MODEL_ID,
    AssessmentStatus,
    CriticalControlVerdict,
    compute_uhqs,
    letter_grade,
)


def _scores(**overrides: float) -> dict[str, float]:
    base = {"A": 80.0, "B": 80.0, "C": 80.0, "D": 100.0, "E": 80.0, "F": 80.0}
    base.update(overrides)
    return base


def test_scoring_model_id_is_pinned() -> None:
    assert SCORING_MODEL_ID == "uhqs-v5.0-critical-gate-diagnostic"


def test_incomplete_assessment_is_ungraded() -> None:
    result = compute_uhqs(
        _scores(),
        profile_class="POSIX-Shell",
        assessment_status=AssessmentStatus.INCOMPLETE,
    )
    assert result.uhqs is None
    assert result.graded is False
    assert letter_grade(result.uhqs) is None


def test_gate_failed_is_ungraded() -> None:
    result = compute_uhqs(
        _scores(D=0.0),
        profile_class="POSIX-Shell",
        critical_control_verdict=CriticalControlVerdict.GATE_FAILED,
    )
    assert result.uhqs is None
    assert result.safety_gate_passed is False
    assert result.critical_control_verdict is CriticalControlVerdict.GATE_FAILED


def test_gate_passed_publishes_weighted_sum() -> None:
    result = compute_uhqs(
        _scores(),
        profile_class="POSIX-Shell",
        critical_control_verdict=CriticalControlVerdict.GATE_PASSED,
    )
    assert result.uhqs == 80.0
    assert result.delta_c == 1.0
    assert result.graded is True


def test_adding_failure_cannot_improve_score() -> None:
    base = [
        CheckResult(id="a", team="blue", passed=True, score=100.0),
        CheckResult(id="b", team="blue", passed=True, score=100.0),
    ]
    worse = base + [CheckResult(id="c", team="blue", passed=False, score=0.0)]
    assert score_checks(worse) <= score_checks(base)


def test_omitting_mandatory_check_blocks_completeness() -> None:
    checks = [
        CheckResult.make(
            id="m1",
            team="blue",
            outcome=CheckOutcome.PASS,
            score=100.0,
            mandatory=True,
        ),
        CheckResult.make(
            id="m2",
            team="blue",
            outcome=CheckOutcome.NOT_TESTED,
            mandatory=True,
        ),
    ]
    agg = summarize_checks(checks)
    assert agg.complete is False
    assert agg.score == 0.0


def test_not_applicable_leaves_denominator() -> None:
    checks = [
        CheckResult.make(
            id="a",
            team="blue",
            outcome=CheckOutcome.PASS,
            score=100.0,
        ),
        CheckResult.make(
            id="b",
            team="blue",
            outcome=CheckOutcome.NOT_APPLICABLE,
            applicability_rationale="protocol lacks capability X",
            mandatory=True,
        ),
    ]
    assert score_checks(checks) == 100.0
    assert summarize_checks(checks).complete is True


def test_not_tested_never_earns_credit() -> None:
    c = CheckResult.make(
        id="x",
        team="blue",
        outcome=CheckOutcome.NOT_TESTED,
        score=50.0,  # forced to 0 in __post_init__
    )
    assert c.score == 0.0


def test_stix_rejects_non_stix_honeypot_type() -> None:
    ok, detail = validate_stix21({"type": "cowrie.session.connect"})
    assert ok is False
    assert "unknown" in detail.lower() or "type" in detail.lower()


def test_stix_accepts_minimal_indicator() -> None:
    ok, _ = validate_stix21(
        {
            "type": "indicator",
            "id": "indicator--11111111-1111-1111-1111-111111111111",
            "spec_version": "2.1",
            "pattern": "[file:hashes.'SHA-256' = 'a']",
            "pattern_type": "stix",
            "valid_from": "2020-01-01T00:00:00Z",
        }
    )
    assert ok is True


def test_attack_word_alone_is_not_a_technique() -> None:
    # validate_technique_id requires T#### shape
    rec = validate_technique_id("attack")
    assert rec.valid is False


def test_attack_known_technique_validates() -> None:
    rec = validate_technique_id("T1059.004")
    assert rec.valid is True


def test_mutation_restoring_skip_credit_would_fail_contract() -> None:
    """Guard: NOT_TESTED with positive score cannot survive CheckResult construction."""
    c = CheckResult(
        id="skip",
        team="white",
        outcome=CheckOutcome.NOT_TESTED,
        score=15.0,
    )
    assert c.score == 0.0


def test_v5_golden_incomplete_fixture() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "docs" / "conformance" / "fixtures" / "v5" / "incomplete-ungraded.scorecard.json"
    if not path.is_file():
        pytest.skip("v5 incomplete fixture not present")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("uhqs") is None
    assert data.get("grade") is None
    assert data.get("assessment_status") == "INCOMPLETE"
