"""AEP experiment/trial templates and bundle writers."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from .constants import AEP_VERSION, UHBS_VERSION
from .errors import AepError
from .io import packaged_data_dir


def default_experiment_template(
    *,
    name: str,
    profile_class: str,
    trials: int,
    seed: int,
) -> dict[str, Any]:
    exp_id = re.sub(r"[^A-Za-z0-9._:-]+", "-", name.strip())[:64] or "aep-experiment"
    return {
        "aep_version": AEP_VERSION,
        "uhbs_version": UHBS_VERSION,
        "experiment_id": exp_id,
        "name": name,
        "hypothesis": (
            "Under matched task/budget/timeout, the decoy changes dwell time "
            "and/or defender utility relative to a matched reference."
        ),
        "primary_outcome": "dtdr",
        "secondary_outcomes": ["vod", "eer", "fsv"],
        "profile_class": profile_class,
        "arms": {
            "decoy": {"name": "decoy-under-test", "version": "0.0.0", "digest": ""},
            "reference": {
                "name": "matched-reference",
                "version": "0.0.0",
                "digest": "",
            },
            "evaluator_control": {
                "name": "capability-check",
                "version": "0.0.0",
                "digest": "",
            },
        },
        "attacker_capability_tier": "scripted",
        "task": {
            "description": "Complete the declared recon/exploitation task.",
            "starting_knowledge": "Shared starter brief for all arms.",
            "success_criteria": "Task completion or timeout.",
        },
        "budget": {
            "max_attempts": 20,
            "max_unique_capabilities": 10,
            "currency_unit": "USD",
        },
        "timeout_seconds": 600,
        "randomization": {
            "method": "shuffled_blocks",
            "seed": seed,
            "notes": "Declare the seed used when assigning trial order.",
        },
        "repetitions": {
            "planned_per_arm": trials,
            # Keep minimum ≤ planned so `uhbs aep init --trials N` is immediately valid.
            "minimum_per_arm": max(1, min(trials, 5)),
        },
        "utility": {
            "name": "simple-defender-utility",
            "formula": (
                "U_D = w_detection*detection + w_intel*intelligence_yield "
                "- w_def_cost*defender_infra_cost"
            ),
            "weights": {
                "detection": 1.0,
                "intelligence_yield": 0.5,
                "defender_infra_cost": -0.1,
            },
            "notes": "Replace with study-specific utilities. Never use UHQS.",
        },
        "ethics": {
            "human_subjects": False,
            "consent_attested": False,
            "privacy_minimization": "Use subject pseudonyms only.",
        },
        "attestations": {
            "sandbox_only": True,
            "no_production_assets": True,
            "local_evidence_only": True,
            "informative_only": True,
            "notes": "AEP analyzes local files only; it never launches attacks.",
        },
        "notes": "Fill digests and versions before publishing results.",
    }


def example_trial_line(
    *,
    experiment_id: str,
    trial_id: str,
    arm: str,
    duration: float,
    censored: bool = False,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "aep_version": AEP_VERSION,
        "experiment_id": experiment_id,
        "trial_id": trial_id,
        "subject_pseudonym": "synth-01",
        "arm": arm,
        "started_at": "2026-01-01T00:00:00Z",
        "ended_at": "2026-01-01T00:10:00Z",
        "censored": censored,
        "session_duration_seconds": duration,
        "exchanges": 5,
        "attempts": 3,
        "unique_tools": ["nmap"],
        "unique_credentials": [],
        "unique_payload_families": [],
        "attack_technique_ids": ["T1595"],
        "detector": {
            "layer": "protocol",
            "predicted_decoy": arm == "decoy",
            "actual_is_decoy": arm == "decoy",
            "confidence": 0.8,
        },
        "defender_outcomes": {
            "prevented_compromise": True,
            "detection": True,
            "intelligence_yield": 1.0,
        },
        "costs": {
            "attacker_time_seconds": duration,
            "defender_time_seconds": 30,
            "attacker_token_cost": 0,
            "defender_infra_cost": 1.0,
            "currency_unit": "USD",
        },
        "raw_evidence_sha256": "0" * 64,
        "notes": "Template row — replace with measured values.",
    }
    if arm == "evaluator_control":
        row["evaluator_control_passed"] = True
    return row


def write_init_bundle(
    out_dir: Path,
    *,
    name: str,
    profile_class: str,
    trials: int,
    seed: int,
    force: bool = False,
) -> dict[str, Path]:
    out_dir = Path(out_dir)
    exp_path = out_dir / "experiment.yaml"
    trials_path = out_dir / "trials.jsonl"
    readme = out_dir / "README.md"
    if not force and (exp_path.exists() or trials_path.exists()):
        raise AepError(
            f"Refusing to overwrite existing AEP files in {out_dir}. "
            "Pass force=True / --force to replace them."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    experiment = default_experiment_template(
        name=name, profile_class=profile_class, trials=trials, seed=seed
    )
    with exp_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(experiment, fh, sort_keys=False, allow_unicode=True)

    trial_rows: list[dict[str, Any]] = []
    exp_id = experiment["experiment_id"]
    for arm in ("decoy", "reference", "evaluator_control"):
        for i in range(trials):
            row = example_trial_line(
                experiment_id=exp_id,
                trial_id=f"{arm}-{i+1:03d}",
                arm=arm,
                duration=120.0 if arm == "decoy" else 60.0,
                censored=False,
            )
            if arm != "evaluator_control":
                row.pop("evaluator_control_passed", None)
            trial_rows.append(row)
    with trials_path.open("w", encoding="utf-8") as fh:
        for row in trial_rows:
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")

    readme.write_text(
        "# AEP experiment bundle\n\n"
        "Offline Advanced Evidence Profile inputs. Fill digests/versions, "
        "replace synthetic trial rows with measured local evidence, then run:\n\n"
        "```bash\n"
        "uhbs aep validate experiment.yaml\n"
        "uhbs aep validate-trials trials.jsonl --experiment experiment.yaml\n"
        "uhbs aep analyze --experiment experiment.yaml --trials trials.jsonl "
        "--out advanced-evidence.json\n"
        "uhbs aep report advanced-evidence.json --format markdown "
        "--out ADVANCED-EVIDENCE.md\n"
        "```\n\n"
        "AEP never launches attacks and never changes UHQS.\n",
        encoding="utf-8",
    )
    return {"experiment": exp_path, "trials": trials_path, "readme": readme}


EXAMPLE_BUNDLES = ("beginner", "advanced", "template")

def export_example_bundle(
    name: str,
    out_dir: Path,
    *,
    force: bool = False,
) -> Path:
    """Copy a packaged AEP example/template bundle to a local directory."""
    if name not in EXAMPLE_BUNDLES:
        raise AepError(
            f"Unknown AEP example {name!r}. Choose one of: {', '.join(EXAMPLE_BUNDLES)}"
        )
    src = packaged_data_dir() / name
    if not src.is_dir():
        raise AepError(
            f"Packaged AEP example missing from install: {src}. "
            "Reinstall uhbs[aep] or use a git checkout."
        )
    out_dir = Path(out_dir)
    marker = out_dir / "experiment.yaml"
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        if marker.exists() or (out_dir / "trials.jsonl").exists():
            raise AepError(
                f"Refusing to overwrite existing files in {out_dir}. Use --force."
            )
        raise AepError(
            f"Output directory {out_dir} is not empty. Choose an empty path or use --force."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dest = out_dir / item.name
        if item.is_dir():
            if dest.exists() and force:
                shutil.rmtree(dest)
            shutil.copytree(item, dest, dirs_exist_ok=force)
        else:
            if dest.exists() and not force:
                raise AepError(f"Refusing to overwrite {dest}. Use --force.")
            shutil.copy2(item, dest)
    return out_dir
