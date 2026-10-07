#!/usr/bin/env python3
"""Sync golden scorecard fixtures from results-5.0.1 full-run artifacts.

Reconciliation for the 5.0.1 coverage wave: every refreshable unit with a
completed local-Docker full run (report.json + SCORECARD.txt + run-meta.json)
should have a golden fixture that agrees with its published artifacts and the
normative scoring math. Driven by benchmark-manifest.yaml (the tracker control
plane), never by directory-name guessing.

Rules (mirroring scripts/rescore_renorm.py and assert_scorecard_integrity):

* composite/δ_C/grade are recomputed through ``uhbs_core.uhqs_math.compute_uhqs``
  (single source of truth — never a second math copy) and cross-checked against
  the artifact's stored values (0.05 composite tolerance, 1e-6 δ_C tolerance);
  mismatches are reported and the unit is skipped, not silently overridden
* assessment_status / verdict / safety_gate.passed are derived with the same
  fail-closed rules the integrity check enforces (any unmeasured module →
  INCOMPLETE; passed = GATE_PASSED verdict AND COMPLETE assessment)
* per-module scores/statuses/notes are artifact evidence, copied verbatim
  (``GATE FAILED`` is normalized to ``GATE_FAILED`` to match fixture convention)
* when the artifact's own assessment label disagrees with the derived one
  (the harness used a looser ≥4-measured rule), the label is patched in
  report.json / SCORECARD.txt and the MANIFEST.json sha256 refreshed so all
  published layers stay coherent
* every written fixture is schema-validated and must pass
  ``assert_scorecard_integrity`` before it touches the repository

Usage:
    python scripts/sync_wave_fixtures.py [--write]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uhbs_cli.scoring import assert_scorecard_integrity  # noqa: E402
from uhbs_core.uhqs_math import (  # noqa: E402
    SCORING_MODEL_ID,
    assessment_from_module_results,
    compute_uhqs,
    letter_grade,
    measured_modules_from_results,
)

MANIFEST = ROOT / "docs/conformance/latest/results-5.0.1/benchmark-manifest.yaml"
SCHEMA = ROOT / "schemas/scorecard.schema.json"

# (benchmark_id, protocol_id) → fixture, mirroring scripts/tracker.py overrides.
# Keeps units whose fixture name is not derivable from benchmark/protocol.
EXTRA_FIXTURE_OVERRIDES: dict[tuple[str, str], str] = {
    ("mockssh", "ssh"): "docs/conformance/fixtures/mockssh-low-interaction.scorecard.json",
}

MOD_ROW = re.compile(
    r"^Module ([A-F]): (.+?)\s*:\s*([\d.]+)/100\s+(\S+)\s+([A-Z_ ]+?)(?:\s\((.*)\))?$"
)
DATE_RE = re.compile(r"^Evaluation Date\s*: (\d{4}-\d{2}-\d{2})$", re.M)
STATUS_LINE = re.compile(r"^(Assessment Status\s*:\s*)(\S+)$", re.M)

_INCOMPLETE_D_STATUSES = {
    "SKIPPED",
    "N/A",
    "NOT_RUN",
    "INCOMPLETE",
    "NOT_TESTED",
    "NOT_MEASURED",
}


def measured_flags(report: dict) -> dict[str, bool]:
    payload = {
        m.get("module"): {"status": m.get("status"), "complete": m.get("complete")}
        for m in report.get("modules", [])
        if m.get("module") in {"A", "B", "C", "E", "F"}
    }
    return measured_modules_from_results(payload)


def containment_measured(report: dict) -> bool:
    if report.get("uhqs", {}).get("containment_measured") is False:
        return False
    d_mod = next((m for m in report.get("modules", []) if m.get("module") == "D"), {})
    status = str(d_mod.get("status", "")).upper().replace(" ", "_")
    return status not in _INCOMPLETE_D_STATUSES


def parse_scorecard_txt(text: str) -> tuple[str | None, dict[str, str]]:
    """Return (evaluation_date, {module_letter: note})."""
    date = DATE_RE.search(text)
    notes: dict[str, str] = {}
    for line in text.splitlines():
        m = MOD_ROW.match(line)
        if m:
            letter, _name, _score, _weight, _status, note = m.groups()
            notes[letter] = (note or "").strip()
    return (date.group(1) if date else None), notes


def build_fixture(unit: dict, report: dict, sc_txt: str, run_meta: dict) -> tuple[dict, dict]:
    """Return (fixture_dict, summary). Raises ValueError on artifact mismatch."""
    u = report["uhqs"]
    weights = {
        "w_A": u["weights"]["protocol"],
        "w_B": u["weights"]["behavior"],
        "w_C": u["weights"]["telemetry"],
        "w_E": u["weights"]["scale"],
        "w_F": u["weights"]["static"],
    }
    scores = {k: float(u[f"S_{k}"]) for k in "ABCEF"}
    scores["D"] = float(u.get("C", 0.0))

    rows = {m.get("module"): m for m in report.get("modules", [])}
    fixture_rows: dict[str, dict] = {}
    for letter in "ABCDEF":
        row = rows.get(letter)
        if row is None:
            raise ValueError(f"report.json has no module {letter}")
        entry: dict = {
            "score": float(row["score"]),
            "status": str(row["status"]).replace(" ", "_"),
            "notes": "",
            "complete": bool(row.get("complete")),
        }
        if letter == "D":
            entry["critical_control_verdict"] = str(
                row.get("critical_control_verdict") or "INCOMPLETE"
            )
        else:
            entry["weight"] = float(weights[f"w_{letter}"])
        fixture_rows[letter] = entry

    # Derive status/verdict exactly the way assert_scorecard_integrity does.
    derived_status, verdict0 = assessment_from_module_results(
        fixture_rows, critical_control_verdict=None
    )
    cm = containment_measured(report)
    result = compute_uhqs(
        scores,
        weights,
        profile_class=u.get("profile_class") or "POSIX-Shell",
        containment_measured=cm,
        assessment_status=derived_status,
        critical_control_verdict=verdict0,
        measured_modules=measured_flags(report),
    )

    stored_uhqs = float(u["uhqs"])
    if abs(result.uhqs - stored_uhqs) > 0.05:
        raise ValueError(
            f"composite mismatch: recomputed {result.uhqs:.4f} vs stored {stored_uhqs}"
        )
    if abs((result.delta_c or 0.0) - float(u.get("delta_c") or 0.0)) > 1e-6:
        raise ValueError(
            f"delta_c mismatch: recomputed {result.delta_c} vs stored {u.get('delta_c')}"
        )

    eval_date, mod_notes = parse_scorecard_txt(sc_txt)
    if not eval_date:
        raise ValueError("SCORECARD.txt has no Evaluation Date")
    for letter, entry in fixture_rows.items():
        entry["notes"] = mod_notes.get(letter, "")

    uhqs_value = result.uhqs
    grade = letter_grade(uhqs_value)
    commit = str(run_meta.get("upstream_commit") or "")
    repo = str(run_meta.get("upstream_repo") or "")
    latest = unit["latest_path"]
    notes = (
        f"Evaluation proof only. results-5.0.1 local-Docker refresh of {unit['unit_id']}"
        + (f" at {commit[:12]}" if commit else "")
        + (f" (upstream {repo})" if repo else "")
        + f". Regraded under {SCORING_MODEL_ID} (always-grade; measured modules "
        "renormalized; Safety Gate is a δ_C factor). "
        f"Artifacts: {latest}/full."
    )
    fixture = {
        "uhbs_version": str(run_meta.get("uhbs_version") or "5.0.1"),
        "target": {
            "name": unit.get("proof_label") or unit["unit_id"],
            "class": u.get("profile_class") or unit.get("class_name"),
            "profile_ref": run_meta.get("tps_path") or unit.get("full_tps_path"),
        },
        "evaluated_at": eval_date,
        "auditor": f"UHBS-Lab results-5.0.1 refresh ({unit['unit_id']})",
        "modules": fixture_rows,
        "weights": weights,
        "safety_gate": {
            "containment_score": float(rows["D"]["score"]),
            "delta_c": result.delta_c,
            "passed": result.safety_gate_passed,
            "critical_control_verdict": result.critical_control_verdict.value,
            "unauthorized_egress_leaks": 0,
        },
        "uhqs": uhqs_value,
        "grade": grade,
        "notes": notes,
        "scoring_model_id": SCORING_MODEL_ID,
        "assessment_status": derived_status.value,
        "critical_control_verdict": verdict0.value,
        "containment_measured": cm,
    }
    summary = {
        "uhqs": uhqs_value,
        "grade": grade,
        "verdict": verdict0.value,
        "gate_ccv": result.critical_control_verdict.value,
        "status": derived_status.value,
        "artifact_status": str(u.get("assessment_status")),
        "stored_uhqs": stored_uhqs,
    }
    return fixture, summary


def patch_artifact_label(full_dir: Path, derived_status: str) -> bool:
    """Align the artifact's assessment label with the fail-closed derivation."""
    rj = full_dir / "report.json"
    report = json.loads(rj.read_text())
    changed = False
    if report.get("uhqs", {}).get("assessment_status") != derived_status:
        report["uhqs"]["assessment_status"] = derived_status
        rj.write_text(json.dumps(report, indent=2) + "\n")
        changed = True
    for name in ("SCORECARD.txt", "REPORT.txt"):
        tp = full_dir / name
        if not tp.is_file():
            continue
        text = tp.read_text()
        new = STATUS_LINE.sub(lambda m: m.group(1) + derived_status, text, count=1)
        if new != text:
            tp.write_text(new)
            changed = True
    return changed


