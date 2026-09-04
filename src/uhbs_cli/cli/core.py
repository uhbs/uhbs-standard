"""Core UHBS CLI commands: validate, score, and lab shim."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from jsonschema import Draft202012Validator

from uhbs_cli import __version__
from uhbs_cli.scoring import (
    PROFILE_WEIGHTS,
    assert_scorecard_integrity,
    compute_uhqs,
    letter_grade,
    validate_weights,
    weights_for_class,
)
from uhbs_core.termui import echo_error, echo_ok

from .paths import _load_json, _load_schema, _load_yaml


@click.group()
@click.version_option(__version__, prog_name="uhbs")
@click.pass_context
def main(ctx: click.Context) -> None:
    """UHBS — validate profiles/scorecards and compute UHQS (lab/sandbox evaluation)."""
    # Show once per invocation when a subcommand runs (not for bare --help/--version).
    if ctx.invoked_subcommand is not None:
        from uhbs_core.notices import print_lab_sandbox_notice

        print_lab_sandbox_notice()

@main.command("validate-profile")
@click.argument("profile", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--strict/--no-strict",
    default=True,
    help="Enforce class→weight table match (default: on).",
)
def validate_profile(profile: Path, strict: bool) -> None:
    """Validate a TPS profile.yaml against the official schema."""
    data = _load_yaml(profile)
    schema = _load_schema("profile.schema.json")
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            loc = ".".join(str(p) for p in err.path) or "(root)"
            echo_error(f"ERROR {loc}: {err.message}")
        sys.exit(1)

    weights = data.get("module_weights", {})
    ok, total = validate_weights(weights)
    if not ok:
        echo_error(f"ERROR module_weights: sum is {total:.6f}, expected 1.000 (±0.001)")
        sys.exit(1)

    profile_class = (data.get("target_metadata") or {}).get("class")
    if strict and profile_class in PROFILE_WEIGHTS:
        expected = PROFILE_WEIGHTS[profile_class]
        for key in ("w_A", "w_B", "w_C", "w_E", "w_F"):
            if abs(float(weights[key]) - expected[key]) > 0.001:
                echo_error(
                    f"ERROR module_weights.{key}: {weights[key]} does not match "
                    f"class {profile_class} (expected {expected[key]})"
                )
                sys.exit(1)

    echo_ok(f"OK  {profile} — valid UHBS TPS profile (weights sum={total:.3f})")


@main.command("validate-scorecard")
@click.argument("scorecard", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--strict/--no-strict",
    default=True,
    help="Recompute UHQS/δ_C/grade and enforce class weights (default: on).",
)
def validate_scorecard(scorecard: Path, strict: bool) -> None:
    """Validate a scorecard JSON against the official schema."""
    data = _load_json(scorecard)
    schema = _load_schema("scorecard.schema.json")
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            loc = ".".join(str(p) for p in err.path) or "(root)"
            echo_error(f"ERROR {loc}: {err.message}")
        sys.exit(1)

    if strict:
        integrity = assert_scorecard_integrity(data)
        if integrity:
            for msg in integrity:
                echo_error(f"ERROR integrity: {msg}")
            sys.exit(1)

    echo_ok(f"OK  {scorecard} — valid UHBS scorecard (UHQS={data.get('uhqs')})")


@main.command("validate-evidence")
@click.argument("evidence", type=click.Path(exists=True, path_type=Path))
def validate_evidence(evidence: Path) -> None:
    """Validate an evidence pack against the official schema."""
    data = _load_json(evidence)
    schema = _load_schema("evidence-pack.schema.json")
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            loc = ".".join(str(p) for p in err.path) or "(root)"
            echo_error(f"ERROR {loc}: {err.message}")
        sys.exit(1)
    echo_ok(f"OK  {evidence} — valid UHBS evidence pack")


@main.command("score")
@click.option(
    "--profile",
    "profile_path",
    type=click.Path(exists=True, path_type=Path),
    help="TPS profile.yaml providing module weights.",
)
@click.option(
    "--class",
    "profile_class",
    type=click.Choice(sorted(PROFILE_WEIGHTS.keys())),
    help="Profile class (uses normative weight table when --profile omitted).",
)
@click.option(
    "--scores",
    "scores_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="JSON object with module scores A,B,C,D,E,F.",
)
def score_cmd(
    profile_path: Path | None,
    profile_class: str | None,
    scores_path: Path,
) -> None:
    """Compute UHQS from module scores and profile weights."""
    scores = _load_json(scores_path)
    if profile_path:
        profile = _load_yaml(profile_path)
        weights = profile["module_weights"]
        profile_class = (profile.get("target_metadata") or {}).get("class") or profile_class
    elif profile_class:
        weights = weights_for_class(profile_class)
    else:
        raise click.UsageError("Provide --profile or --class")

    result = compute_uhqs(scores=scores, weights=weights)
    click.echo(
        json.dumps(
            {
                "uhbs_version": __version__,
                "profile_class": profile_class,
                "delta_c": result.delta_c,
                "uhqs": result.uhqs,
                "grade": letter_grade(result.uhqs),
                "safety_gate_passed": result.safety_gate_passed,
                "weighted_sum": result.weighted_sum,
            },
            indent=2,
        )
    )


@main.command(
    "lab",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def lab_cmd(ctx: click.Context) -> None:
    """Run the UHBS-Lab reference harness (requires: pip install 'uhbs[lab]')."""
    try:
        from uhbs_core.run_benchmark import main as lab_main
    except ImportError as exc:  # pragma: no cover
        raise click.ClickException(
            "uhbs-core lab harness unavailable. Install with: pip install 'uhbs[lab]'"
        ) from exc
    raise SystemExit(lab_main(tuple(ctx.args)))

