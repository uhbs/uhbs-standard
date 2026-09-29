"""Path and schema helpers for the UHBS CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml


def _repo_root() -> Path:
    """Resolve the UHBS checkout root (editable layout or UHBS_ROOT)."""
    env = os.environ.get("UHBS_ROOT")
    if env:
        return Path(env)
    # src/uhbs_cli/cli/paths.py → repo root (editable / Docker source tree)
    return Path(__file__).resolve().parents[3]


def _uhbs_cli_root() -> Path:
    """Return the uhbs_cli package directory (parent of this cli package)."""
    return Path(__file__).resolve().parents[1]


def _schema_dir() -> Path:
    """Locate JSON Schemas for profile/scorecard/evidence validation.

    Prefer ``UHBS_SCHEMA_DIR``, then schemas shipped inside the installed
    ``uhbs_cli`` package (PyPI wheel), then a source checkout's ``schemas/``.
    """
    env = os.environ.get("UHBS_SCHEMA_DIR")
    if env:
        return Path(env)
    packaged = _uhbs_cli_root() / "schemas"
    if (packaged / "scorecard.schema.json").is_file():
        return packaged
    return _repo_root() / "schemas"


ROOT = _repo_root()
SCHEMA_DIR = _schema_dir()


def _load_schema(name: str) -> dict[str, Any]:
    path = _schema_dir() / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _schema_for_document(name: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Load a schema, preferring frozen ``v4/`` copies for UHBS 4.x documents.

    When ``uhbs_version`` starts with ``4.`` and the document does **not**
    declare a v5 ``scoring_model_id``, validate against ``schemas/v4/<name>``.
    Documents that already carry ``uhqs-v5*`` use the current (v5) schema even
    if ``uhbs_version`` has not been bumped yet.
    """
    payload = data or {}
    version = str(payload.get("uhbs_version") or "")
    model = str(payload.get("scoring_model_id") or "")
    if version.startswith("4.") and not model.startswith("uhqs-v5"):
        v4_name = f"v4/{name}"
        v4_path = _schema_dir() / v4_name
        if v4_path.is_file():
            return _load_schema(v4_name)
    return _load_schema(name)


def _load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)
