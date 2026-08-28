"""LLM prompt & guardrail boundary audit."""
from __future__ import annotations

from pathlib import Path
from typing import List, Set

from uhbs_core.models import CheckResult

from .fs import FALLBACK_LEAK_RE, WEAK_PROMPT_BOUNDARIES, _iter_files, _read

def _scan_prompts(root: Path) -> List[CheckResult]:
    prompt_dirs = [
        root / "prompts",
        root / "personas",
        root / "engine" / "internal" / "persona",
        root / "services" / "ai-broker",
    ]
    files: List[Path] = []
    for d in prompt_dirs:
        if d.is_dir():
            files.extend([p for p in d.rglob("*") if p.is_file()])
    # Also catch *prompt* filenames
    for p in _iter_files(root, limit=3000):
        if "prompt" in p.name.lower() or p.suffix in {".txt", ".md"} and "persona" in str(p).lower():
            files.append(p)
    # unique
    uniq: List[Path] = []
    seen: Set[str] = set()
    for f in files:
        s = str(f)
        if s not in seen:
            seen.add(s)
            uniq.append(f)

    weak = 0
    leak = 0
    samples: List[str] = []
    for fp in uniq[:200]:
        # Test fixtures intentionally contain extraction-attack strings; skip them.
        parts = {p.lower() for p in fp.parts}
        name_l = fp.name.lower()
        if (
            "tests" in parts
            or "testdata" in parts
            or "__pycache__" in parts
            or ".venv" in parts
            or name_l.endswith("_test.py")
            or name_l.endswith("_test.go")
            or name_l.startswith("test_")
            or name_l.endswith(".pyc")
            or name_l.endswith(".pyo")
        ):
            continue
        text = _read(fp)
        try:
            rel = str(fp.relative_to(root))
        except ValueError:
            rel = str(fp)
        if any(r.search(text) for r in WEAK_PROMPT_BOUNDARIES):
            weak += 1
            samples.append(f"weak-boundary:{rel}")
        if FALLBACK_LEAK_RE.search(text):
            leak += 1
            samples.append(f"fallback-leak:{rel}")

    # Missing prompt corpus is not a failure for non-LLM honeypots
    has_prompts = len(uniq) > 0
    boundary_ok = weak == 0
    leak_ok = leak == 0
    return [
        CheckResult(
            id="white.prompt_corpus_present",
            team="white",
            passed=True,
            detail=f"{len(uniq)} prompt/persona files scanned" if has_prompts else "no prompt corpus (N/A for non-LLM)",
            score=5.0 if has_prompts else 5.0,
        ),
        CheckResult(
            id="white.prompt_boundaries",
            team="white",
            passed=boundary_ok,
            detail="no weak delimiter/extract patterns" if boundary_ok else f"{weak} weak boundary hits",
            score=10.0 if boundary_ok else 2.0,
            evidence=samples[:8],
        ),
        CheckResult(
            id="white.fallback_strings",
            team="white",
            passed=leak_ok,
            detail="no plain-text LLM fallback artifacts" if leak_ok else f"{leak} fallback leak hits",
            score=10.0 if leak_ok else 2.0,
            evidence=[s for s in samples if s.startswith("fallback")][:8],
        ),
    ]
