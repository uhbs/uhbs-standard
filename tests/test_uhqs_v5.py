"""UHQS v5 invariants, Module C/D regressions, and mutation guards."""

from __future__ import annotations

import json
from pathlib import Path

from uhbs_core.attack_validate import extract_technique_ids, resolve_technique
from uhbs_core.check_scoring import score_checks
from uhbs_core.models import CheckOutcome, CheckResult, module_completeness
from uhbs_core.telemetry.formats import validate_stix21
from uhbs_core.uhqs_math import (
    CriticalControlVerdict,
    compute_uhqs,
    letter_grade,
)


def test_not_applicable_leaves_denominator() -> None:
    checks = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(
            id="b",
            team="blue",
            outcome=CheckOutcome.NOT_APPLICABLE,
            score=0.0,
            applicability_rationale="not in profile",
            mandatory=False,
        ),
    ]
    assert score_checks(checks) == 100.0


def test_not_tested_stays_in_denominator_and_blocks_completeness() -> None:
    checks = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(id="b", team="blue", outcome=CheckOutcome.NOT_TESTED, score=0.0),
    ]
    # Near-zero log floor → essentially no earned credit from the untested check
    assert score_checks(checks) < 0.1
    assert module_completeness(checks)["complete"] is False


def test_not_tested_cannot_earn_credit() -> None:
    c = CheckResult(
        id="x",
        team="blue",
        outcome=CheckOutcome.NOT_TESTED,
        score=50.0,  # attempted skip-credit
    )
    assert c.score == 0.0


def test_adding_failure_cannot_improve_score() -> None:
    base = [
        CheckResult(id="a", team="blue", outcome=CheckOutcome.PASS, score=100.0),
        CheckResult(id="b", team="blue", outcome=CheckOutcome.PASS, score=100.0),
    ]
    worse = base + [
        CheckResult(id="c", team="blue", outcome=CheckOutcome.FAIL, score=0.0)
    ]
    assert score_checks(worse) < score_checks(base)


def test_stix_rejects_non_stix_types() -> None:
    ok, msg = validate_stix21({"type": "cowrie.session.connect"})
    assert not ok
    assert "unknown" in msg or "non-STIX" in msg or "type" in msg.lower()


def test_stix_accepts_indicator_with_spec() -> None:
    ok, _ = validate_stix21(
        {
            "type": "indicator",
            "id": "indicator--a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "spec_version": "2.1",
            "pattern": "[file:hashes.'SHA-256'='a']",
            "pattern_type": "stix",
            "valid_from": "2020-01-01T00:00:00Z",
        }
    )
    assert ok


def test_attack_keyword_is_not_a_technique_id() -> None:
    assert extract_technique_ids("this is an attack against the host") == []
    assert not resolve_technique("attack").valid


def test_attack_resolves_pinned_id() -> None:
    r = resolve_technique("T1059.004")
    assert r.valid
    assert not r.revoked


def test_gate_failed_null_uhqs_invariant() -> None:
    result = compute_uhqs(
        {"A": 100, "B": 100, "C": 100, "D": 0, "E": 100, "F": 100},
        profile_class="POSIX-Shell",
        critical_control_verdict=CriticalControlVerdict.GATE_FAILED,
    )
    assert result.uhqs is None
    assert letter_grade(result.uhqs) is None


def test_mutation_no_95_floor_in_safety_source() -> None:
    src = Path("src/uhbs_core/test_safety.py").read_text(encoding="utf-8")
    assert "score = max(score, 95" not in src
    assert "score = max(score, 95.0)" not in src


def test_mutation_no_c2_rescale_in_telemetry() -> None:
    src = Path("src/uhbs_core/test_telemetry.py").read_text(encoding="utf-8")
    assert "100.0 / 52" not in src
    assert "c2 * (100" not in src
    assert "* (100.0 / 52" not in src


def test_attack_pin_file_present() -> None:
    pin = json.loads(
        Path("src/uhbs_core/data/attack_pin.json").read_text(encoding="utf-8")
    )
    assert "T1041" in pin["techniques"]
