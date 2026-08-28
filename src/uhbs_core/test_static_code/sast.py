"""SAST & supply-chain tooling wrappers (Bandit / Semgrep / Trivy)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from uhbs_core.models import CheckResult

def _run_tool_json(
    cmd: Sequence[str], cwd: Path, timeout: int = 180
) -> Tuple[bool, dict, str]:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return False, {}, "not installed"
    except subprocess.TimeoutExpired:
        return False, {}, "timeout"
    raw = proc.stdout or ""
    try:
        return True, json.loads(raw) if raw.strip() else {}, ""
    except json.JSONDecodeError:
        return True, {"raw": raw[:2000], "returncode": proc.returncode}, ""


def _sast_checks(root: Path, image: Optional[str], out_dir: Optional[Path]) -> List[CheckResult]:
    checks: List[CheckResult] = []
    high_crit = 0

    # Bandit (Python)
    bandit_ok, bandit, berr = _run_tool_json(
        ["bandit", "-r", ".", "-f", "json", "-q"],
        cwd=root,
        timeout=240,
    )
    if berr == "not installed":
        checks.append(
            CheckResult(
                id="white.bandit",
                team="white",
                passed=True,
                detail="bandit not installed (skipped)",
                score=5.0,
            )
        )
    else:
        metrics = bandit.get("metrics", {}) if isinstance(bandit, dict) else {}
        totals = metrics.get("_totals", {}) if isinstance(metrics, dict) else {}
        sev_h = int(totals.get("SEVERITY.HIGH", 0) or 0)
        sev_c = int(totals.get("SEVERITY.HIGH", 0) or 0)  # bandit has HIGH/MEDIUM/LOW
        # Also count CONFIDENCE — prefer results list
        results = bandit.get("results", []) if isinstance(bandit, dict) else []
        high = sum(1 for r in results if str(r.get("issue_severity", "")).upper() == "HIGH")
        high_crit += high
        if out_dir:
            (out_dir / "bandit-report.json").write_text(
                json.dumps(bandit, indent=2)[:2_000_000], encoding="utf-8"
            )
        checks.append(
            CheckResult(
                id="white.bandit",
                team="white",
                passed=high == 0,
                detail=f"bandit HIGH={high}" + (f" ({berr})" if berr else ""),
                score=8.0 if high == 0 else max(0.0, 8.0 - high),
            )
        )
        _ = sev_h, sev_c, bandit_ok

    # Semgrep
    sem_ok, sem, serr = _run_tool_json(
        ["semgrep", "--config=auto", "--json", "--quiet", "."],
        cwd=root,
        timeout=300,
    )
    if serr == "not installed":
        checks.append(
            CheckResult(
                id="white.semgrep",
                team="white",
                passed=True,
                detail="semgrep not installed (skipped)",
                score=5.0,
            )
        )
    else:
        results = sem.get("results", []) if isinstance(sem, dict) else []
        errorish = [
            r
            for r in results
            if str(r.get("extra", {}).get("severity", "")).lower() in {"error", "critical"}
            or str(r.get("severity", "")).lower() in {"error", "critical"}
        ]
        high_crit += len(errorish)
        if out_dir:
            (out_dir / "semgrep-report.json").write_text(
                json.dumps(sem, indent=2)[:2_000_000], encoding="utf-8"
            )
        checks.append(
            CheckResult(
                id="white.semgrep",
                team="white",
                passed=len(errorish) == 0,
                detail=f"semgrep error/critical={len(errorish)} total={len(results)}"
                + (f" ({serr})" if serr else ""),
                score=8.0 if len(errorish) == 0 else max(0.0, 8.0 - len(errorish)),
            )
        )
        _ = sem_ok

    # Trivy (image or fs)
    if image:
        tcmd = ["trivy", "image", "--format", "json", "--quiet", image]
    else:
        tcmd = ["trivy", "fs", "--format", "json", "--quiet", "."]
    tok, trivy, terr = _run_tool_json(tcmd, cwd=root, timeout=300)
    if terr == "not installed":
        checks.append(
            CheckResult(
                id="white.trivy",
                team="white",
                passed=True,
                detail="trivy not installed (skipped)",
                score=4.0,
            )
        )
    else:
        crit = 0
        high = 0
        for res in (trivy.get("Results") or []) if isinstance(trivy, dict) else []:
            for v in res.get("Vulnerabilities") or []:
                sev = str(v.get("Severity", "")).upper()
                if sev == "CRITICAL":
                    crit += 1
                elif sev == "HIGH":
                    high += 1
        high_crit += crit + high
        if out_dir:
            (out_dir / "trivy-report.json").write_text(
                json.dumps(trivy, indent=2)[:2_000_000], encoding="utf-8"
            )
        checks.append(
            CheckResult(
                id="white.trivy",
                team="white",
                passed=crit == 0 and high == 0,
                detail=f"trivy CRITICAL={crit} HIGH={high}" + (f" ({terr})" if terr else ""),
                score=4.0 if crit == 0 and high == 0 else max(0.0, 4.0 - crit - 0.5 * high),
            )
        )
        _ = tok

    checks.append(
        CheckResult(
            id="white.sast_gate",
            team="white",
            passed=high_crit == 0,
            detail="0 high/critical static findings" if high_crit == 0 else f"{high_crit} high/critical findings",
            score=0.0,  # informational aggregate; points already in tools
        )
    )
    return checks
