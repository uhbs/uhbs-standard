"""Type coercion and hashing helpers for SLM responses."""

from __future__ import annotations

import hashlib
from typing import Any

from .errors import AepSlmError


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _as_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    raise AepSlmError(
        f"{field}: expected JSON boolean, got {type(value).__name__} ({value!r})"
    )


def _as_float(value: Any, *, field: str) -> float:
    # bool is a subclass of int — reject explicitly.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AepSlmError(
            f"{field}: expected JSON number, got {type(value).__name__} ({value!r})"
        )
    return float(value)


def _as_int(value: Any, *, field: str) -> int:
    if isinstance(value, bool):
        raise AepSlmError(
            f"{field}: expected JSON integer, got boolean ({value!r})"
        )
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise AepSlmError(
        f"{field}: expected JSON integer, got {type(value).__name__} ({value!r})"
    )


def _as_str_list(value: Any, *, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise AepSlmError(
            f"{field}: expected JSON array of strings, got {type(value).__name__}"
        )
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise AepSlmError(
                f"{field}[{i}]: expected string, got {type(item).__name__}"
            )
        out.append(item)
    return out
