#!/usr/bin/env python3
"""Deterministic per-unit verifier for the results-5.0.0 refresh.

Exit 0 only when quick+full artifacts, non-empty full-run.cast, EXECUTION-STEPS.md,
valid JSON, MANIFEST hashes, fixture status, SQLite rows, upstream SHA, and
base_image / runtime strategy fields are coherent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".local" / "benchmark-refresh" / "results-5.0.0.sqlite3"

QUICK_FILES = (
    "README.md",
    "SCORECARD.txt",
    "REPORT.txt",
    "report.json",
    "MANIFEST.json",
    "run-meta.json",
    "uhbs-run.log",
)
FULL_FILES = QUICK_FILES
JSON_FILES = ("report.json", "MANIFEST.json", "run-meta.json")
SUCCESS_STATUSES = frozenset({"succeeded", "success", "ok"})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def resolve(root: Path, maybe: str | None) -> Path | None:
    if not maybe:
        return None
    path = Path(maybe)
    if path.is_absolute():
        return path
    return root / path


def latest_run(conn: sqlite3.Connection, unit_id: str, mode: str) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT * FROM run_executions
        WHERE unit_id = ? AND run_mode = ?
        ORDER BY COALESCE(finished_at, started_at) DESC
        LIMIT 1
        """,
        (unit_id, mode),
    ).fetchone()


def check_json(path: Path, errors: list[str], label: str) -> dict | None:
    if not path.is_file():
        errors.append(f"{label}: missing JSON file {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON in {path}: {exc}")
        return None


def check_manifest_hashes(directory: Path, errors: list[str], label: str) -> None:
    manifest_path = directory / "MANIFEST.json"
    data = check_json(manifest_path, errors, label)
    if not data:
        return
    entries = data.get("artifacts") or data.get("files") or []
    if isinstance(entries, dict):
        items = [{"path": k, "sha256": v} for k, v in entries.items()]
    else:
        items = list(entries)
    if not items:
        errors.append(f"{label}: MANIFEST.json has no artifacts/files entries")
        return
    for item in items:
        if isinstance(item, str):
            rel_path, expected = item, None
        else:
            rel_path = item.get("path") or item.get("rel_path")
            expected = item.get("sha256") or item.get("hash")
        if not rel_path:
            errors.append(f"{label}: MANIFEST entry missing path")
            continue
        if Path(rel_path).name == "MANIFEST.json":
            continue
        target = directory / rel_path
        if not target.is_file():
            errors.append(f"{label}: MANIFEST lists missing file {rel_path}")
            continue
        if expected:
            actual = sha256_file(target)
            if actual != expected:
                errors.append(f"{label}: hash mismatch for {rel_path}: {actual} != {expected}")


def check_artifact_dir(directory: Path, mode: str, errors: list[str]) -> None:
    label = mode
    if not directory.is_dir():
        errors.append(f"{label}: directory missing: {directory}")
        return
    required = FULL_FILES if mode == "full" else QUICK_FILES
    for name in required:
        path = directory / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"{label}: required file missing or empty: {path}")
    for name in JSON_FILES:
        check_json(directory / name, errors, label)
    if (directory / "MANIFEST.json").is_file():
        check_manifest_hashes(directory, errors, label)
    if mode == "full":
        static_dir = directory / "static"
        if not static_dir.is_dir():
            errors.append(f"{label}: static/ directory missing: {static_dir}")
        cast = directory / "proof" / "full-run.cast"
        if not cast.is_file() or cast.stat().st_size == 0:
            errors.append(f"{label}: full-run.cast missing or empty: {cast}")


def validate_unit(unit_id: str, db_path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    if not db_path.is_file():
        return [f"database missing: {db_path}"]
    conn = connect(db_path)
    try:
        unit = conn.execute(
            "SELECT * FROM benchmark_units WHERE unit_id = ?", (unit_id,)
        ).fetchone()
        if unit is None:
            return [f"unknown unit_id: {unit_id}"]
        latest = resolve(root, unit["latest_path"])
        if latest is None:
            errors.append("latest_path is empty")
            latest = root
        steps = latest / "EXECUTION-STEPS.md"
        if not steps.is_file() or steps.stat().st_size == 0:
            errors.append(f"EXECUTION-STEPS.md missing or empty: {steps}")
        if not (unit["upstream_commit"] or "").strip():
            errors.append("upstream_commit is not recorded on the unit")
        fixture_path = resolve(root, unit["fixture_path"]) if unit["fixture_path"] else None
        if unit["fixture_path"]:
            if fixture_path is None or not fixture_path.is_file():
                errors.append(f"fixture_path does not exist: {unit['fixture_path']}")
        else:
            errors.append("fixture_path is unset (fixture status must be explicit)")

        check_artifact_dir(latest / "quick", "quick", errors)
        check_artifact_dir(latest / "full", "full", errors)

        quick = latest_run(conn, unit_id, "quick")
        full = latest_run(conn, unit_id, "full")
        if quick is None:
            errors.append("SQLite missing run_executions row for quick")
        if full is None:
            errors.append("SQLite missing run_executions row for full")
        if full is not None:
            if full["run_status"] in SUCCESS_STATUSES or full["run_status"] == "running":
                if not (full["cast_path"] or "").strip():
                    errors.append("full run_executions.cast_path is empty")
                else:
                    cast = resolve(root, full["cast_path"])
                    if cast is None or not cast.is_file() or cast.stat().st_size == 0:
                        errors.append(f"SQLite cast_path missing or empty: {full['cast_path']}")
            if not (full["base_image"] or "").strip():
                errors.append("full run_executions.base_image is not recorded")
            if not (full["container_runtime_strategy"] or "").strip():
                errors.append("full run_executions.container_runtime_strategy is not recorded")
            artifacts = conn.execute(
                "SELECT * FROM artifacts WHERE run_id = ?", (full["run_id"],)
            ).fetchall()
            if not artifacts:
                errors.append("SQLite missing artifacts rows for the full run")
        if quick is not None:
            artifacts = conn.execute(
                "SELECT * FROM artifacts WHERE run_id = ?", (quick["run_id"],)
            ).fetchall()
            if not artifacts:
                errors.append("SQLite missing artifacts rows for the quick run")
    finally:
        conn.close()
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate one refresh unit")
    parser.add_argument("--unit-id", required=True)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    errors = validate_unit(args.unit_id, Path(args.db), Path(args.root))
    if errors:
        print(f"FAIL {args.unit_id}", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print(f"OK {args.unit_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
