"""UHBS Advanced Evidence Profile (AEP) — offline analysis only.

This package parses local experiment manifests and trial JSONL, computes
informative metrics (VoD, FSV, DTDR, EER), and renders addenda. It must never
import sockets, HTTP clients, SSH libraries, subprocess, Docker SDKs, protocol
plugins, or uhbs-lab.
"""

from __future__ import annotations

from .analyze import AnalyzeConfig, analyze
from .constants import AEP_VERSION, ARMS, FSV_LAYERS, UHBS_VERSION
from .errors import AepError
from .io import _schema_dir as _schema_dir
from .io import load_json, load_schema, load_yaml, packaged_data_dir
from .metrics import compute_dtdr, compute_eer, compute_fsv, compute_vod
from .render import render_markdown
from .stats import bootstrap_ci, kaplan_meier_median
from .templates import (
    EXAMPLE_BUNDLES,
    default_experiment_template,
    example_trial_line,
    export_example_bundle,
    write_init_bundle,
)
from .validate import (
    load_trials_jsonl,
    reject_forbidden_cli_values,
    validate_experiment,
    validate_schema,
    validate_trials,
)

__all__ = [
    "AEP_VERSION",
    "ARMS",
    "AepError",
    "AnalyzeConfig",
    "EXAMPLE_BUNDLES",
    "FSV_LAYERS",
    "UHBS_VERSION",
    "analyze",
    "bootstrap_ci",
    "compute_dtdr",
    "compute_eer",
    "compute_fsv",
    "compute_vod",
    "default_experiment_template",
    "example_trial_line",
    "export_example_bundle",
    "kaplan_meier_median",
    "load_json",
    "load_schema",
    "load_trials_jsonl",
    "load_yaml",
    "packaged_data_dir",
    "reject_forbidden_cli_values",
    "render_markdown",
    "validate_experiment",
    "validate_schema",
    "validate_trials",
    "write_init_bundle",
]
