"""Gate A tests for scripts/validate_unit.py."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "scripts" / "tracker.py"
VALIDATE = ROOT / "scripts" / "validate_unit.py"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_py(script: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"{script.name} {' '.join(args)} failed ({result.returncode})\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def write_manifest(path: Path, latest: str, fixture: str) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "units": [
                    {
                        "unit_id": "demo-http",
                        "benchmark_id": "demo",
                        "protocol_id": "http",
                        "proof_label": "Demo HTTP",
                        "upstream_repo": "https://github.com/example/demo.git",
                        "current_report_path": "reports/demo",
                        "archive_path": "archive/demo",
                        "latest_path": latest,
                        "lab_dir": "labs/demo",
                        "inventory_path": "labs/demo/inventory.yaml",
                        "quick_tps_path": "labs/demo/q.yaml",
                        "full_tps_path": "labs/demo/f.yaml",
                        "fixture_path": fixture,
                        "class_name": "Web-API",
                        "refreshability_status": "refreshable",
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def write_artifact_dir(directory: Path, *, cast: bool) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "static").mkdir(exist_ok=True)
    bodies = {
        "README.md": "# demo\n",
        "SCORECARD.txt": "UHQS 1.0\n",
        "REPORT.txt": "report\n",
        "report.json": json.dumps(
            {
                "uhqs": {
                    "uhqs": 10.0,
                    "grade": "F",
                    "delta_c": 0.4,
                    "S_A": 10,
                    "S_B": 10,
                    "S_C": 10,
                    "C": 10,
                    "S_E": 10,
                    "S_F": 10,
                }
            }
        ),
        "run-meta.json": json.dumps({"uhbs_version": "5.0.0", "run_mode": directory.name}),
        "uhbs-run.log": "ok\n",
    }
    artifacts = []
    for name, body in bodies.items():
        (directory / name).write_text(body, encoding="utf-8")
        artifacts.append({"path": name, "sha256": sha256_text(body)})
    if cast:
        proof = directory / "proof"
        proof.mkdir(exist_ok=True)
        cast_body = '{"version": 2, "width": 80, "height": 24}\n'
        (proof / "full-run.cast").write_text(cast_body, encoding="utf-8")
        artifacts.append({"path": "proof/full-run.cast", "sha256": sha256_text(cast_body)})
    (directory / "MANIFEST.json").write_text(
        json.dumps({"uhbs_version": "5.0.0", "artifacts": artifacts}),
        encoding="utf-8",
    )


def seed_complete_unit(tmp_path: Path, *, include_cast: bool) -> tuple[Path, Path]:
    db = tmp_path / "t.sqlite3"
    latest = tmp_path / "latest" / "demo"
    fixture = tmp_path / "demo.scorecard.json"
    fixture.write_text("{}", encoding="utf-8")
    manifest = tmp_path / "manifest.yaml"
    write_manifest(manifest, str(latest), str(fixture))
    run_py(TRACKER, "--db", str(db), "init-db")
    run_py(TRACKER, "--db", str(db), "import-manifest", "--manifest", str(manifest))
    run_py(
        TRACKER,
        "--db",
        str(db),
        "set-unit-meta",
        "--unit-id",
        "demo-http",
        "--upstream-commit",
        "abc123def456",
        "--upstream-branch",
        "main",
    )
    latest.mkdir(parents=True, exist_ok=True)
    (latest / "EXECUTION-STEPS.md").write_text("# steps\n1. clone\n", encoding="utf-8")
    (latest / "index.md").write_text("# demo\n", encoding="utf-8")
    write_artifact_dir(latest / "quick", cast=False)
    write_artifact_dir(latest / "full", cast=include_cast)

    for mode, out in (("quick", latest / "quick"), ("full", latest / "full")):
        extra = [
            "--base-image",
            "ubuntu:latest",
            "--base-image-reason",
            "SOP default",
            "--strategy",
            "ubuntu-wrapper",
            "--airgap-attested",
        ]
        run_py(
            TRACKER,
            "--db",
            str(db),
            "log-run-start",
            "--unit-id",
            "demo-http",
            "--mode",
            mode,
            *extra,
        )
        finish = [
            TRACKER,
            "--db",
            str(db),
            "log-run-finish",
            "--unit-id",
            "demo-http",
            "--mode",
            mode,
            "--out-dir",
            str(out),
        ]
        if mode == "full" and include_cast:
            finish.extend(["--cast-path", str(out / "proof" / "full-run.cast")])
        run_py(*finish)
    return db, latest


def test_complete_fake_tree_passes(tmp_path: Path) -> None:
    db, _latest = seed_complete_unit(tmp_path, include_cast=True)
    result = run_py(
        VALIDATE,
        "--unit-id",
        "demo-http",
        "--db",
        str(db),
        "--root",
        str(tmp_path),
    )
    assert result.returncode == 0
    assert "OK demo-http" in result.stdout


def test_missing_cast_fails(tmp_path: Path) -> None:
    db, latest = seed_complete_unit(tmp_path, include_cast=False)
    result = run_py(
        VALIDATE,
        "--unit-id",
        "demo-http",
        "--db",
        str(db),
        "--root",
        str(tmp_path),
        check=False,
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "cast" in combined.lower()
    assert not (latest / "full" / "proof" / "full-run.cast").exists()
