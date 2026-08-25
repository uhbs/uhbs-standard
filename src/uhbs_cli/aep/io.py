"""Local filesystem IO and schema loading for AEP."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

from .constants import _FORBIDDEN_ARG_PATTERNS
from .errors import AepError


def _uhbs_cli_root() -> Path:
    """Return the uhbs_cli package directory (parent of this aep package)."""
    return Path(__file__).resolve().parents[1]


def _schema_dir() -> Path:
    env = os.environ.get("UHBS_SCHEMA_DIR")
    if env:
        return Path(env)
    packaged = _uhbs_cli_root() / "schemas"
    if (packaged / "aep-experiment.schema.json").is_file():
        return packaged
    return Path(__file__).resolve().parents[3] / "schemas"


def packaged_data_dir() -> Path:
    """Directory of packaged AEP examples/templates inside uhbs_cli."""
    return _uhbs_cli_root() / "data" / "advanced-evidence"


def load_schema(name: str) -> dict[str, Any]:
    path = _schema_dir() / name
    if not path.is_file():
        raise AepError(f"AEP schema not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_yaml(path: Path) -> Any:
    _assert_local_path(path)
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        raise AepError(f"{path}: empty or null YAML document")
    return data


def load_json(path: Path) -> Any:
    _assert_local_path(path)
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if data is None:
        raise AepError(f"{path}: JSON null root is not allowed")
    return data


def _assert_local_path(path: Path) -> None:
    text = str(path)
    for pat in _FORBIDDEN_ARG_PATTERNS:
        if pat.search(text):
            raise AepError(
                f"AEP accepts local filesystem paths only; refused remote-looking path: {path}"
            )
    if path.is_absolute() and not path.exists() and "://" in text:
        raise AepError(f"AEP accepts local filesystem paths only: {path}")

