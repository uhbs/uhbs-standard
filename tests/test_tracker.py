"""Gate A tests for scripts/tracker.py."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "scripts" / "tracker.py"


def run_tracker(db: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(TRACKER), "--db", str(db), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise AssertionError(
            f"tracker {' '.join(args)} failed ({result.returncode})\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def payload(result: subprocess.CompletedProcess[str]) -> dict:
    line = result.stdout.strip().splitlines()[-1]
    return json.loads(line)


def write_manifest(path: Path, unit_id: str = "demo-http") -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "units": [
                    {
                        "unit_id": unit_id,
                        "benchmark_id": "demo",
                        "protocol_id": "http",
                        "proof_label": "Demo HTTP",
                        "upstream_repo": "https://github.com/example/demo.git",
                        "upstream_default_branch": None,
                        "upstream_commit": None,
                        "current_report_path": "docs/conformance/reports/demo",
                        "archive_path": "docs/conformance/archive/v5.0.0/demo",
                        "latest_path": "docs/conformance/latest/results-5.0.0/demo",
                        "lab_dir": "docs/conformance/labs/demo",
                        "inventory_path": "docs/conformance/labs/demo/inventory.yaml",
                        "quick_tps_path": "docs/conformance/labs/demo/web_api_http_quick.yaml",
                        "full_tps_path": "docs/conformance/labs/demo/web_api_http_full.yaml",
                        "fixture_path": None,
                        "class_name": "Web-API",
                        "target_host": "demo-lab",
                        "target_port": 80,
                        "refreshability_status": "refreshable",
                        "assigned_agent": None,
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_init_db_wal_and_schema(tmp_path: Path) -> None:
    db = tmp_path / "results-5.0.0.sqlite3"
    out = payload(run_tracker(db, "init-db"))
    assert out["ok"] is True
    assert db.is_file()
    conn = sqlite3.connect(db)
    try:
        journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal.lower() == "wal"
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        assert {
            "benchmark_units",
            "run_executions",
            "artifacts",
            "blockers",
        } <= tables
        cols = {
            row[1] for row in conn.execute("PRAGMA table_info(benchmark_units)").fetchall()
        }
        assert "unit_id" in cols
        assert "refreshability_status" in cols
    finally:
        conn.close()


def test_import_and_atomic_claim(tmp_path: Path) -> None:
    db = tmp_path / "t.sqlite3"
    manifest = tmp_path / "manifest.yaml"
    write_manifest(manifest)
    run_tracker(db, "init-db")
    imported = payload(run_tracker(db, "import-manifest", "--manifest", str(manifest)))
    assert imported["imported"] == 1

    first = payload(run_tracker(db, "claim-unit", "--unit-id", "demo-http", "--agent", "worker-a"))
    assert first["claimed"] is True
    assert first["unit"]["assigned_agent"] == "worker-a"
    assert first["unit"]["refreshability_status"] == "assigned"

    second = run_tracker(
        db, "claim-unit", "--unit-id", "demo-http", "--agent", "worker-b", check=False
    )
    assert second.returncode != 0
    failed = payload(second)
    assert failed["ok"] is False
    assert failed["claimed"] is False

    conn = sqlite3.connect(db)
    try:
        agent = conn.execute(
            "SELECT assigned_agent FROM benchmark_units WHERE unit_id='demo-http'"
        ).fetchone()[0]
        assert agent == "worker-a"
    finally:
        conn.close()


def test_claim_next_empty_when_all_assigned(tmp_path: Path) -> None:
    db = tmp_path / "t.sqlite3"
    manifest = tmp_path / "manifest.yaml"
    write_manifest(manifest)
    run_tracker(db, "init-db")
    run_tracker(db, "import-manifest", "--manifest", str(manifest))
    claimed = payload(run_tracker(db, "claim-next", "--agent", "worker-1"))
    assert claimed["unit_id"] == "demo-http"
    empty = payload(run_tracker(db, "claim-next", "--agent", "worker-2"))
    assert empty["unit_id"] is None


def test_run_start_finish_blocker_and_fixture(tmp_path: Path) -> None:
    db = tmp_path / "t.sqlite3"
    manifest = tmp_path / "manifest.yaml"
    write_manifest(manifest)
    run_tracker(db, "init-db")
    run_tracker(db, "import-manifest", "--manifest", str(manifest))
    run_tracker(db, "claim-unit", "--unit-id", "demo-http", "--agent", "worker-a")

    started = payload(
        run_tracker(
            db,
            "log-run-start",
            "--unit-id",
            "demo-http",
            "--mode",
            "quick",
            "--base-image",
            "ubuntu:latest",
            "--base-image-reason",
            "default wrapper",
            "--strategy",
            "ubuntu-wrapper",
            "--airgap-attested",
        )
    )
    assert started["run_mode"] == "quick"
    assert started["run_id"]

    out_dir = tmp_path / "quick"
    out_dir.mkdir()
    (out_dir / "SCORECARD.txt").write_text("grade\n", encoding="utf-8")
    (out_dir / "REPORT.txt").write_text("report\n", encoding="utf-8")
    (out_dir / "report.json").write_text(
        json.dumps({"uhqs": {"uhqs": 12.5, "grade": "F", "delta_c": 0.5, "S_A": 1}}),
        encoding="utf-8",
    )
    (out_dir / "MANIFEST.json").write_text("{}", encoding="utf-8")
    (out_dir / "run-meta.json").write_text("{}", encoding="utf-8")
    (out_dir / "uhbs-run.log").write_text("ok\n", encoding="utf-8")
    (out_dir / "README.md").write_text("readme\n", encoding="utf-8")

    finished = payload(
        run_tracker(
            db,
            "log-run-finish",
            "--unit-id",
            "demo-http",
            "--mode",
            "quick",
            "--out-dir",
            str(out_dir),
        )
    )
    assert finished["run_status"] == "succeeded"
    assert any(a["type"] == "scorecard" and a["exists"] for a in finished["artifacts"])

    blocked = payload(
        run_tracker(
            db,
            "log-blocker",
            "--unit-id",
            "demo-http",
            "--stage",
            "full-run",
            "--summary",
            "uhbs full run failed",
            "--log-path",
            str(out_dir / "uhbs-run.log"),
        )
    )
    assert blocked["blocker_id"]
    assert blocked["stage"] == "full-run"

    fixture = tmp_path / "demo.scorecard.json"
    fixture.write_text("{}", encoding="utf-8")
    set_fx = payload(
        run_tracker(
            db,
            "set-fixture",
            "--unit-id",
            "demo-http",
            "--fixture-path",
            str(fixture),
        )
    )
    assert "demo.scorecard.json" in set_fx["fixture_path"]

    conn = sqlite3.connect(db)
    try:
        status = conn.execute(
            "SELECT refreshability_status FROM benchmark_units WHERE unit_id='demo-http'"
        ).fetchone()[0]
        assert status.startswith("blocked")
        n_runs = conn.execute("SELECT COUNT(*) FROM run_executions").fetchone()[0]
        assert n_runs == 1
        n_art = conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]
        assert n_art >= 1
        n_block = conn.execute("SELECT COUNT(*) FROM blockers").fetchone()[0]
        assert n_block == 1
    finally:
        conn.close()


def test_sync_ledger(tmp_path: Path) -> None:
    db = tmp_path / "t.sqlite3"
    manifest = tmp_path / "manifest.yaml"
    ledger = tmp_path / "RUN-LEDGER.md"
    write_manifest(manifest)
    run_tracker(db, "init-db")
    run_tracker(db, "import-manifest", "--manifest", str(manifest))
    run_tracker(db, "sync-ledger", "--ledger", str(ledger), "--declare-gate-d-open")
    text = ledger.read_text(encoding="utf-8")
    assert "demo-http" in text
    assert "Gate D:** OPEN" in text
    assert "refreshable" in text
    assert "## Notes" in text
    assert "_No legacy-closure notes._" in text


def test_log_blocker_classification_keeps_legacy_status(tmp_path: Path) -> None:
    db = tmp_path / "t.sqlite3"
    manifest = tmp_path / "manifest.yaml"
    ledger = tmp_path / "RUN-LEDGER.md"
    write_manifest(manifest, unit_id="acra-legacy")
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    data["units"][0]["refreshability_status"] = "legacy-not-refreshed"
    data["units"][0]["benchmark_id"] = "acra"
    data["units"][0]["protocol_id"] = "legacy"
    manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    run_tracker(db, "init-db")
    run_tracker(db, "import-manifest", "--manifest", str(manifest))
    blocked = payload(
        run_tracker(
            db,
            "log-blocker",
            "--unit-id",
            "acra-legacy",
            "--stage",
            "classification",
            "--blocker-type",
            "classification",
            "--status",
            "legacy-not-refreshed",
            "--summary",
            (
                "legacy-not-refreshed: no usable inventory + quick/full TPS. "
                "Closed without new UHQS scores."
            ),
        )
    )
    assert blocked["blocker_id"]
    run_tracker(db, "sync-ledger", "--ledger", str(ledger), "--declare-gate-d-open")
    conn = sqlite3.connect(db)
    try:
        status = conn.execute(
            "SELECT refreshability_status FROM benchmark_units WHERE unit_id='acra-legacy'"
        ).fetchone()[0]
        scored = conn.execute(
            "SELECT COUNT(*) FROM run_executions WHERE uhqs IS NOT NULL"
        ).fetchone()[0]
    finally:
        conn.close()
    assert status == "legacy-not-refreshed"
    assert scored == 0
    text = ledger.read_text(encoding="utf-8")
    assert "## Notes" in text
    assert "`acra-legacy`" in text
    assert "Closed without new UHQS scores." in text
    # Classification blockers are notes, not open execution blockers.
    assert "_None._" in text
