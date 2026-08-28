"""Mock, recorded, and openai_compatible response providers."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any

from uhbs_cli import aep as aep_mod

from .errors import AepSlmError
from .http_client import _call_openai_compatible


def _render_user_prompt(template: str, *, arm: str, trial_index: int, seed: int) -> str:
    try:
        return template.format(arm=arm, trial_index=trial_index, seed=seed)
    except (KeyError, ValueError, IndexError) as exc:
        raise AepSlmError(
            "task.user_prompt_template format error "
            f"(allowed placeholders: {{arm}}, {{trial_index}}, {{seed}}): {exc}"
        ) from exc


def _mock_response(
    *, arm: str, trial_index: int, seed: int, temperature: float
) -> dict[str, Any]:
    """Deterministic synthetic model JSON — no network."""
    rng = random.Random(f"{seed}:{arm}:{trial_index}:{temperature}")
    if arm == "decoy":
        duration = 80.0 + rng.random() * 40.0
        exchanges = 4 + rng.randint(0, 4)
        predicted = True
        confidence = 0.55 + rng.random() * 0.35
        control_ok = True
    elif arm == "reference":
        duration = 30.0 + rng.random() * 30.0
        exchanges = 1 + rng.randint(0, 2)
        predicted = False
        confidence = 0.50 + rng.random() * 0.40
        control_ok = True
    else:
        duration = 20.0 + rng.random() * 20.0
        exchanges = 2 + rng.randint(0, 2)
        predicted = False
        confidence = 0.70 + rng.random() * 0.25
        control_ok = True
    return {
        "session_duration_seconds": round(duration, 3),
        "exchanges": exchanges,
        "attempts": max(1, exchanges - 1),
        "predicted_decoy": predicted,
        "confidence": round(confidence, 4),
        "evaluator_control_passed": control_ok,
        "unique_tools": ["shell"] if arm != "reference" else [],
        "unique_credentials": [],
        "unique_payload_families": ["recon"],
    }


def _parse_model_json(text: str) -> dict[str, Any]:
    text = text.strip()
    # Tolerate fenced blocks from local models.
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        # Last-resort: find first {...}
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                obj = json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc2:
                raise AepSlmError(f"model response is not JSON: {exc2}") from exc2
        else:
            raise AepSlmError(f"model response is not JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise AepSlmError("model response JSON root must be an object")
    return obj

def _load_recorded(path: Path) -> list[dict[str, Any]]:
    aep_mod.reject_forbidden_cli_values(str(path))
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                raise AepSlmError(f"{path}:{lineno}: invalid JSON — {exc}") from exc
            if not isinstance(obj, dict):
                raise AepSlmError(f"{path}:{lineno}: recorded row must be an object")
            rows.append(obj)
    if not rows:
        raise AepSlmError(f"{path}: no recorded responses")
    return rows


def _resolve_response(
    config: dict[str, Any],
    *,
    arm: str,
    trial_index: int,
    recorded: list[dict[str, Any]] | None,
    recorded_cursor: list[int],
) -> tuple[dict[str, Any], str]:
    gen = config.get("generation") or {}
    seed = int(gen.get("seed") or 0)
    temperature = float(gen.get("temperature") or 0)
    task = config.get("task") or {}
    provider = config.get("provider")

    if provider == "mock":
        parsed = _mock_response(
            arm=arm, trial_index=trial_index, seed=seed, temperature=temperature
        )
        raw = json.dumps(parsed, sort_keys=True)
        return parsed, raw

    user_prompt = _render_user_prompt(
        str(task.get("user_prompt_template") or ""),
        arm=arm,
        trial_index=trial_index,
        seed=seed,
    )
    system_prompt = str(task.get("system_prompt") or "")

    if provider == "recorded":
        if recorded is None:
            raise AepSlmError("recorded provider requires recorded_responses_path data")
        idx = recorded_cursor[0]
        if idx >= len(recorded):
            raise AepSlmError(
                "recorded_responses_path exhausted before all trials were filled"
            )
        row = recorded[idx]
        recorded_cursor[0] = idx + 1
        if "content" in row:
            raw = str(row["content"])
            parsed = _parse_model_json(raw)
        elif "response" in row and isinstance(row["response"], dict):
            parsed = row["response"]
            raw = json.dumps(parsed, sort_keys=True)
        else:
            raise AepSlmError(
                "recorded row needs 'content' (string) or 'response' (object)"
            )
        return parsed, raw

    if provider == "openai_compatible":
        raw = _call_openai_compatible(
            config, system_prompt=system_prompt, user_prompt=user_prompt
        )
        return _parse_model_json(raw), raw

    raise AepSlmError(f"unsupported provider: {provider!r}")

