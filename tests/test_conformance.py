"""Conformance fixtures — UHQS always-grade golden vectors + migrated proofs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from uhbs_cli.scoring import (
    PROFILE_WEIGHTS,
    assert_scorecard_integrity,
)
from uhbs_core.uhqs_math import SCORING_MODEL_ID

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "conformance" / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "name,expected_uhqs,expected_grade",
    [
        ("cowrie-low-interaction.scorecard.json", 61.37, "D"),
        ("posix-shell-lab.scorecard.json", 80.33, "B"),
        ("echidra-low-interaction.scorecard.json", 36.58, "F"),
        ("v5/gate-passed-graded.scorecard.json", 90.0, "A"),
        ("safety-gate-fail.scorecard.json", 23.49, "F"),
        ("v5/gate-failed-ungraded.scorecard.json", 50.0, "D"),
        ("v5/incomplete-ungraded.scorecard.json", 42.75, "F"),
    ],
)
def test_conformance_fixture_integrity(
    name: str, expected_uhqs: float | None, expected_grade: str | None
) -> None:
    data = _load(name)
    assert data["uhqs"] == expected_uhqs
    assert data["grade"] == expected_grade
    assert data["scoring_model_id"] == SCORING_MODEL_ID
    errors = assert_scorecard_integrity(data)
    assert errors == [], errors


def test_all_fixtures_integrity() -> None:
    failures: list[str] = []
    for path in sorted(FIXTURES.rglob("*.scorecard.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = assert_scorecard_integrity(data)
        if errors:
            failures.append(f"{path.relative_to(FIXTURES)}: {errors}")
    assert failures == [], "\n".join(failures)


def test_cowrie_matches_low_interaction_weights() -> None:
    data = _load("cowrie-low-interaction.scorecard.json")
    expected = PROFILE_WEIGHTS["Low-Interaction"]
    for key, val in expected.items():
        assert abs(data["weights"][key] - val) < 1e-9


def test_posix_lab_meets_production_baseline() -> None:
    data = _load("posix-shell-lab.scorecard.json")
    assert data["uhqs"] is not None and data["uhqs"] >= 80
    assert data["grade"] == "B"
    assert data["critical_control_verdict"] == "GATE_PASSED"


def test_gate_factor_fixtures_still_have_letter_grade() -> None:
    for name in (
        "v5/incomplete-ungraded.scorecard.json",
        "v5/gate-failed-ungraded.scorecard.json",
        "safety-gate-fail.scorecard.json",
    ):
        data = _load(name)
        assert data["uhqs"] is not None
        assert data["grade"] in {"A", "B", "C", "D", "F"}
