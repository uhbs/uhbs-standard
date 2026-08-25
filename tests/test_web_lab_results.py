"""Integrity checks for landing-hub published lab results data."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "web" / "src" / "data" / "labResults.json"
FILTERS = ROOT / "web" / "src" / "data" / "protocolFilters.json"

REQUIRED = {
    "name",
    "classLabel",
    "protocol",
    "protocolLabel",
    "repo",
    "repoUpdated",
    "uhqsQuick",
    "uhqsFull",
    "gradeQuick",
    "gradeFull",
    "hub",
    "tutorial",
    "methodology",
    "scorecard",
    "quick",
    "full",
    "quickCard",
    "fullCard",
}


def test_lab_results_file_exists() -> None:
    assert LAB.is_file()
    assert FILTERS.is_file()


def test_lab_results_non_empty_and_unique_names() -> None:
    rows = json.loads(LAB.read_text(encoding="utf-8"))
    assert isinstance(rows, list)
    assert len(rows) >= 20
    names = [r["name"] + "|" + r["protocol"] for r in rows]
    assert len(names) == len(set(names))


def test_lab_results_schema_fields() -> None:
    rows = json.loads(LAB.read_text(encoding="utf-8"))
    for row in rows:
        missing = REQUIRED - set(row)
        assert not missing, f"{row.get('name')}: missing {missing}"
        assert isinstance(row["name"], str) and row["name"]
        assert row["repo"].startswith("http")
        assert row["hub"].startswith("mkdocs/")
        for key in ("uhqsQuick", "uhqsFull"):
            val = row[key]
            assert val is None or isinstance(val, (int, float))
        for key in ("gradeQuick", "gradeFull"):
            assert isinstance(row[key], str)


def test_protocol_filters_cover_lab_protocols() -> None:
    rows = json.loads(LAB.read_text(encoding="utf-8"))
    filters = json.loads(FILTERS.read_text(encoding="utf-8"))
    ids = {f["id"] for f in filters}
    assert "all" in ids
    protocols = {r["protocol"] for r in rows}
    missing = protocols - ids
    assert not missing, f"PROTOCOL_FILTERS missing ids: {sorted(missing)}"
