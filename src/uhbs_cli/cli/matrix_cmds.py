"""Click commands for experimental five-dimension matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from uhbs_core.termui import echo_error, echo_ok

from .core import main


@main.group("matrix")
def matrix_group() -> None:
    """Experimental five-dimension matrix — offline informative analysis.

    Does not change UHQS, weights, or δ_C. Missing dimensions stay missing.
    """


@matrix_group.command("example")
@click.argument("name", type=click.Choice(["beginner", "advanced", "template"]))
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.option("--force/--no-force", default=False, show_default=True)
def matrix_example(name: str, out_dir: Path | None, force: bool) -> None:
    """Copy a packaged matrix example (works after pip install)."""
    from uhbs_cli import matrix as matrix_mod

    target = out_dir or Path(f"matrix-{name}")
    try:
        written = matrix_mod.export_example_bundle(name, target, force=force)
    except matrix_mod.MatrixError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote packaged example '{name}' to {written}")


@matrix_group.command("validate")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True)
def matrix_validate(input_path: Path, as_json: bool) -> None:
    """Validate a matrix input document."""
    from uhbs_cli import matrix as matrix_mod

    try:
        data = matrix_mod.load_json(input_path)
        errors = matrix_mod.validate_input(data)
    except matrix_mod.MatrixError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    elif errors:
        for err in errors:
            echo_error(f"ERROR {err}")
        sys.exit(1)
    else:
        echo_ok(f"OK  {input_path} — valid experimental matrix input")
    if errors:
        sys.exit(1)


@matrix_group.command("analyze")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default=Path("matrix-report.json"))
def matrix_analyze(input_path: Path, out: Path) -> None:
    """Analyze matrix input → experimental report (UHQS unchanged)."""
    from uhbs_cli import matrix as matrix_mod

    try:
        data = matrix_mod.load_json(input_path)
        report = matrix_mod.analyze(data)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except matrix_mod.MatrixError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote {out} (experimental; UHQS unchanged)")


@matrix_group.command("report")
@click.argument("report_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    show_default=True,
)
@click.option("--out", type=click.Path(path_type=Path), default=None)
def matrix_report(report_path: Path, fmt: str, out: Path | None) -> None:
    """Render an experimental matrix report."""
    from uhbs_cli import matrix as matrix_mod

    try:
        report = matrix_mod.load_json(report_path)
        errors = matrix_mod.validate_report(report)
        if errors:
            raise matrix_mod.MatrixError("; ".join(errors[:5]))
        text = (
            json.dumps(report, indent=2) + "\n"
            if fmt == "json"
            else matrix_mod.render_markdown(report)
        )
    except matrix_mod.MatrixError as exc:
        raise click.ClickException(str(exc)) from exc
    if out:
        out.write_text(text, encoding="utf-8")
        echo_ok(f"OK  wrote {out}")
    else:
        click.echo(text, nl=not text.endswith("\n"))

