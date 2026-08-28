"""Click commands for experimental host provenance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from uhbs_core.termui import echo_error, echo_ok

from .core import main


@main.group("provenance")
def provenance_group() -> None:
    """Experimental host provenance — validate/summarize collector exports.

    Collector-neutral; rate-limits before hashing. Does not change UHQS.
    Does not load eBPF or expose via MCP.
    """


@provenance_group.command("example")
@click.argument("name", type=click.Choice(["beginner", "advanced", "template"]))
@click.option("--out", "out_dir", type=click.Path(path_type=Path), default=None)
@click.option("--force/--no-force", default=False, show_default=True)
def provenance_example(name: str, out_dir: Path | None, force: bool) -> None:
    from uhbs_cli import provenance as prov_mod

    target = out_dir or Path(f"provenance-{name}")
    try:
        written = prov_mod.export_example_bundle(name, target, force=force)
    except prov_mod.ProvenanceError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote packaged example '{name}' to {written}")


@provenance_group.command("summarize")
@click.argument("events", type=click.Path(exists=True, path_type=Path))
@click.option("--collector", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--max-events", default=5000, show_default=True, type=int)
@click.option("--max-bytes", default=2_000_000, show_default=True, type=int)
@click.option(
    "--aggregation",
    type=click.Choice(["none", "by_type", "ring_buffer"]),
    default="by_type",
    show_default=True,
)
@click.option("--platform", default=None, help="e.g. linux (others → not_applicable)")
@click.option("--out", type=click.Path(path_type=Path), default=Path("provenance-summary.json"))
def provenance_summarize(
    events: Path,
    collector: Path | None,
    max_events: int,
    max_bytes: int,
    aggregation: str,
    platform: str | None,
    out: Path,
) -> None:
    """Summarize JSONL events with rate limits, then hash."""
    from uhbs_cli import provenance as prov_mod

    try:
        rows = prov_mod.load_events_jsonl(events)
        col = None
        if collector:
            with collector.open(encoding="utf-8") as fh:
                col = json.load(fh)
        report = prov_mod.summarize_events(
            rows,
            collector=col,
            max_events=max_events,
            max_bytes=max_bytes,
            aggregation=aggregation,
            platform=platform or (col or {}).get("platform"),
        )
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except prov_mod.ProvenanceError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(
        f"OK  wrote {out} (accepted={report['summary']['accepted']} "
        f"dropped={report['summary']['dropped']})"
    )


@provenance_group.command("validate")
@click.argument("summary", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True)
def provenance_validate(summary: Path, as_json: bool) -> None:
    from uhbs_cli import provenance as prov_mod

    try:
        with summary.open(encoding="utf-8") as fh:
            report = json.load(fh)
        errors = prov_mod.validate_report(report)
    except prov_mod.ProvenanceError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    elif errors:
        for err in errors:
            echo_error(f"ERROR {err}")
        sys.exit(1)
    else:
        echo_ok(f"OK  {summary} — valid experimental provenance summary")
    if errors:
        sys.exit(1)


@provenance_group.command("attach")
@click.argument("summary", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--manifest",
    type=click.Path(path_type=Path),
    required=True,
    help="MANIFEST.json to update (created if missing).",
)
@click.option("--out", type=click.Path(path_type=Path), default=None)
def provenance_attach(summary: Path, manifest: Path, out: Path | None) -> None:
    """Attach provenance digest refs into MANIFEST.json."""
    from uhbs_cli import provenance as prov_mod

    try:
        with summary.open(encoding="utf-8") as fh:
            report = json.load(fh)
        errors = prov_mod.validate_report(report)
        if errors:
            raise prov_mod.ProvenanceError("; ".join(errors[:5]))
        updated = prov_mod.attach_digest_to_manifest(manifest, report)
        dest = out or manifest
        dest.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    except prov_mod.ProvenanceError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote {dest}")

