"""Filesystem helpers and scan constants for Module F static audit."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

# Package lives at uhbs_core/test_static_code/; coverage lists stay under uhbs_core/profiles/.
ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".local",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".cursor",
    "testdata",
    "honeyfs",  # fake FS content trees are expected decoy data
}

TEXT_SUFFIXES = {
    ".py",
    ".go",
    ".rs",
    ".js",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".md",
    ".txt",
    ".cfg",
    ".ini",
    ".sh",
    ".bash",
    ".env.example",
}

PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |ED25519 )?PRIVATE KEY-----"
)
SSH_BANNER_RE = re.compile(
    r"""(?:ServerVersion|versionString|banner)\s*=\s*['\"]SSH-[^'\"]+['\"]""",
    re.IGNORECASE,
)
RANDOM_SEED_RE = re.compile(r"random\.seed\s*\(|rand\.Seed\s*\(|math/rand\.Seed")
MAC_RE = re.compile(r"(?:['\"])(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}(?:['\"])")
WEAK_PROMPT_BOUNDARIES = [
    re.compile(r"ignore\s+previous\s+instructions", re.I),
    re.compile(r"you\s+are\s+chatgpt", re.I),
    re.compile(r"SYSTEM\s*PROMPT\s*:", re.I),
]
FALLBACK_LEAK_RE = re.compile(
    # Bare "hallucin" matches the target decoy brand — require real leak phrases.
    r"(as an ai|language model|i cannot actually execute|llm fallback|"
    r"hallucinat(?:e|es|ed|ing|ion)s?)",
    re.I,
)


def _iter_files(root: Path, limit: int = 8000) -> Iterable[Path]:
    n = 0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix and p.suffix.lower() not in TEXT_SUFFIXES and p.name not in (
            "Dockerfile",
            "Makefile",
        ):
            # still scan key-like filenames without suffix filter bypass for *.pem
            if p.suffix.lower() not in {".pem", ".key", ".pub"}:
                continue
        yield p
        n += 1
        if n >= limit:
            return


def _read(path: Path, max_bytes: int = 512_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return ""
    return data.decode("utf-8", errors="ignore")

