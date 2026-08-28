"""Module F entrypoints: ``run`` and CLI ``main``."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List, Optional

from uhbs_core.hqs import pass_status
from uhbs_core.models import CheckResult, ModuleResult, TargetSpec

from .artifacts import _scan_artifacts
from .coverage import _coverage_review
from .fs import _iter_files, _read
from .prompts import _scan_prompts
from .sast import _sast_checks

def run(
    target: TargetSpec,
    out_dir: Optional[Path] = None,
    skip_sast_tools: bool = False,
) -> ModuleResult:
    if not target.source_root:
        return ModuleResult(
            module="F",
            dimension="static",
            score=0.0,
            status="SKIPPED",
            notes=["no source_root configured"],
        )
    root = Path(target.source_root).expanduser().resolve()
    if not root.is_dir():
        return ModuleResult(
            module="F",
            dimension="static",
            score=0.0,
            status="FAILED",
            error=f"source_root not found: {root}",
        )

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    checks: List[CheckResult] = []
    checks.extend(_scan_artifacts(root))
    checks.extend(_scan_prompts(root))
    if skip_sast_tools:
        checks.append(
            CheckResult(
                id="white.sast_tools",
                team="white",
                passed=True,
                detail="SAST tools skipped by flag",
                score=15.0,
            )
        )
    else:
        checks.extend(_sast_checks(root, target.container_image, out_dir))
    checks.extend(_coverage_review(root, target.kind, target.profile_class))

    # Blocking / async heuristic (efficiency static focus from matrix)
    blocking_hits = 0
    for fp in _iter_files(root, limit=2000):
        if fp.suffix not in {".py", ".go"}:
            continue
        text = _read(fp, max_bytes=120_000)
        if re.search(r"time\.sleep\s*\(\s*[1-9]", text) or "time.Sleep(" in text:
            # only count outside tests lightly
            if "test" not in str(fp).lower():
                blocking_hits += 1
    checks.append(
        CheckResult(
            id="white.blocking_calls",
            team="white",
            passed=blocking_hits < 25,
            detail=f"sleep/blocking markers in non-test code≈{blocking_hits}",
            score=5.0 if blocking_hits < 25 else 1.0,
        )
    )

    score = min(100.0, sum(c.score for c in checks))
    # Normalize roughly: max theoretical ~25+25+25+25+5 ≈ 105 with skips
    score = min(100.0, score)

    # Hard gate note: high/critical SAST findings should keep F from looking perfect
    sast_gate = next((c for c in checks if c.id == "white.sast_gate"), None)
    if sast_gate and not sast_gate.passed:
        score = min(score, 70.0)

    return ModuleResult(
        module="F",
        dimension="static",
        score=round(score, 2),
        status=pass_status(score),
        checks=checks,
        metrics={"source_root": str(root)},
        notes=["Module F white-box audit (keys/prompts/SAST/VFS)"],
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Module F: Source Code & Static Audit")
    p.add_argument("--repo-path", "--source-root", dest="repo_path", required=True)
    p.add_argument("--kind", default="generic")
    p.add_argument("--output", default="static-report.json")
    p.add_argument("--container-image", default=None)
    p.add_argument("--skip-sast-tools", action="store_true")
    args = p.parse_args()
    t = TargetSpec(
        name=Path(args.repo_path).name,
        kind=args.kind,
        source_root=args.repo_path,
        container_image=args.container_image,
    )
    out = Path(args.output).resolve().parent
    result = run(t, out_dir=out, skip_sast_tools=args.skip_sast_tools)
    Path(args.output).write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(f"Module F static score={result.score} status={result.status}")
    for c in result.checks:
        print(f"  [{c.team}] {c.id}: {'PASS' if c.passed else 'FAIL'} — {c.detail}")
    return 0 if result.status != "FAILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
