"""Pinned MITRE ATT&CK technique ID resolution (Enterprise + ICS)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

_PIN_PATH = Path(__file__).resolve().parent / "data" / "attack_pin.json"
_TECH_RE = re.compile(r"^T[0-9]{4}(?:\.[0-9]{3})?$")
_TECH_FIND_RE = re.compile(r"\bT[0-9]{4}(?:\.[0-9]{3})?\b")


@dataclass(frozen=True)
class AttackMappingResult:
    technique_id: str
    valid: bool
    revoked: bool
    deprecated: bool
    name: str | None
    domains: tuple[str, ...]
    detail: str


@lru_cache(maxsize=1)
def _load_pin() -> dict[str, Any]:
    return json.loads(_PIN_PATH.read_text(encoding="utf-8"))


def pin_meta() -> dict[str, str]:
    data = _load_pin()
    return {
        "bundle_id": str(data.get("bundle_id", "")),
        "enterprise_version": str(data.get("enterprise_version", "")),
        "ics_version": str(data.get("ics_version", "")),
    }


def resolve_technique(technique_id: str) -> AttackMappingResult:
    tid = technique_id.strip().upper()
    if not _TECH_RE.match(tid):
        return AttackMappingResult(
            technique_id=tid,
            valid=False,
            revoked=False,
            deprecated=False,
            name=None,
            domains=(),
            detail="id does not match T####(.###) pattern",
        )
    techniques = _load_pin().get("techniques") or {}
    # Preserve dotted form; also try as-given
    entry = techniques.get(tid) or techniques.get(technique_id.strip())
    if not entry:
        # Try original casing keys
        for k, v in techniques.items():
            if k.upper() == tid:
                entry = v
                tid = k
                break
    if not entry:
        return AttackMappingResult(
            technique_id=tid,
            valid=False,
            revoked=False,
            deprecated=False,
            name=None,
            domains=(),
            detail="technique not present in pinned ATT&CK bundle",
        )
    revoked = bool(entry.get("revoked"))
    deprecated = bool(entry.get("deprecated"))
    return AttackMappingResult(
        technique_id=tid,
        valid=not revoked,
        revoked=revoked,
        deprecated=deprecated,
        name=str(entry.get("name") or "") or None,
        domains=tuple(entry.get("domains") or ()),
        detail="ok" if not revoked else "revoked in pinned bundle",
    )


def extract_technique_ids(blob: str) -> list[str]:
    """Extract ATT&CK technique IDs — not bare words like 'attack'."""
    return sorted(set(_TECH_FIND_RE.findall(blob.upper().replace("ATT&CK", " "))))


def validate_claimed_mappings(
    claimed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate claimed ATT&CK mappings; record basis/confidence/provenance fields."""
    out: list[dict[str, Any]] = []
    for row in claimed:
        tid = str(row.get("technique_id") or row.get("id") or "")
        resolved = resolve_technique(tid)
        basis = str(row.get("mapping_basis") or row.get("basis") or "analyst_asserted")
        if basis not in {"observed", "inferred", "analyst_asserted"}:
            basis = "analyst_asserted"
        out.append(
            {
                "technique_id": resolved.technique_id,
                "valid": resolved.valid,
                "revoked": resolved.revoked,
                "deprecated": resolved.deprecated,
                "name": resolved.name,
                "mapping_basis": basis,
                "confidence": row.get("confidence"),
                "source_event_refs": list(row.get("source_event_refs") or []),
                "data_markings": list(row.get("data_markings") or []),
                "bundle": pin_meta(),
                "detail": resolved.detail,
            }
        )
    return out
