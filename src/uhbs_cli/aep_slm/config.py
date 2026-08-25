"""Config template, validation, and IO for AEP SLM."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from uhbs_cli import aep as aep_mod

from .constants import AEP_SLM_VERSION, SCHEMA_NAME, UNLOCK_PHRASE
from .errors import AepSlmError
from .http_client import _assert_loopback_url


def default_config_template(
    *,
    experiment_path: str = "experiment.yaml",
    output_trials: str = "slm-trials.jsonl",
    output_run: str = "slm-run.json",
) -> dict[str, Any]:
    """Return a **disabled** alpha config. User must edit the file to activate."""
    return {
        "aep_slm_version": AEP_SLM_VERSION,
        "status": "alpha",
        "enabled": False,
        "activation": {
            "unlock_phrase": "CHANGE_ME_SEE_DOCS",
            "acknowledge_alpha": False,
            "lab_sandbox_only": False,
            "no_production_targets": False,
            "no_uhqs_scoring_impact": False,
            "allow_local_model_calls": False,
        },
        "provider": "mock",
        "model": {
            "name": "uhbs-mock-slm",
            "notes": "Deterministic offline mock. Replace only after unlocking.",
        },
        "task": {
            "prompt_id": "aep-slm-alpha-v1",
            "system_prompt": (
                "You are a lab-only honeypot engagement evaluator. "
                "Reply with a single JSON object describing a synthetic trial "
                "outcome. Never suggest contacting production systems."
            ),
            "user_prompt_template": (
                "Arm={arm} trial_index={trial_index} seed={seed}. "
                "Return JSON with keys: session_duration_seconds, exchanges, "
                "attempts, predicted_decoy (bool), confidence (0-1), "
                "evaluator_control_passed (bool)."
            ),
        },
        "generation": {
            "trials_per_arm": 5,
            "seed": 42,
            "temperature": 0.0,
            "max_tokens": 256,
            "arms": ["decoy", "reference", "evaluator_control"],
        },
        "paths": {
            "experiment": experiment_path,
            "output_trials": output_trials,
            "output_run": output_run,
        },
        "safety": {
            "loopback_only": True,
            "forbid_tools": True,
            "forbid_network_targets": True,
            "write_local_files_only": True,
        },
        "notes": (
            "ALPHA / DISABLED BY DEFAULT. To activate, edit this file: set "
            f"enabled=true, unlock_phrase={UNLOCK_PHRASE!r}, and every "
            "activation.* boolean to true (for openai_compatible also set "
            "allow_local_model_calls=true). Then: uhbs aep slm validate && "
            "uhbs aep slm generate. Does not change UHQS."
        ),
    }


def activation_blockers(config: dict[str, Any]) -> list[str]:
    """Return human-readable reasons generation is blocked (empty if unlocked)."""
    blockers: list[str] = []
    if config.get("enabled") is not True:
        blockers.append("enabled is not true (edit config: enabled: true)")
    act = config.get("activation") or {}
    if act.get("unlock_phrase") != UNLOCK_PHRASE:
        blockers.append(
            f"activation.unlock_phrase must be exactly {UNLOCK_PHRASE!r}"
        )
    for key in (
        "acknowledge_alpha",
        "lab_sandbox_only",
        "no_production_targets",
        "no_uhqs_scoring_impact",
    ):
        if act.get(key) is not True:
            blockers.append(f"activation.{key} must be true")
    provider = config.get("provider")
    # Offline recorded/mock do not need model-call attestation.
    if provider == "openai_compatible" and act.get("allow_local_model_calls") is not True:
        blockers.append(
            "activation.allow_local_model_calls must be true for "
            "provider='openai_compatible'"
        )
    return blockers


def validate_config(config: Any, *, require_unlocked: bool = False) -> list[str]:
    """Schema + safety checks. Optionally require full activation."""
    if not isinstance(config, dict):
        return ["(root): config must be a mapping/object"]
    errors = aep_mod.validate_schema(config, SCHEMA_NAME)
    safety = config.get("safety") or {}
    for key in (
        "loopback_only",
        "forbid_tools",
        "forbid_network_targets",
        "write_local_files_only",
    ):
        if safety.get(key) is not True:
            errors.append(f"safety.{key}: must be true (const)")
    provider = config.get("provider")
    if provider == "openai_compatible":
        endpoint = config.get("endpoint") or {}
        base = endpoint.get("base_url")
        if not base:
            errors.append("endpoint.base_url: required for openai_compatible")
        else:
            try:
                _assert_loopback_url(str(base))
            except AepSlmError as exc:
                errors.append(str(exc))
    if provider == "recorded" and not config.get("recorded_responses_path"):
        errors.append("recorded_responses_path: required for provider=recorded")
    if require_unlocked:
        errors.extend(activation_blockers(config))
    return errors


def load_config(path: Path) -> dict[str, Any]:
    aep_mod.reject_forbidden_cli_values(str(path))
    data = aep_mod.load_yaml(path)
    if not isinstance(data, dict):
        raise AepSlmError(f"{path}: config must be a YAML mapping")
    return data


def write_init_config(
    out_path: Path,
    *,
    force: bool = False,
    experiment_path: str = "experiment.yaml",
) -> Path:
    """Write a disabled-by-default alpha SLM config file."""
    aep_mod.reject_forbidden_cli_values(str(out_path), experiment_path)
    out_path = Path(out_path)
    if out_path.exists() and not force:
        raise AepSlmError(
            f"Refusing to overwrite {out_path}. Pass --force to replace it."
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = default_config_template(experiment_path=experiment_path)
    with out_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(cfg, fh, sort_keys=False, allow_unicode=True)
    return out_path

