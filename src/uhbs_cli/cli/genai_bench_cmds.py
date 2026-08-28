"""Click commands for experimental GenAI/MCP benchmark."""

from __future__ import annotations

import json
from pathlib import Path

import click

from uhbs_core.termui import echo_ok

from .core import main


@main.group("genai-bench")
def genai_bench_group() -> None:
    """Experimental GenAI/MCP benchmark — replay-first offline analysis.

    Default CI path is deterministic replay. Live probes are lab-only and are
    not exposed via uhbs-mcp. Does not change UHQS.
    """


@genai_bench_group.command("example")
@click.argument("name", type=click.Choice(["beginner", "advanced", "template"]))
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.option("--force/--no-force", default=False, show_default=True)
def genai_bench_example(name: str, out_dir: Path | None, force: bool) -> None:
    from uhbs_cli import genai_bench as gb

    target = out_dir or Path(f"genai-bench-{name}")
    try:
        written = gb.export_example_bundle(name, target, force=force)
    except gb.GenaiBenchError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote packaged example '{name}' to {written}")


@genai_bench_group.command("stub")
@click.option("--out", type=click.Path(path_type=Path), default=Path("replay.json"))
@click.option("--force/--no-force", default=False, show_default=True)
def genai_bench_stub(out: Path, force: bool) -> None:
    """Write a deterministic replay-buffer stub (CI-safe)."""
    from uhbs_cli import genai_bench as gb

    try:
        path = gb.write_stub_replay(out, force=force)
    except gb.GenaiBenchError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote replay stub {path}")


@genai_bench_group.command("analyze")
@click.argument("replay", type=click.Path(exists=True, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default=Path("genai-benchmark-report.json"))
def genai_bench_analyze(replay: Path, out: Path) -> None:
    """Analyze a replay buffer → experimental GenAI/MCP report."""
    from uhbs_cli import genai_bench as gb

    try:
        data = gb.load_replay(replay)
        report = gb.analyze_replay(data)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except gb.GenaiBenchError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote {out} (experimental; UHQS unchanged)")

