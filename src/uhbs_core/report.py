"""UHBS v5 scorecard + JSON report writer."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from uhbs_core._version import __version__

from .models import DIM_LABELS, DIMS, UHQS_ATTR, ModuleResult, TargetSpec, UHQSResult
from .uhqs_math import SCORING_MODEL_ID


def _status_line(mod: ModuleResult | None, score: float | None) -> str:
    if mod is None:
        return "N/A"
    if mod.status in {"SKIPPED", "INCOMPLETE"}:
        return f"{mod.status} ({'; '.join(mod.notes[:1]) or 'not complete'})"
    detail = ""
    failed = [
        c
        for c in mod.checks
        if c.outcome and c.outcome.value in {"FAIL", "ERROR", "NOT_TESTED"}
    ]
    passed = [c for c in mod.checks if c.passed]
    if failed:
        detail = failed[0].detail or failed[0].id
    elif passed:
        detail = passed[-1].detail or passed[-1].id
    numeric = score if isinstance(score, (int, float)) else 0.0
    st = (
        mod.status
        if numeric < 70 or mod.status in {"FAILED", "GATE_FAILED"}
        else "PASSED"
    )
    return f"{st}" + (f" ({detail})" if detail else "")


def _score_cell(score: float | None) -> str:
    if score is None:
        return "  —/100"
    return f"{float(score):>5.1f}/100"


def render_card(
    target: TargetSpec,
    baseline: TargetSpec | None,
    uhqs: UHQSResult,
    modules: list[ModuleResult],
    environment: str = "Isolated Sandbox",
    evaluation_type: str = "Full-Spectrum (Static Audit + Dynamic Sandbox)",
) -> str:
    by_dim: dict[str, ModuleResult] = {}
    for m in modules:
        if m.module == "SOURCE":
            by_dim.setdefault(m.dimension, m)
        else:
            by_dim[m.dimension] = m

    weights = uhqs.weights
    ungraded = uhqs.uhqs is None
    lines = [
        "====================================================================================",
        f"                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v{__version__}",
        "====================================================================================",
        f"Target System         : {target.label}",
        f"System Profile Class  : {uhqs.profile_class}",
        f"Scoring Model         : {uhqs.scoring_model_id}",
        f"Assessment Status     : {uhqs.assessment_status}",
        f"Critical Controls     : {uhqs.critical_control_verdict}",
        f"Protocols             : {', '.join(target.protocol_list())}",
        f"Evaluation Date       : {datetime.now(UTC).strftime('%Y-%m-%d')}",
        f"Evaluation Type       : {evaluation_type}",
        f"Environment           : {environment}",
    ]
    for m in modules:
        if m.module == "B" and m.metrics.get("surface_depth"):
            lines.append(f"MCP Surface Depth     : {m.metrics['surface_depth']}")
            reason = (target.annotations or {}).get("mcp_surface_reason")
            if not reason:
                for note in m.notes or []:
                    text = str(note)
                    if (
                        "surface_depth=" in text
                        or "SKIPPED_" in text
                        or "NEUTRAL_" in text
                        or "Module B" in text
                        or text.startswith("UHBS ")
                    ):
                        continue
                    reason = text
                    break
            if reason:
                lines.append(f"MCP Surface Reason    : {str(reason)[:120]}")
            break
    lines.extend(
        [
            "------------------------------------------------------------------------------------",
            "EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS",
            "------------------------------------------------------------------------------------",
        ]
    )
    for dim in DIMS:
        label = DIM_LABELS[dim]
        score = getattr(uhqs, UHQS_ATTR[dim])
        wtxt = "GATE" if dim == "containment" else f"{weights.get(dim, 0):.2f}"
        status = _status_line(by_dim.get(dim), score)
        lines.append(f"{label:<36}: {_score_cell(score)}       {wtxt:<6}   {status}")
    if uhqs.assessment_status == "INCOMPLETE":
        gate = "Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)"
    elif uhqs.critical_control_verdict == "GATE_FAILED":
        gate = f"GATE_FAILED (defense-in-depth C={uhqs.C}; no composite UHQS)"
    elif uhqs.critical_control_verdict == "GATE_PASSED":
        gate = f"GATE_PASSED (δ_C={uhqs.delta_c}; defense-in-depth C={uhqs.C})"
    else:
        gate = f"verdict={uhqs.critical_control_verdict} δ_C={uhqs.delta_c}"
    if ungraded:
        uhqs_txt = "null (Ungraded — no composite UHQS)"
        grade_txt = "— (no letter grade)"
    else:
        uhqs_txt = f"{uhqs.uhqs} / 100"
        grade_txt = uhqs.grade if uhqs.grade is not None else "— (no letter grade)"
    lines += [
        "------------------------------------------------------------------------------------",
        f"SAFETY GATE / CRITICAL CONTROLS        : {gate}",
        f"FINAL COMPOSITE SCORE (UHQS {__version__})      : {uhqs_txt}",
        f"OVERALL EVALUATION GRADE              : {grade_txt}",
        f"scoring_model_id                      : {SCORING_MODEL_ID}",
        "====================================================================================",
    ]
    if baseline:
        lines.insert(6, f"Baseline System       : {baseline.label}")
    return "\n".join(lines) + "\n"


def write_report(
    out_dir: Path,
    target: TargetSpec,
    baseline: TargetSpec | None,
    uhqs: UHQSResult,
    modules: list[ModuleResult],
    extras: dict[str, Any] | None = None,
    evaluation_type: str = "Full-Spectrum (Static Audit + Dynamic Sandbox)",
    *,
    assurance_level: str | None = None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    card = render_card(
        target, baseline, uhqs, modules, evaluation_type=evaluation_type
    )
    (out_dir / "REPORT.txt").write_text(card, encoding="utf-8")
    (out_dir / "SCORECARD.txt").write_text(card, encoding="utf-8")
    payload = {
        "framework": f"Universal Honeypot Benchmarking Standard (UHBS) v{__version__}",
        "scoring_model_id": uhqs.scoring_model_id,
        "assessment_status": uhqs.assessment_status,
        "critical_control_verdict": uhqs.critical_control_verdict,
        "evaluation_type": evaluation_type,
        "target": {
            "name": target.name,
            "kind": target.kind,
            "host": target.host,
            "port": target.port,
            "source_root": target.source_root,
            "profile_class": target.profile_class,
            "protocols": target.protocol_list(),
            "ports_map": target.ports_map,
        },
        "baseline": (
            {
                "name": baseline.name,
                "kind": baseline.kind,
                "host": baseline.host,
                "protocols": baseline.protocol_list(),
            }
            if baseline
            else None
        ),
        "uhqs": uhqs.to_dict(),
        "hqs": uhqs.to_dict(),  # compat
        "modules": [m.to_dict() for m in modules],
        "extras": extras or {},
    }
    path = out_dir / "report.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if modules:
        from uhbs_core.evidence_pack import write_evidence_pack
        from uhbs_core.outcomes import AssuranceLevel

        write_evidence_pack(
            out_dir,
            modules=modules,
            target=target,
            uhqs=uhqs,
            assurance_level=assurance_level or AssuranceLevel.SELF_ASSESSED.value,
        )
    return path
