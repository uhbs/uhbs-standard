"""Markdown rendering for AEP evidence addenda."""

from __future__ import annotations

from typing import Any


def render_markdown(evidence: dict[str, Any], *, include_methodology: bool = True) -> str:
    lines = [
        "# Advanced Evidence Addendum",
        "",
        "> **Informative only · lab / sandbox evidence.** This document does "
        "**not** change UHQS, δ_C, weights, or letter grade. Status values are "
        "`valid | inconclusive | control_failed` — not pass/fail grades. "
        "UHBS/AEP are laboratory evaluation tools — not real-world production testing.",
        "",
        f"- Experiment ID: `{evidence.get('experiment_id')}`",
        f"- AEP status: **{evidence.get('status')}**",
        f"- Control status: **{evidence.get('control_status')}**",
        f"- UHQS unchanged: **{evidence.get('uhqs_unchanged')}**",
        "",
    ]
    if include_methodology:
        lines += [
            "## Methodology (summary)",
            "",
            "Three-arm controlled **lab** design (decoy, matched lab reference, "
            "optional evaluator control). Metrics use local trial evidence only. "
            "Bootstrap intervals use the declared analysis seed.",
            "",
            "## Academic credit",
            "",
            "AEP design vocabulary draws on Zhu (2019) DOI 10.1145/3314058.3314067; "
            "Collins, Xu & Brown (2024) arXiv:2401.13815; Ersok et al. (2022) "
            "DOI 10.1109/ICCC202255925.2022.9922853; Li et al. (2020) "
            "DOI 10.1109/OJCS.2020.3030825. Citation does not imply endorsement. "
            "See UHBS docs: advanced-evidence/research-foundations.",
            "",
        ]
    lines += ["## Metrics", ""]
    metrics = evidence.get("metrics") or {}
    for name in ("vod", "dtdr", "eer"):
        block = metrics.get(name) or {}
        lines.append(f"### {name.upper()}")
        lines.append("")
        lines.append(f"- Value: `{block.get('value')}` {block.get('unit', '')}")
        lines.append(f"- Status: `{block.get('status')}`")
        lines.append(f"- n: `{block.get('n')}`")
        interval = block.get("interval") or {}
        lines.append(
            f"- Interval ({interval.get('confidence')}): "
            f"[{interval.get('low')}, {interval.get('high')}]"
        )
        if block.get("notes"):
            lines.append(f"- Notes: {block['notes']}")
        lines.append("")
    fsv = metrics.get("fsv") or {}
    lines += ["### FSV (per layer)", ""]
    for layer, block in (fsv.get("layers") or {}).items():
        lines.append(
            f"- **{layer}**: TPR=`{block.get('tpr')}` FPR=`{block.get('fpr')}` "
            f"bal_acc=`{block.get('balanced_accuracy')}` "
            f"status=`{block.get('status')}` n=`{block.get('n')}`"
        )
    lines += ["", "## Sample", ""]
    sample = evidence.get("sample") or {}
    for arm, counts in (sample.get("per_arm") or {}).items():
        lines.append(f"- {arm}: n={counts.get('n')} censored={counts.get('censored')}")
    lines.append(f"- Censoring rate: {sample.get('censoring_rate')}")
    lines += ["", "## Warnings", ""]
    warnings = evidence.get("warnings") or []
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- (none)")
    lines += [
        "",
        "## Interpretation",
        "",
        evidence.get("interpretation")
        or "AEP evidence observed under the declared controlled conditions.",
        "",
        "## Limitations",
        "",
    ]
    for lim in evidence.get("limitations") or []:
        lines.append(f"- {lim}")
    lines += [
        "",
        "## Provenance",
        "",
        f"- Tool: `{((evidence.get('provenance') or {}).get('tool'))}` "
        f"{((evidence.get('provenance') or {}).get('tool_version'))}",
        f"- Analysis seed: `{(evidence.get('provenance') or {}).get('analysis_seed')}`",
        f"- Scorecard ref: `{(evidence.get('provenance') or {}).get('scorecard_ref')}`",
        "",
    ]
    return "\n".join(lines) + "\n"

