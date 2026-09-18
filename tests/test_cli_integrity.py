"""CLI, integrity, and cross-package UHQS consistency tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from uhbs_cli.cli import main
from uhbs_cli.scoring import assert_scorecard_integrity, letter_grade, weights_for_class
from uhbs_cli.scoring import compute_uhqs as cli_compute
from uhbs_core.models import compute_uhqs as core_compute
from uhbs_core.uhqs_math import grade_for
from uhbs_core.uhqs_math import letter_grade as shared_letter

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "conformance" / "fixtures"
# Anonymous Low-Interaction worked example (NOT the live Cowrie fixture).
LI_WORKED_SCORES = {
    "A": 23.5,
    "B": 42.5,
    "C": 57.0,
    "D": 100.0,
    "E": 55.0,
    "F": 69.0,
}
LI_WORKED_DIMS = {
    "protocol": 23.5,
    "behavior": 42.5,
    "telemetry": 57.0,
    "containment": 100.0,
    "scale": 55.0,
    "static": 69.0,
}


def test_cli_and_core_uhqs_agree() -> None:
    weights = weights_for_class("Low-Interaction")
    cli = cli_compute(LI_WORKED_SCORES, weights)
    core = core_compute(LI_WORKED_DIMS, target="x", profile_class="Low-Interaction")
    assert cli.uhqs == core.uhqs == 46.97
    assert cli.delta_c == pytest.approx(core.delta_c)
    assert shared_letter(cli.uhqs) == letter_grade(cli.uhqs) == "F"
    assert grade_for(cli.uhqs).startswith("GRADE F")


def test_missing_module_score_raises() -> None:
    weights = weights_for_class("Low-Interaction")
    incomplete = {"A": 1, "B": 1, "C": 1, "E": 1, "F": 1}  # no D
    with pytest.raises(KeyError, match="Missing module scores"):
        cli_compute(incomplete, weights)
    with pytest.raises(KeyError, match="Missing module scores"):
        core_compute({"protocol": 1.0}, target="x")


def test_containment_not_measured_is_ungraded() -> None:
    """v5: unmeasured containment cannot pass the gate or invent a grade."""
    scores = {**LI_WORKED_DIMS, "containment": 10.0}
    gated = core_compute(
        scores,
        target="x",
        profile_class="Low-Interaction",
        critical_control_verdict="GATE_FAILED",
    )
    unmeasured = core_compute(
        scores,
        target="x",
        profile_class="Low-Interaction",
        containment_measured=False,
    )
    assert gated.uhqs is None
    assert unmeasured.uhqs is None
    assert unmeasured.delta_c == 0.0
    assert not unmeasured.graded


def test_integrity_detects_tampered_uhqs() -> None:
    data = json.loads((FIXTURES / "cowrie-low-interaction.scorecard.json").read_text())
    data["uhqs"] = 99.99
    errors = assert_scorecard_integrity(data)
    assert any("uhqs=" in e for e in errors)


def test_integrity_detects_tampered_grade() -> None:
    data = json.loads((FIXTURES / "cowrie-low-interaction.scorecard.json").read_text())
    data["grade"] = "A"
    errors = assert_scorecard_integrity(data)
    assert any("grade=" in e for e in errors)


def test_integrity_skipped_module_d_is_ungraded() -> None:
    data = json.loads((FIXTURES / "cowrie-low-interaction.scorecard.json").read_text())
    data["modules"]["D"] = {
        "score": 10.0,
        "status": "INCOMPLETE",
        "complete": False,
        "critical_control_verdict": "INCOMPLETE",
    }
    data["assessment_status"] = "INCOMPLETE"
    data["critical_control_verdict"] = "INCOMPLETE"
    data["containment_measured"] = False
    data["safety_gate"] = {
        "containment_score": 10.0,
        "delta_c": 0.0,
        "passed": False,
        "critical_control_verdict": "INCOMPLETE",
        "unauthorized_egress_leaks": 0,
    }
    data["uhqs"] = None
    data["grade"] = None
    errors = assert_scorecard_integrity(data)
    assert errors == [], errors


def test_cli_validate_scorecard_ok() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["validate-scorecard", str(FIXTURES / "cowrie-low-interaction.scorecard.json")],
    )
    assert result.exit_code == 0, result.output
    assert "OK" in result.output


def test_cli_validate_scorecard_fails_on_tamper(tmp_path: Path) -> None:
    data = json.loads((FIXTURES / "cowrie-low-interaction.scorecard.json").read_text())
    data["uhqs"] = 12.34
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["validate-scorecard", str(path)])
    assert result.exit_code == 1
    assert "integrity" in result.output


def test_cli_validate_profile_ok() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main, ["validate-profile", str(ROOT / "templates" / "profile.yaml")]
    )
    assert result.exit_code == 0, result.output


def test_cli_score_command() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("scores.json").write_text(json.dumps(LI_WORKED_SCORES), encoding="utf-8")
        result = runner.invoke(
            main, ["score", "--class", "Low-Interaction", "--scores", "scores.json"]
        )
    assert result.exit_code == 0, result.output
    assert "lab/sandbox evaluation of decoys" in result.output
    json_start = result.output.index("{")
    json_end = result.output.rindex("}") + 1
    payload = json.loads(result.output[json_start:json_end])
    assert payload["uhqs"] == 46.97
    assert payload["grade"] == "F"


def test_cli_prints_lab_sandbox_notice() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["validate-scorecard", str(FIXTURES / "cowrie-low-interaction.scorecard.json")],
    )
    assert result.exit_code == 0, result.output
    assert "UHBS/AEP are for lab/sandbox evaluation of decoys" in result.output
    assert "Do not run them against production or unauthorized real services" in result.output


def test_cli_lab_list_protocols() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["lab", "--list-protocols"])
    assert result.exit_code == 0, result.output
    assert "ssh" in result.output


def test_cli_command_tree_complete() -> None:
    """Registration side-effects must keep all top-level and nested commands."""
    assert sorted(main.list_commands(None)) == [
        "aep",
        "genai-bench",
        "lab",
        "matrix",
        "provenance",
        "score",
        "validate-evidence",
        "validate-profile",
        "validate-scorecard",
    ]
    aep = main.get_command(None, "aep")
    assert aep is not None
    assert sorted(aep.list_commands(None)) == [
        "analyze",
        "example",
        "init",
        "report",
        "slm",
        "validate",
        "validate-trials",
    ]
    slm = aep.get_command(None, "slm")
    assert slm is not None
    assert sorted(slm.list_commands(None)) == [
        "generate",
        "init",
        "status",
        "validate",
    ]
    for group_name, expected in (
        ("matrix", ["analyze", "example", "report", "validate"]),
        ("provenance", ["attach", "example", "summarize", "validate"]),
        ("genai-bench", ["analyze", "example", "stub"]),
    ):
        group = main.get_command(None, group_name)
        assert group is not None, group_name
        assert sorted(group.list_commands(None)) == expected
