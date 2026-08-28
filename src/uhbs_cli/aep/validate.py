"""Experiment/trial validation for AEP."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .constants import _FORBIDDEN_ARG_PATTERNS, _FORBIDDEN_FIELD_KEYS
from .errors import AepError
from .io import _assert_local_path, load_schema


def reject_forbidden_cli_values(*values: str | None) -> None:
    """Reject URL / host:port style CLI string values."""
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        for pat in _FORBIDDEN_ARG_PATTERNS:
            if pat.search(text):
                raise AepError(
                    "AEP commands refuse URL/remote inputs. "
                    "Provide local experiment and trial files only."
                )
        if re.fullmatch(r"[A-Za-z0-9.-]+:\d{1,5}", text):
            raise AepError(
                "AEP commands refuse host:port inputs. "
                "Provide local experiment and trial files only."
            )


def _walk_forbidden_keys(obj: Any, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            loc = f"{path}.{key}" if path else str(key)
            if str(key).lower() in _FORBIDDEN_FIELD_KEYS:
                hits.append(loc)
            hits.extend(_walk_forbidden_keys(val, loc))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            hits.extend(_walk_forbidden_keys(item, f"{path}[{i}]"))
    return hits


def validate_schema(data: Any, schema_name: str) -> list[str]:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [
        f"{'.'.join(str(p) for p in err.path) or '(root)'}: {err.message}" for err in errors
    ]


def validate_experiment(data: Any, *, strict: bool = True) -> list[str]:
    if not isinstance(data, dict):
        return ["(root): experiment must be a mapping/object"]
    errors = validate_schema(data, "aep-experiment.schema.json")
    errors.extend(f"forbidden field: {loc}" for loc in _walk_forbidden_keys(data))
    if strict:
        attest = data.get("attestations") or {}
        for key in (
            "sandbox_only",
            "no_production_assets",
            "local_evidence_only",
            "informative_only",
        ):
            if attest.get(key) is not True:
                errors.append(f"attestations.{key}: must be true")
        utility = data.get("utility") or {}
        weights = utility.get("weights") or {}
        if not weights:
            errors.append("utility.weights: required for VoD (explicit utility model)")
        reps = data.get("repetitions") or {}
        if reps.get("minimum_per_arm", 0) > reps.get("planned_per_arm", 0):
            errors.append("repetitions: minimum_per_arm cannot exceed planned_per_arm")
    return errors


def load_trials_jsonl(path: Path) -> list[dict[str, Any]]:
    _assert_local_path(path)
    trials: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                raise AepError(f"{path}:{lineno}: invalid JSON — {exc}") from exc
            if not isinstance(obj, dict):
                raise AepError(f"{path}:{lineno}: trial must be a JSON object")
            trials.append(obj)
    if not trials:
        raise AepError(f"{path}: no trial objects found (empty JSONL)")
    return trials


def validate_trials(
    trials: list[dict[str, Any]],
    experiment: dict[str, Any] | None = None,
    *,
    strict: bool = True,
) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    exp_id = (experiment or {}).get("experiment_id")
    for idx, trial in enumerate(trials):
        prefix = f"trial[{idx}]"
        schema_errs = validate_schema(trial, "aep-trial.schema.json")
        errors.extend(f"{prefix}.{e}" for e in schema_errs)
        errors.extend(f"{prefix} forbidden field: {loc}" for loc in _walk_forbidden_keys(trial))
        tid = trial.get("trial_id")
        if isinstance(tid, str):
            if tid in seen_ids:
                errors.append(f"{prefix}.trial_id: duplicate {tid}")
            seen_ids.add(tid)
        if exp_id and trial.get("experiment_id") != exp_id:
            errors.append(
                f"{prefix}.experiment_id: {trial.get('experiment_id')!r} "
                f"!= experiment {exp_id!r}"
            )
        started = trial.get("started_at")
        ended = trial.get("ended_at")
        if isinstance(started, str) and isinstance(ended, str):
            try:
                t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(ended.replace("Z", "+00:00"))
                if t1 < t0:
                    errors.append(f"{prefix}: ended_at before started_at")
            except ValueError:
                errors.append(f"{prefix}: invalid timestamp")
    if strict and experiment is not None:
        arms_present = {t.get("arm") for t in trials}
        if "decoy" not in arms_present or "reference" not in arms_present:
            errors.append("strict: trials must include both decoy and reference arms")
        min_n = int((experiment.get("repetitions") or {}).get("minimum_per_arm", 1))
        for arm in ("decoy", "reference"):
            n = sum(1 for t in trials if t.get("arm") == arm)
            if n < min_n:
                errors.append(f"strict: arm {arm} has {n} trials; minimum_per_arm={min_n}")
    return errors

