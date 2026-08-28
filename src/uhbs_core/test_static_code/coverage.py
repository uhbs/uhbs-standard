"""POSIX VFS and OT/Modbus coverage checks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

from uhbs_core.models import CheckResult

from .fs import ROOT, _iter_files, _read

def _posix_list() -> List[str]:
    path = ROOT / "profiles" / "coverage" / "posix_commands.txt"
    cmds: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cmds.append(line)
    return cmds


def _ot_list() -> List[str]:
    path = ROOT / "profiles" / "coverage" / "ot_modbus_coverage.txt"
    items: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        items.append(line)
    return items


def _coverage_review(root: Path, kind: str, profile_class: str) -> List[CheckResult]:
    """F3 — POSIX VFS and/or OT register-map coverage."""
    out: List[CheckResult] = []
    # POSIX
    posix = _vfs_coverage(root, kind)
    out.append(posix)

    # OT / ICS register & function coverage
    if profile_class in {"ICS-SCADA"} or kind in {"modbus"}:
        terms = _ot_list()
        focus = [
            root / "engine" / "internal" / "protocol" / "modbus",
            root,
        ]
        blobs: List[str] = []
        for base in focus:
            if not base.exists():
                continue
            for fp in _iter_files(base if base.is_dir() else root, limit=3000):
                blobs.append(_read(fp, max_bytes=150_000))
        blob = "\n".join(blobs).lower()
        found = {t for t in terms if t.lower().replace("_", " ") in blob or t.lower() in blob}
        cov = len(found) / max(len(terms), 1)
        out.append(
            CheckResult(
                id="white.ot_register_coverage",
                team="white",
                passed=cov >= 0.30,
                detail=f"OT/Modbus coverage {cov:.0%} ({len(found)}/{len(terms)})",
                score=round(25.0 * cov, 2),
                evidence=sorted(found)[:40],
            )
        )
    return out


def _vfs_coverage(root: Path, kind: str) -> CheckResult:
    cmds = _posix_list()
    text_blobs: List[str] = []
    focus: List[Path] = [root]
    if kind == "research":
        focus = [
            root / "engine" / "internal" / "protocol" / "ssh",
            root / "engine" / "internal" / "decoyfs",
        ]
    elif kind == "cowrie":
        focus = [
            root / "src" / "cowrie" / "commands",
            root / "cowrie" / "commands",
            root / "src" / "cowrie" / "shell",
        ]
    found: Set[str] = set()
    for base in focus:
        if not base.exists():
            continue
        for fp in _iter_files(base if base.is_dir() else root, limit=4000):
            text_blobs.append(_read(fp, max_bytes=200_000))
    blob = "\n".join(text_blobs).lower()
    for c in cmds:
        if re.search(rf"(?:^|[^a-z0-9_]){re.escape(c.lower())}(?:[^a-z0-9_]|$)", blob):
            found.add(c)
    coverage = len(found) / max(len(cmds), 1)
    return CheckResult(
        id="white.vfs_posix_coverage",
        team="white",
        passed=coverage >= 0.35,
        detail=f"POSIX coverage {coverage:.0%} ({len(found)}/{len(cmds)})",
        score=round(25.0 * coverage, 2),
        evidence=sorted(found)[:40],
    )
