#!/usr/bin/env python3
"""Rescore results-5.0.1 artifacts under the spec-correct measured-renorm rule.

Fix context (2026-09-28): run_benchmark.py graded unmeasured modules
(complete=False — skipped SAST, unrun telemetry sinks) as product zeros with
full weight, contradicting the uhqs_math spec (exclusion + renormalization).
The harness is fixed; this tool applies the same rule to already-graded
artifacts WITHOUT re-running the labs:

* per-module scores are valid evidence — only the composite is recomputed
* recomputation goes through the normative ``uhbs_core.uhqs_math.compute_uhqs``
  (single source of truth — never a second math copy)
* δ_C is re-derived from the stored Module D verdict and cross-checked against
  the stored delta_c; mismatches are reported, not silently overridden
* fewer than 4 measured composite modules -> assessment_status=INCOMPLETE
  (partial measurement — not comparable), mirroring the harness guard
* updates report.json / SCORECARD.txt / REPORT.txt composite lines and the
  affected MANIFEST.json sha256 entries

Usage:
    python scripts/rescore_renorm.py --root docs/conformance/latest/results-5.0.1 [--write]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uhbs_core.run_benchmark import MIN_MEASURED_COMPOSITE  # noqa: E402
from uhbs_core.uhqs_math import (  # noqa: E402
    AssessmentStatus,
    CriticalControlVerdict,
    compute_uhqs,
    grade_for,
    measured_modules_from_results,
)

RESCORE_NOTE = "rescored 2026-09-28: measured-renorm exclusion fix (harness never passed measured_modules)"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def flags_from_report(d: dict) -> dict[str, bool]:
    payload = {
        m.get("module"): {"status": m.get("status"), "complete": m.get("complete")}
        for m in d.get("modules", [])
        if m.get("module") in {"A", "B", "C", "E", "F"}
    }
    return measured_modules_from_results(payload)


def verdict_from_report(d: dict) -> CriticalControlVerdict:
    for m in d.get("modules", []):
        if m.get("module") == "D":
            raw = m.get("critical_control_verdict")
            if raw:
                try:
                    return CriticalControlVerdict(raw)
                except ValueError:
                    return CriticalControlVerdict.INCOMPLETE
            return CriticalControlVerdict.INCOMPLETE
    return CriticalControlVerdict.INCOMPLETE


def recompute(d: dict) -> dict | None:
    u = d.get("uhqs") or {}
    if not isinstance(u.get("uhqs"), (int, float)):
        return None
    w = u.get("weights") or {}
    weights = {
        "w_A": w.get("protocol"), "w_B": w.get("behavior"), "w_C": w.get("telemetry"),
        "w_E": w.get("scale"), "w_F": w.get("static"),
    }
    if any(v is None for v in weights.values()):
        return None
    scores = {"A": u["S_A"], "B": u["S_B"], "C": u["S_C"], "D": u.get("C", 0.0),
              "E": u["S_E"], "F": u["S_F"]}
    measured = flags_from_report(d)
    verdict = verdict_from_report(d)
    n_measured = sum(measured.values())
    result = compute_uhqs(
        scores, weights,
        profile_class=u.get("profile_class") or "POSIX-Shell",
        containment_measured=bool(u.get("containment_measured", True)),
        assessment_status=AssessmentStatus.INCOMPLETE if n_measured < MIN_MEASURED_COMPOSITE
        else AssessmentStatus.COMPLETE,
        critical_control_verdict=verdict,
        measured_modules=measured,
    )
    return {
        "uhqs": result.uhqs,
        "grade": grade_for(result.uhqs),
        "delta_c": result.delta_c,
        "assessment_status": result.assessment_status.value,
        "measured": measured,
        "stored_delta_c": u.get("delta_c"),
        "stored_uhqs": u["uhqs"],
        "stored_grade": u.get("grade"),
    }


def patch_text(text: str, r: dict) -> str:
    text = re.sub(
        r"(FINAL COMPOSITE SCORE \(UHQS [0-9.]+\)\s*:\s*)[0-9.]+",
        lambda m: m.group(1) + f"{r['uhqs']:.2f}",
        text,
    )
    text = re.sub(
        r"(OVERALL EVALUATION GRADE\s*:\s*)GRADE [A-F] \([^)]*\)",
        lambda m: m.group(1) + r["grade"],
        text,
    )
    text = re.sub(
        r"(Assessment Status\s*:\s*)\w+",
        lambda m: m.group(1) + r["assessment_status"],
        text,
    )
    return text


def refresh_manifest(out_dir: Path, touched: list[str]) -> bool:
    mf = out_dir / "MANIFEST.json"
    if not mf.is_file():
        return False
    try:
        man = json.loads(mf.read_text())
    except json.JSONDecodeError:
        return False
    hit = False
    for art in man.get("artifacts", []):
        rel = str(art.get("path", ""))
        if rel in touched or Path(rel).name in touched:
            p = out_dir / rel
            if p.is_file():
                art["sha256"] = sha256_file(p)
                hit = True
    if hit:
        man["rescore"] = RESCORE_NOTE
        mf.write_text(json.dumps(man, indent=2) + "\n")
    return hit


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path,
                   default=ROOT / "docs/conformance/latest/results-5.0.1")
    p.add_argument("--write", action="store_true", help="apply changes (default: dry-run)")
    args = p.parse_args(argv)

    changed, delta_mismatch, total = [], [], 0
    for rj in sorted(args.root.rglob("report.json")):
        total += 1
        d = json.loads(rj.read_text())
        r = recompute(d)
        if r is None:
            continue
        if abs((r["delta_c"] or 0) - (r["stored_delta_c"] or 0)) > 1e-6:
            delta_mismatch.append(str(rj))
        if abs(r["uhqs"] - r["stored_uhqs"]) <= 0.05:
            continue
        changed.append((rj, r))
        if args.write:
            out_dir = rj.parent
            if "uhqs_pre_renorm" not in d["uhqs"]:
                # Preserve the pre-fix composite in-file: this tree is not yet
                # in git, and evaluation-proof history must stay recoverable.
                d["uhqs"]["uhqs_pre_renorm"] = {
                    k: d["uhqs"].get(k)
                    for k in ("uhqs", "grade", "assessment_status", "delta_c")
                }
            d["uhqs"]["uhqs"] = r["uhqs"]
            d["uhqs"]["grade"] = r["grade"]
            d["uhqs"]["assessment_status"] = r["assessment_status"]
            d["uhqs"]["measured_modules"] = r["measured"]
            d["uhqs"]["rescore_note"] = RESCORE_NOTE
            rj.write_text(json.dumps(d, indent=2) + "\n")
            touched = []
            for name in ("SCORECARD.txt", "REPORT.txt"):
                tp = out_dir / name
                if tp.is_file():
                    tp.write_text(patch_text(tp.read_text(), r))
                    touched.append(name)
            refresh_manifest(out_dir, ["report.json", *touched])

    print(f"artifacts scanned: {total}")
    print(f"score changes: {len(changed)}" + ("  (dry-run — nothing written)" if not args.write else "  [written]"))
    for rj, r in sorted(changed, key=lambda x: -(x[1]["uhqs"] - x[1]["stored_uhqs"]))[:20]:
        delta = r["uhqs"] - r["stored_uhqs"]
        short = r["grade"].replace("GRADE ", "").split(" (")[0]
        stored_short = str(r["stored_grade"] or "?").replace("GRADE ", "").split(" (")[0]
        print(f"  {delta:+7.2f}  {r['uhqs']:6.2f} {stored_short}->{short}  "
              f"{rj.relative_to(args.root)}  unmeasured="
              f"{[k for k, v in r['measured'].items() if not v]}")
    if delta_mismatch:
        print(f"\nWARNING delta_c mismatches ({len(delta_mismatch)}) — verdict/δ_C drift, review before trusting:")
        for m in delta_mismatch[:10]:
            print(f"  {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
