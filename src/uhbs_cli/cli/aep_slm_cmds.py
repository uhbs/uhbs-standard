"""Click commands for AEP SLM (alpha, opt-in)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from uhbs_core.termui import echo_error, echo_info, echo_ok, echo_warn

from .aep_cmds import aep_group


@aep_group.group("slm")
def aep_slm_group() -> None:
    """Alpha SLM evaluator for AEP trials (opt-in; disabled by default).

    Not activated until you edit a local aep-slm.yaml (enabled + unlock phrase
    + attestations). Does not change UHQS. Lab/sandbox only.
    """


@aep_slm_group.command("init")
@click.option(
    "--out",
    "out_path",
    type=click.Path(path_type=Path),
    default=Path("aep-slm.yaml"),
    show_default=True,
    help="Path for the disabled-by-default alpha config.",
)
@click.option(
    "--experiment",
    "experiment_path",
    default="experiment.yaml",
    show_default=True,
    help="Relative/local path recorded under paths.experiment.",
)
@click.option(
    "--force/--no-force",
    default=False,
    show_default=True,
    help="Overwrite an existing config file.",
)
def aep_slm_init(out_path: Path, experiment_path: str, force: bool) -> None:
    """Write a disabled alpha SLM config (must edit file to activate)."""
    from uhbs_cli import aep_slm as slm

    try:
        path = slm.write_init_config(
            out_path, force=force, experiment_path=experiment_path
        )
    except slm.AepSlmError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote {path}")
    echo_warn(
        "AEP SLM is ALPHA and DISABLED. Edit the YAML (enabled, unlock_phrase, "
        "activation.*) before uhbs aep slm generate."
    )


@aep_slm_group.command("validate")
@click.argument("config", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--require-unlocked/--allow-locked",
    default=False,
    show_default=True,
    help="Fail if activation gates are not fully unlocked.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable status.")
def aep_slm_validate(config: Path, require_unlocked: bool, as_json: bool) -> None:
    """Validate an aep-slm.yaml and report whether generation is unlocked."""
    from uhbs_cli import aep_slm as slm

    try:
        data = slm.load_config(config)
        errors = slm.validate_config(data, require_unlocked=require_unlocked)
        report = slm.status_report(data)
    except slm.AepSlmError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(json.dumps(report, indent=2, sort_keys=True))
    else:
        if report["schema_ok"]:
            echo_ok("OK  schema")
        else:
            for err in report["schema_errors"]:
                echo_error(f"ERROR {err}")
        if report["unlocked"]:
            echo_ok("OK  activation unlocked (generate permitted)")
        else:
            echo_warn("LOCKED  generation blocked until you edit the config:")
            for blocker in report["activation_blockers"]:
                echo_warn(f"  - {blocker}")
        echo_info("UHQS unchanged — SLM output is AEP trial evidence only.")
    if errors:
        sys.exit(1)


@aep_slm_group.command("status")
@click.argument("config", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True)
def aep_slm_status(config: Path, as_json: bool) -> None:
    """Show activation status for an alpha SLM config (never runs a model)."""
    from uhbs_cli import aep_slm as slm

    try:
        data = slm.load_config(config)
        report = slm.status_report(data)
    except slm.AepSlmError as exc:
        raise click.ClickException(str(exc)) from exc
    if as_json:
        click.echo(json.dumps(report, indent=2, sort_keys=True))
        return
    echo_info(f"status={report['status']} provider={report['provider']}")
    echo_info(f"enabled={report['enabled']} unlocked={report['unlocked']}")
    if report["activation_blockers"]:
        echo_warn("Activation blockers:")
        for blocker in report["activation_blockers"]:
            echo_warn(f"  - {blocker}")
    else:
        echo_ok("No activation blockers")
    if report["schema_errors"]:
        for err in report["schema_errors"]:
            echo_error(f"ERROR {err}")
        sys.exit(1)


@aep_slm_group.command("generate")
@click.argument("config", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--force/--no-force",
    default=False,
    show_default=True,
    help="Overwrite existing output_trials / output_run paths.",
)
def aep_slm_generate(config: Path, force: bool) -> None:
    """Generate AEP trials from an unlocked alpha SLM config.

    Refuses default/locked configs. Lab/sandbox only. Does not change UHQS.
    """
    from uhbs_cli import aep_slm as slm

    try:
        data = slm.load_config(config)
        result = slm.generate_trials(data, config_path=config, force=force)
    except slm.AepSlmError as exc:
        raise click.ClickException(str(exc)) from exc
    echo_ok(f"OK  wrote {result['trials_path']} ({result['trial_count']} trials)")
    echo_ok(f"OK  wrote {result['run_path']}")
    echo_warn(
        "Next (offline): uhbs aep validate-trials … && uhbs aep analyze … "
        "(UHQS unchanged)"
    )

