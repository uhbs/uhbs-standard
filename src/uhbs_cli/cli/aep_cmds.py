"""Click commands for Advanced Evidence Profile (AEP)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from uhbs_cli.scoring import PROFILE_WEIGHTS
from uhbs_core.termui import echo_error, echo_info, echo_ok, echo_warn

from .core import main


@main.group("aep")
def aep_group() -> None:
    """Advanced Evidence Profile — offline analysis only (optional).

    Requires local experiment/trial files. Never launches attacks, probes,
    containers, or network connections. Does not change UHQS.
    """


@aep_group.command("init")
@click.option("--name", default="aep-experiment", show_default=True)
@click.option(
    "--class",
    "profile_class",
    type=click.Choice(sorted(PROFILE_WEIGHTS.keys())),
    default="Web-API",
    show_default=True,
)
@click.option("--trials", default=5, show_default=True, type=click.IntRange(min=1))
@click.option("--seed", default=42, show_default=True, type=int)
@click.option(
    "--out",
    "out_dir",
    type=click.Path(path_type=Path),
    default=Path("aep-experiment"),
    show_default=True,
)
@click.option(
    "--force/--no-force",
    default=False,
    show_default=True,
    help="Overwrite existing experiment.yaml / trials.jsonl in --out.",
)
def aep_init(
    name: str,
    profile_class: str,
    trials: int,
    seed: int,
    out_dir: Path,
    force: bool,
) -> None:
    """Create an experiment manifest + synthetic trial template (local files)."""
    from uhbs_cli import aep as aep_mod

    try:
        aep_mod.reject_forbidden_cli_values(name, str(out_dir))
        paths = aep_mod.write_init_bundle(
            out_dir,
            name=name,
            profile_class=profile_class,
            trials=trials,
            seed=seed,
            force=force,
        )
    except aep_mod.AepError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote {paths['experiment']}")
    echo_ok(f"OK  wrote {paths['trials']}")
    echo_ok(f"OK  wrote {paths['readme']}")
    echo_warn("AEP is offline analysis only — replace synthetic trials before publishing.")


@aep_group.command("example")
@click.argument("name", type=click.Choice(["beginner", "advanced", "template"]))
@click.option(
    "--out",
    "out_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Destination directory (default: ./aep-<name>).",
)
@click.option(
    "--force/--no-force",
    default=False,
    show_default=True,
    help="Overwrite existing files in --out.",
)
def aep_example(name: str, out_dir: Path | None, force: bool) -> None:
    """Copy a packaged synthetic AEP example (works after pip install)."""
    from uhbs_cli import aep as aep_mod

    target = out_dir or Path(f"aep-{name}")
    try:
        aep_mod.reject_forbidden_cli_values(str(target))
        written = aep_mod.export_example_bundle(name, target, force=force)
    except aep_mod.AepError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote packaged example '{name}' to {written}")
    echo_info("Next: uhbs aep validate experiment.yaml  (from that directory)")


@aep_group.command("validate")
@click.argument("experiment", type=click.Path(exists=True, path_type=Path))
@click.option("--strict/--no-strict", default=True, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable result.")
def aep_validate(experiment: Path, strict: bool, as_json: bool) -> None:
    """Validate an AEP experiment manifest."""
    from uhbs_cli import aep as aep_mod

    try:
        aep_mod.reject_forbidden_cli_values(str(experiment))
        data = aep_mod.load_yaml(experiment)
        errors = aep_mod.validate_experiment(data, strict=strict)
    except aep_mod.AepError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    elif errors:
        for err in errors:
            echo_error(f"ERROR {err}")
        sys.exit(1)
    else:
        echo_ok(f"OK  {experiment} — valid AEP experiment manifest")
    if errors:
        sys.exit(1)


@aep_group.command("validate-trials")
@click.argument("trials", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--experiment",
    "experiment_path",
    type=click.Path(exists=True, path_type=Path),
    help="Optional experiment manifest for cross-checks.",
)
@click.option("--strict/--no-strict", default=True, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def aep_validate_trials(
    trials: Path,
    experiment_path: Path | None,
    strict: bool,
    as_json: bool,
) -> None:
    """Validate AEP trial events (JSONL)."""
    from uhbs_cli import aep as aep_mod

    try:
        aep_mod.reject_forbidden_cli_values(
            str(trials), str(experiment_path) if experiment_path else None
        )
        rows = aep_mod.load_trials_jsonl(trials)
        experiment = aep_mod.load_yaml(experiment_path) if experiment_path else None
        errors = aep_mod.validate_trials(rows, experiment, strict=strict)
    except aep_mod.AepError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(
            json.dumps({"ok": not errors, "n": len(rows), "errors": errors}, indent=2)
        )
    elif errors:
        for err in errors:
            echo_error(f"ERROR {err}")
        sys.exit(1)
    else:
        echo_ok(f"OK  {trials} — {len(rows)} valid AEP trial event(s)")
    if errors:
        sys.exit(1)


@aep_group.command("analyze")
@click.option(
    "--experiment",
    "experiment_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--trials",
    "trials_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--scorecard",
    "scorecard_path",
    type=click.Path(exists=True, path_type=Path),
    help="Optional local scorecard path (linked only; never mutated).",
)
@click.option("--bootstrap-samples", default=1000, show_default=True, type=click.IntRange(min=0))
@click.option("--confidence", default=0.95, show_default=True, type=float)
@click.option("--seed", default=42, show_default=True, type=int)
@click.option(
    "--out",
    "out_path",
    type=click.Path(path_type=Path),
    default=Path("advanced-evidence.json"),
    show_default=True,
)
def aep_analyze(
    experiment_path: Path,
    trials_path: Path,
    scorecard_path: Path | None,
    bootstrap_samples: int,
    confidence: float,
    seed: int,
    out_path: Path,
) -> None:
    """Compute informative AEP metrics from local evidence files."""
    from uhbs_cli import aep as aep_mod

    try:
        aep_mod.reject_forbidden_cli_values(
            str(experiment_path),
            str(trials_path),
            str(scorecard_path) if scorecard_path else None,
            str(out_path),
        )
        if not (0.0 < confidence < 1.0):
            raise aep_mod.AepError("--confidence must be between 0 and 1 (exclusive)")
        experiment = aep_mod.load_yaml(experiment_path)
        exp_errors = aep_mod.validate_experiment(experiment, strict=True)
        if exp_errors:
            for err in exp_errors:
                echo_error(f"ERROR experiment: {err}")
            sys.exit(1)
        rows = aep_mod.load_trials_jsonl(trials_path)
        trial_errors = aep_mod.validate_trials(rows, experiment, strict=True)
        if trial_errors:
            for err in trial_errors:
                echo_error(f"ERROR trials: {err}")
            sys.exit(1)
        if scorecard_path is not None:
            # Ensure scorecard exists and looks like UHBS scorecard JSON; do not mutate.
            scorecard = aep_mod.load_json(scorecard_path)
            if not isinstance(scorecard, dict) or "uhqs" not in scorecard:
                raise aep_mod.AepError(
                    f"{scorecard_path}: --scorecard must be a UHBS scorecard JSON "
                    "object containing uhqs (AEP never mutates it)"
                )
        result = aep_mod.analyze(
            experiment,
            rows,
            config=aep_mod.AnalyzeConfig(
                bootstrap_samples=bootstrap_samples,
                confidence=confidence,
                seed=seed,
                experiment_path=str(experiment_path),
                trials_path=str(trials_path),
                scorecard_ref=str(scorecard_path) if scorecard_path else None,
            ),
        )
        schema_errors = aep_mod.validate_schema(result, "advanced-evidence.schema.json")
        if schema_errors:
            for err in schema_errors:
                echo_error(f"ERROR output schema: {err}")
            sys.exit(1)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
            fh.write("\n")
    except aep_mod.AepError as exc:
        raise click.ClickException(str(exc)) from exc

    echo_ok(f"OK  wrote {out_path}")
    echo_info(
        f"status={result['status']} control={result['control_status']} "
        f"warnings={len(result.get('warnings') or [])}"
    )
    echo_info("UHQS unchanged — AEP writes a separate evidence addendum only.")


@aep_group.command("report")
@click.argument("evidence", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "markdown"]),
    default="markdown",
    show_default=True,
)
@click.option(
    "--include-methodology/--no-include-methodology",
    default=True,
    show_default=True,
)
@click.option(
    "--out",
    "out_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Output path (default: stdout for markdown; required for json overwrite).",
)
def aep_report(
    evidence: Path,
    fmt: str,
    include_methodology: bool,
    out_path: Path | None,
) -> None:
    """Render an Advanced Evidence Addendum from analysis JSON."""
    from uhbs_cli import aep as aep_mod

    try:
        aep_mod.reject_forbidden_cli_values(
            str(evidence), str(out_path) if out_path else None
        )
        data = aep_mod.load_json(evidence)
        errors = aep_mod.validate_schema(data, "advanced-evidence.schema.json")
        if errors:
            for err in errors:
                echo_error(f"ERROR {err}")
            sys.exit(1)
        if fmt == "json":
            text = json.dumps(data, indent=2, sort_keys=True) + "\n"
            target = out_path or Path("advanced-evidence.json")
        else:
            text = aep_mod.render_markdown(
                data, include_methodology=include_methodology
            )
            target = out_path
            if target is None:
                click.echo(text, nl=False)
                return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        echo_ok(f"OK  wrote {target}")
    except aep_mod.AepError as exc:
        raise click.ClickException(str(exc)) from exc

