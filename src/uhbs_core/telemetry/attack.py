"""Pinned MITRE ATT&CK technique ID validation (Enterprise + ICS subset).

Bundle is a repository-local allowlist derived from ATT&CK STIX technique IDs.
Full STIX bundle import is optional; validation rejects unknown / revoked IDs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

_TECH_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$")


@dataclass(frozen=True)
class AttackMappingRecord:
    technique_id: str
    valid: bool
    revoked: bool
    deprecated: bool
    bundle_version: str
    mapping_basis: str  # observed | inferred | analyst_asserted
    confidence: float | None
    detail: str


@lru_cache(maxsize=1)
def _load_bundle() -> dict[str, Any]:
    # Prefer packaged data next to this module tree
    candidates = [
        Path(__file__).resolve().parents[1] / "data" / "attack" / "pinned_techniques.json",
    ]
    for path in candidates:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    # Fallback minimal set if data file missing (tests still exercise API)
    return {
        "bundle_version": "attack-v15.1-subset-uhbs",
        "techniques": {
            "T1041": {
                "name": "Exfiltration Over C2 Channel",
                "revoked": False,
                "deprecated": False,
            },
            "T1059": {
                "name": "Command and Scripting Interpreter",
                "revoked": False,
                "deprecated": False,
            },
            "T1059.004": {"name": "Unix Shell", "revoked": False, "deprecated": False},
            "T1078": {"name": "Valid Accounts", "revoked": False, "deprecated": False},
            "T1110": {"name": "Brute Force", "revoked": False, "deprecated": False},
            "T1595": {"name": "Active Scanning", "revoked": False, "deprecated": False},
        },
    }


def bundle_version() -> str:
    return str(_load_bundle().get("bundle_version", "unknown"))


def validate_technique_id(
    technique_id: str,
    *,
    mapping_basis: str = "observed",
    confidence: float | None = None,
) -> AttackMappingRecord:
    tid = str(technique_id).strip().upper()
    bundle = _load_bundle()
    version = str(bundle.get("bundle_version", "unknown"))
    if not _TECH_RE.match(tid):
        return AttackMappingRecord(
            technique_id=tid,
            valid=False,
            revoked=False,
            deprecated=False,
            bundle_version=version,
            mapping_basis=mapping_basis,
            confidence=confidence,
            detail="id does not match ATT&CK technique pattern",
        )
    techniques = bundle.get("techniques") or {}
    meta = techniques.get(tid)
    if meta is None:
        # Try parent technique for sub-techniques
        parent = tid.split(".")[0]
        meta = techniques.get(parent)
        if meta is None:
            return AttackMappingRecord(
                technique_id=tid,
                valid=False,
                revoked=False,
                deprecated=False,
                bundle_version=version,
                mapping_basis=mapping_basis,
                confidence=confidence,
                detail="technique not in pinned ATT&CK bundle",
            )
    revoked = bool(meta.get("revoked"))
    deprecated = bool(meta.get("deprecated"))
    ok = not revoked and not deprecated
    detail = meta.get("name") or "ok"
    if revoked:
        detail = "revoked in pinned bundle"
    elif deprecated:
        detail = "deprecated in pinned bundle"
    return AttackMappingRecord(
        technique_id=tid,
        valid=ok,
        revoked=revoked,
        deprecated=deprecated,
        bundle_version=version,
        mapping_basis=mapping_basis,
        confidence=confidence,
        detail=str(detail),
    )


def extract_technique_ids(text: str) -> list[str]:
    """Extract ATT&CK-looking IDs from free text (not a validity claim)."""
    found = re.findall(r"\bT\d{4}(?:\.\d{3})?\b", text, flags=re.IGNORECASE)
    # Deduplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for item in found:
        key = item.upper()
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out
