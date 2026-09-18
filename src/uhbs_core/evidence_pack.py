"""Emit schema-oriented UHBS v5 evidence packs from harness ModuleResults."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from uhbs_core._version import __version__
from uhbs_core.manifest import sha256_file
from uhbs_core.models import ModuleResult, TargetSpec, UHQSResult, module_completeness
from uhbs_core.outcomes import AssuranceLevel
from uhbs_core.uhqs_math import SCORING_MODEL_ID


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_catalog_hash(check_ids: Iterable[str]) -> str:
    """Placeholder catalog hash: SHA-256 of sorted check ids (newline-joined)."""
    blob = "\n".join(sorted(check_ids))
    return _sha256_text(blob)


def _evidence_hashes(check: Any) -> list[str]:
    existing = list(getattr(check, "evidence_hashes", None) or [])
    if existing:
        return existing
    return [_sha256_text(str(e)) for e in (getattr(check, "evidence", None) or [])]


def build_evidence_pack(
    *,
    modules: Sequence[ModuleResult],
    target: TargetSpec | None = None,
    uhqs: UHQSResult | None = None,
    target_name: str | None = None,
    profile_class: str | None = None,
    out_dir: Path | None = None,
    profile_ref: str | None = None,
    protocols: list[str] | None = None,
    target_digest: str | None = None,
    environment_digest: str | None = None,
    harness_version: str | None = None,
    plugin_versions: dict[str, str] | None = None,
    command_digest: str | None = None,
    config_digest: str | None = None,
    assurance_level: str = AssuranceLevel.SELF_ASSESSED.value,
    attestation_ref: str | None = None,
) -> dict[str, Any]:
    """Build an evidence-pack dict from ModuleResult list (+ optional TargetSpec/UHQSResult)."""
    if target is not None:
        target_name = target_name or target.label
        profile_class = profile_class or target.profile_class
        protocols = protocols if protocols is not None else target.protocol_list()
        if profile_ref is None and target.tps_path:
            profile_ref = target.tps_path
    target_name = target_name or (uhqs.target if uhqs else "unknown")
    profile_class = profile_class or (uhqs.profile_class if uhqs else "POSIX-Shell")

    check_ids: list[str] = []
    module_rows: list[dict[str, Any]] = []
    for mod in modules:
        checks_out: list[dict[str, Any]] = []
        for c in mod.checks:
            check_ids.append(c.id)
            outcome_val = (
                c.outcome.value if c.outcome else ("PASS" if c.passed else "FAIL")
            )
            checks_out.append(
                {
                    "id": c.id,
                    "team": c.team,
                    "outcome": outcome_val,
                    "passed": c.passed,
                    "score": c.score,
                    "detail": c.detail,
                    "critical": c.critical,
                    "mandatory": c.mandatory,
                    "applicability_rationale": c.applicability_rationale,
                    "catalog_id": c.catalog_id or c.id,
                    "evidence": list(c.evidence or []),
                    "evidence_refs": list(c.evidence_refs or []),
                    "evidence_hashes": _evidence_hashes(c),
                }
            )
        completeness = module_completeness(list(mod.checks))
        module_rows.append(
            {
                "module": mod.module,
                "dimension": mod.dimension,
                "score": mod.score,
                "status": mod.status,
                "complete": bool(mod.complete and completeness["complete"]),
                "completeness": completeness,
                "applicable_checks": (
                    mod.applicable_checks
                    if mod.applicable_checks
                    else completeness["applicable_checks"]
                ),
                "scored_checks": (
                    mod.scored_checks
                    if mod.scored_checks
                    else completeness["scored_checks"]
                ),
                "critical_control_verdict": mod.critical_control_verdict,
                "checks": checks_out,
                "metrics": mod.metrics,
                "notes": mod.notes,
                "error": mod.error,
            }
        )

    artifacts: list[dict[str, str]] = []
    if out_dir and out_dir.is_dir():
        for path in sorted(out_dir.rglob("*")):
            if not path.is_file() or path.name in {"MANIFEST.json", "evidence-pack.json"}:
                continue
            rel = str(path.relative_to(out_dir))
            artifacts.append({"path": rel, "sha256": sha256_file(path)})

    catalog_hash = check_catalog_hash(check_ids)
    pack: dict[str, Any] = {
        "uhbs_version": __version__,
        "specification_version": __version__,
        "scoring_model_id": (
            uhqs.scoring_model_id if uhqs is not None else SCORING_MODEL_ID
        ),
        "check_catalog_hash": catalog_hash,
        "check_catalog": {
            "id": "uhbs-default-v5",
            "hash": catalog_hash,
        },
        "target": {
            "name": target_name,
            "class": profile_class,
            "protocols": protocols or [],
            "profile_ref": profile_ref,
            "artifact_digest": target_digest,
        },
        "environment": {
            "digest": environment_digest,
        },
        "evaluated_at": date.today().isoformat(),
        "harness": {
            "name": "uhbs-lab",
            "version": harness_version or __version__,
            "plugin_versions": plugin_versions or {},
            "command_digest": command_digest,  # placeholder until harness records argv digest
            "config_digest": config_digest,  # placeholder until harness records config digest
            "phases": ["profile", "static", "sandbox", "dynamic", "score"],
        },
        "modules": module_rows,
        "assurance_level": assurance_level,
        "attestation_ref": attestation_ref,
        "manifest": {
            "artifacts": artifacts,
            "digest": None,
        },
    }
    if uhqs is not None:
        pack["uhqs"] = {
            "uhqs": uhqs.uhqs,
            "grade": uhqs.grade,
            "assessment_status": uhqs.assessment_status,
            "critical_control_verdict": uhqs.critical_control_verdict,
            "scoring_model_id": uhqs.scoring_model_id,
        }
    manifest_blob = json.dumps(pack["manifest"]["artifacts"], sort_keys=True)
    pack["manifest"]["digest"] = _sha256_text(manifest_blob)
    return pack


def write_evidence_pack(
    out_dir: Path,
    *,
    pack: dict[str, Any] | None = None,
    modules: Sequence[ModuleResult] | None = None,
    target: TargetSpec | None = None,
    uhqs: UHQSResult | None = None,
    **build_kwargs: Any,
) -> Path:
    """Write ``evidence-pack.json`` under ``out_dir``.

    Pass either a pre-built ``pack`` dict or ``modules`` (+ optional target/uhqs)
    to build one via :func:`build_evidence_pack`.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if pack is None:
        if modules is None:
            raise ValueError("write_evidence_pack requires pack= or modules=")
        pack = build_evidence_pack(
            modules=modules,
            target=target,
            uhqs=uhqs,
            out_dir=out_dir,
            **build_kwargs,
        )
    dest = out_dir / "evidence-pack.json"
    dest.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return dest
