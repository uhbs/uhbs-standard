#!/usr/bin/env python3
"""Bump or verify UHBS version strings.

Source of truth: ``src/uhbs_core/_version.py`` (``__version__``).

Runtime Python packages import that value. Static mirrors (schemas, fixtures,
docs, Docker tags, discovery files, web copy) are updated by this script.

Usage::

    python scripts/bump_version.py 4.5.3
    python scripts/bump_version.py --check

Never rewrite ``web/package-lock.json`` (or other lockfiles) — lockfile package
versions can collide with the UHBS semver and break Pages deploys.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "src" / "uhbs_core" / "_version.py"
VERSION_RE = re.compile(r'^__version__\s*=\s*"([^"]+)"\s*$', re.M)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".tox",
}
SKIP_FILE_NAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.lock",
    "poetry.lock",
    "uv.lock",
}
# Binary / non-text — never rewrite
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".zip",
    ".gz",
    ".whl",
    ".pyc",
    ".so",
    ".dylib",
    ".mp4",
    ".webm",
    ".cast",
}

# Files that MUST mention the SoT version (mirrors / packaging metadata).
REQUIRED_MIRRORS = (
    "AGENTS.md",
    "VERSIONING.md",
    "CITATION.cff",
    "server.json",
    "Dockerfile",
    "Dockerfile.full",
    "docker-compose.yml",
    "llms.txt",
    "schemas/scorecard.schema.json",
    "src/uhbs_cli/schemas/scorecard.schema.json",
)


def read_version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if not match:
        raise SystemExit(f"could not parse __version__ in {VERSION_FILE}")
    return match.group(1)


def write_version(new: str) -> None:
    text = VERSION_FILE.read_text(encoding="utf-8")
    updated, n = VERSION_RE.subn(f'__version__ = "{new}"', text, count=1)
    if n != 1:
        raise SystemExit(f"failed to rewrite __version__ in {VERSION_FILE}")
    VERSION_FILE.write_text(updated, encoding="utf-8")


def iter_text_files() -> list[Path]:
    out: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.name in SKIP_FILE_NAMES:
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if path.resolve() == VERSION_FILE.resolve():
            continue
        # CHANGELOG historical entries are handled separately
        if path.name == "CHANGELOG.md" and path.parent == ROOT:
            continue
        out.append(path)
    return out


def replace_in_file(path: Path, old: str, new: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    if old not in text:
        return False
    path.write_text(text.replace(old, new), encoding="utf-8")
    return True


def update_changelog(old: str, new: str) -> None:
    path = ROOT / "CHANGELOG.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    # Current advertised version in the preamble only.
    text2 = text.replace(f"share version **{old}**", f"share version **{new}**", 1)
    if f"## [{new}]" not in text2:
        stub = (
            f"## [Unreleased]\n\n"
            f"## [{new}] — TBD\n\n"
            f"Patch/minor release placeholder. **UHQS math unchanged** unless noted.\n\n"
            f"### Changed\n"
            f"- Spec/package/schema/`uhbs_version` fixtures aligned to **{new}**\n\n"
        )
        text2 = text2.replace("## [Unreleased]\n\n", stub, 1)
    if text2 != text:
        path.write_text(text2, encoding="utf-8")


def bump(new: str) -> int:
    if not SEMVER_RE.match(new):
        raise SystemExit(f"version must look like X.Y.Z, got {new!r}")
    old = read_version()
    if old == new:
        print(f"already at {new}; syncing mirrors anyway")
    write_version(new)
    changed = [VERSION_FILE.relative_to(ROOT).as_posix()]
    for path in iter_text_files():
        if replace_in_file(path, old, new):
            changed.append(path.relative_to(ROOT).as_posix())
    update_changelog(old, new)
    if (ROOT / "CHANGELOG.md").is_file():
        changed.append("CHANGELOG.md")
    print(f"bumped {old} → {new}")
    print(f"updated {len(changed)} paths (incl. SoT)")
    return 0


def check() -> int:
    version = read_version()
    errors: list[str] = []

    # Package imports must agree
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from uhbs_cli import __version__ as cli_v
        from uhbs_core import __version__ as core_v
        from uhbs_mcp import __version__ as mcp_v
    except Exception as exc:  # noqa: BLE001 — surface import problems clearly
        errors.append(f"import failed: {exc}")
    else:
        for label, value in (("uhbs_core", core_v), ("uhbs_cli", cli_v), ("uhbs_mcp", mcp_v)):
            if value != version:
                errors.append(f"{label}.__version__={value!r} != SoT {version!r}")

    # No second Python assignment of package version
    assign_re = re.compile(r'^__version__\s*=\s*"[^"]+"\s*$', re.M)
    for path in (ROOT / "src").rglob("*.py"):
        if path.name == "_version.py":
            continue
        text = path.read_text(encoding="utf-8")
        if assign_re.search(text):
            errors.append(f"duplicate __version__ assignment in {path.relative_to(ROOT)}")

    for rel in REQUIRED_MIRRORS:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing required mirror {rel}")
            continue
        if version not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel} does not contain SoT version {version}")

    if errors:
        print("version check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"version check OK ({version})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "version",
        nargs="?",
        help="New semver (X.Y.Z). Omit with --check.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify runtime imports and required mirrors match SoT.",
    )
    args = parser.parse_args(argv)
    if args.check:
        return check()
    if not args.version:
        parser.error("provide X.Y.Z or --check")
    return bump(args.version)


if __name__ == "__main__":
    raise SystemExit(main())