def refresh_manifest(full_dir: Path) -> None:
    mf = full_dir / "MANIFEST.json"
    if not mf.is_file():
        return
    import hashlib

    man = json.loads(mf.read_text())
    for art in man.get("artifacts", []):
        p = full_dir / str(art.get("path", ""))
        if p.is_file():
            art["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    mf.write_text(json.dumps(man, indent=2) + "\n")


def validate_fixture(fixture: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(fixture, schema)
    errors = assert_scorecard_integrity(fixture)
    if errors:
        raise ValueError(f"integrity: {errors}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--write", action="store_true", help="apply changes (default: dry-run)")
    args = p.parse_args(argv)

    manifest = yaml.safe_load(MANIFEST.read_text())
    plan, skipped, collisions = [], [], {}
    fixture_units: dict[str, list[str]] = {}
    for unit in manifest["units"]:
        if unit["refreshability_status"] != "refreshable":
            continue
        full_dir = ROOT / unit["latest_path"] / "full"
        if not ((full_dir / "report.json").is_file() and (full_dir / "SCORECARD.txt").is_file()):
            continue
        report = json.loads((full_dir / "report.json").read_text())
        if report.get("scoring_model_id") != SCORING_MODEL_ID:
            skipped.append((unit["unit_id"], "artifact model != normative"))
            continue
        fixture_path = unit.get("fixture_path") or EXTRA_FIXTURE_OVERRIDES.get(
            (unit["benchmark_id"], unit["protocol_id"])
        )
        if not fixture_path:
            skipped.append((unit["unit_id"], "no fixture mapping"))
            continue
        fixture_units.setdefault(fixture_path, []).append(unit)

    for fixture_path, units in sorted(fixture_units.items()):
        if len(units) > 1:
            collisions[fixture_path] = [u["unit_id"] for u in units]
            continue
        unit = units[0]
        full_dir = ROOT / unit["latest_path"] / "full"
        try:
            report = json.loads((full_dir / "report.json").read_text())
            sc_txt = (full_dir / "SCORECARD.txt").read_text()
            run_meta = json.loads((full_dir / "run-meta.json").read_text())
            fixture, summary = build_fixture(unit, report, sc_txt, run_meta)
            validate_fixture(fixture)
        except (ValueError, KeyError) as exc:
            skipped.append((unit["unit_id"], str(exc)))
            continue
        fpath = ROOT / fixture_path
        old = json.loads(fpath.read_text()) if fpath.is_file() else None
        changed = not old or json.dumps(old, sort_keys=True) != json.dumps(
            fixture, sort_keys=True
        )
        action = "create" if not old else ("update" if changed else "same")
        plan.append((action, fixture_path, unit, fixture, summary))

    print(f"units planned: {len(plan)} | skipped: {len(skipped)} | collisions: {len(collisions)}")
    for fp, ids in collisions.items():
        print(f"  COLLISION {fp}: {ids}")
    for uid, why in skipped:
        print(f"  SKIP {uid}: {why[:110]}")
    label_fixes = 0
    for action, fp, _unit, _fixture, summary in plan:
        if action == "same":
            continue
        if summary["artifact_status"] != summary["status"]:
            label_fixes += 1
        old = json.loads((ROOT / fp).read_text()) if (ROOT / fp).is_file() else {}
        old_s = f"{old.get('uhqs')}/{old.get('grade')}/{old.get('critical_control_verdict')}" if old else "-"
        print(
            f"  {action.upper():6} {Path(fp).name:44} {old_s:30} -> "
            f"{summary['uhqs']}/{summary['grade']}/{summary['verdict']}"
            + (
                f"  [label {summary['artifact_status']}→{summary['status']}]"
                if summary["artifact_status"] != summary["status"]
                else ""
            )
        )

    if args.write:
        for action, fp, unit, fixture, summary in plan:
            if action == "same":
                continue
            path = ROOT / fp
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(fixture, indent=2) + "\n")
            if summary["artifact_status"] != summary["status"]:
                full_dir = ROOT / unit["latest_path"] / "full"
                if patch_artifact_label(full_dir, summary["status"]):
                    refresh_manifest(full_dir)
        print(
            f"wrote {sum(1 for a, *_ in plan if a != 'same')} fixtures, "
            f"{label_fixes} artifact label patches"
        )
    else:
        print("dry-run only — pass --write to apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
