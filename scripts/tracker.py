#!/usr/bin/env python3
"""Benchmark-refresh control plane (SQLite + manifest + RUN-LEDGER).

Workers must use this CLI instead of raw SQL. Schema matches the SOP in
`.trae/documents/benchmark_refresh_results_v1_plan.md`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / ".local" / "benchmark-refresh" / "results-5.0.1.sqlite3"
DEFAULT_MANIFEST = ROOT / "docs" / "conformance" / "latest" / "results-5.0.1" / "benchmark-manifest.yaml"
DEFAULT_LEDGER = ROOT / "docs" / "conformance" / "latest" / "results-5.0.1" / "RUN-LEDGER.md"
REPORTS = ROOT / "docs" / "conformance" / "reports"
LABS = ROOT / "docs" / "conformance" / "labs"
FIXTURES = ROOT / "docs" / "conformance" / "fixtures"
ARCHIVE_ROOT = ROOT / "docs" / "conformance" / "archive" / "v5.0.0"
LATEST_ROOT = ROOT / "docs" / "conformance" / "latest" / "results-5.0.1"

SKIP_UPSTREAM_REPOS = frozenset({"uhbs/uhbs-standard", "mziqudhd92/uhbs-standard"})

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS benchmark_units (
  unit_id TEXT PRIMARY KEY,
  benchmark_id TEXT NOT NULL,
  protocol_id TEXT NOT NULL,
  proof_label TEXT NOT NULL,
  upstream_repo TEXT NOT NULL,
  upstream_default_branch TEXT,
  upstream_commit TEXT,
  current_report_path TEXT NOT NULL,
  archive_path TEXT NOT NULL,
  latest_path TEXT NOT NULL,
  lab_dir TEXT NOT NULL,
  inventory_path TEXT NOT NULL,
  quick_tps_path TEXT,
  full_tps_path TEXT,
  fixture_path TEXT,
  class_name TEXT,
  target_host TEXT,
  target_port INTEGER,
  refreshability_status TEXT NOT NULL,
  assigned_agent TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  telemetry_required INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS run_executions (
  run_id TEXT PRIMARY KEY,
  unit_id TEXT NOT NULL,
  run_mode TEXT NOT NULL CHECK (run_mode IN ('quick','full')),
  run_status TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  uhbs_version TEXT,
  grader_image TEXT,
  grader_image_digest TEXT,
  target_image TEXT,
  target_image_digest TEXT,
  base_image TEXT,
  base_image_reason TEXT,
  container_runtime_strategy TEXT,
  telemetry_mode TEXT,
  airgap_attested INTEGER NOT NULL DEFAULT 0,
  egress_log_path TEXT,
  scorecard_path TEXT,
  report_txt_path TEXT,
  report_json_path TEXT,
  manifest_path TEXT,
  run_meta_path TEXT,
  run_log_path TEXT,
  cast_path TEXT,
  uhqs REAL,
  grade TEXT,
  delta_c REAL,
  module_a REAL,
  module_b REAL,
  module_c REAL,
  module_d REAL,
  module_e REAL,
  module_f REAL,
  validation_status TEXT,
  notes TEXT,
  raw_s3_uri TEXT,
  FOREIGN KEY (unit_id) REFERENCES benchmark_units(unit_id)
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  rel_path TEXT NOT NULL,
  sha256 TEXT,
  file_size_bytes INTEGER,
  exists_on_disk INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES run_executions(run_id)
);

CREATE TABLE IF NOT EXISTS blockers (
  blocker_id TEXT PRIMARY KEY,
  unit_id TEXT NOT NULL,
  blocker_type TEXT NOT NULL,
  blocker_stage TEXT NOT NULL,
  summary TEXT NOT NULL,
  details TEXT,
  log_path TEXT,
  is_resolved INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES benchmark_units(unit_id)
);

CREATE INDEX IF NOT EXISTS idx_benchmark_units_status
  ON benchmark_units(refreshability_status);

CREATE INDEX IF NOT EXISTS idx_run_executions_unit_mode
  ON run_executions(unit_id, run_mode);

CREATE INDEX IF NOT EXISTS idx_run_executions_status
  ON run_executions(run_status);

CREATE INDEX IF NOT EXISTS idx_artifacts_run
  ON artifacts(run_id);

CREATE INDEX IF NOT EXISTS idx_blockers_unit
  ON blockers(unit_id);
"""

FIXTURE_OVERRIDES: dict[tuple[str, str], str] = {
    ("espot", "http"): "docs/conformance/fixtures/espot-web-api.scorecard.json",
    ("miniprint", "pjl"): "docs/conformance/fixtures/miniprint-low-interaction.scorecard.json",
    ("endlessh", "ssh_tarpit"): "docs/conformance/fixtures/endlessh-low-interaction.scorecard.json",
    ("endlessh", "interaction"): "docs/conformance/fixtures/endlessh-low-interaction.scorecard.json",
    ("conpot", "modbus"): "docs/conformance/fixtures/conpot-ics-scada.scorecard.json",
    ("echidra", "ssh"): "docs/conformance/fixtures/echidra-low-interaction.scorecard.json",
    ("HellPot", "http"): "docs/conformance/fixtures/hellpot-web-api.scorecard.json",
    ("HoneyWire", "http"): "docs/conformance/fixtures/honeywire-web-api.scorecard.json",
    ("opencanary", "http"): "docs/conformance/fixtures/opencanary-web-api.scorecard.json",
    ("cowrie", "ssh"): "docs/conformance/fixtures/cowrie-ssh.scorecard.json",
    ("cowrie", "telnet"): "docs/conformance/fixtures/cowrie-telnet.scorecard.json",
    ("mqtt-decoy-a", "mqtt"): "docs/conformance/fixtures/mqtt-decoy-a.scorecard.json",
    ("mqtt-decoy-b", "mqtt"): "docs/conformance/fixtures/mqtt-decoy-b.scorecard.json",
}

UNIT_COLUMNS = [
    "unit_id",
    "benchmark_id",
    "protocol_id",
    "proof_label",
    "upstream_repo",
    "upstream_default_branch",
    "upstream_commit",
    "current_report_path",
    "archive_path",
    "latest_path",
    "lab_dir",
    "inventory_path",
    "quick_tps_path",
    "full_tps_path",
    "fixture_path",
    "class_name",
    "target_host",
    "target_port",
    "refreshability_status",
    "assigned_agent",
    "created_at",
    "updated_at",
    "telemetry_required",
]


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id() -> str:
    return uuid.uuid4().hex


def emit(payload: dict[str, Any], *, ok: bool = True) -> None:
    payload = {"ok": ok, **payload}
    print(json.dumps(payload, default=str))


def rel(path: Path | str | None) -> str:
    if path is None:
        return ""
    p = Path(path)
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = (), retries: int = 8) -> sqlite3.Cursor:
    delay = 0.05
    last: sqlite3.OperationalError | None = None
    for attempt in range(retries):
        try:
            return conn.execute(sql, params)
        except sqlite3.OperationalError as exc:
            last = exc
            if "locked" not in str(exc).lower() or attempt == retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 1.0)
    assert last is not None
    raise last


def init_db(db_path: Path) -> None:
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        migrate_schema(conn)
        journal = execute(conn, "PRAGMA journal_mode").fetchone()[0]
        emit({"db": str(db_path), "journal_mode": journal, "busy_timeout_ms": 10000})
    finally:
        conn.close()


def migrate_schema(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the initial schema (idempotent)."""
    unit_cols = {
        row[1]
        for row in execute(conn, "PRAGMA table_info(benchmark_units)").fetchall()
    }
    if "telemetry_required" not in unit_cols:
        execute(
            conn,
            "ALTER TABLE benchmark_units ADD COLUMN telemetry_required "
            "INTEGER NOT NULL DEFAULT 0",
        )
    run_cols = {
        row[1]
        for row in execute(conn, "PRAGMA table_info(run_executions)").fetchall()
    }
    if run_cols and "raw_s3_uri" not in run_cols:
        execute(conn, "ALTER TABLE run_executions ADD COLUMN raw_s3_uri TEXT")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def tps_protocol(path: Path) -> str | None:
    data = load_yaml(path)
    meta = data.get("target_metadata") or {}
    proto = meta.get("protocol")
    if proto:
        return str(proto)
    protocols = meta.get("protocols") or []
    if protocols:
        return str(protocols[0])
    return None


def extract_upstream(hub: Path) -> str:
    texts: list[str] = []
    for name in ("TUTORIAL.md", "index.md", "METHODOLOGY.md"):
        p = hub / name
        if p.is_file():
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    blob = "\n".join(texts)
    clone = re.findall(
        r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:[\s)'\"#]|$)",
        blob,
    )
    for owner, repo in clone:
        slug = f"{owner}/{repo}"
        if slug in SKIP_UPSTREAM_REPOS:
            continue
        return f"https://github.com/{slug}.git"
    md = re.findall(r"https://github.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", blob)
    for owner, repo in md:
        slug = f"{owner}/{repo}"
        if slug in SKIP_UPSTREAM_REPOS:
            continue
        return f"https://github.com/{slug}.git"
    return ""


def heading(hub: Path) -> str:
    index = hub / "index.md"
    if index.is_file():
        for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return hub.name


def report_is_single_layout(hub: Path) -> bool:
    if not hub.is_dir():
        return True
    names = {p.name for p in hub.iterdir() if p.is_dir()}
    if not names:
        return True
    return names <= {"quick", "full", "static", "proof"}


def match_fixture(benchmark_id: str, protocol_id: str) -> str | None:
    override = FIXTURE_OVERRIDES.get((benchmark_id, protocol_id))
    if override and (ROOT / override).is_file():
        return override
    candidates = [
        FIXTURES / f"{benchmark_id}-{protocol_id}.scorecard.json",
        FIXTURES / f"{benchmark_id.lower()}-{protocol_id}.scorecard.json",
        FIXTURES / f"{benchmark_id.lower()}-{protocol_id.lower()}.scorecard.json",
    ]
    if protocol_id == "http":
        candidates.extend(
            [
                FIXTURES / f"{benchmark_id.lower()}-web-api.scorecard.json",
                FIXTURES / f"{benchmark_id}-web-api.scorecard.json",
            ]
        )
    for path in candidates:
        if path.is_file():
            return rel(path)
    return None


def pair_tps(lab_dir: Path, protocol_id: str, site: dict[str, Any]) -> tuple[str | None, str | None]:
    declared = site.get("tps")
    full_path: Path | None = None
    if declared:
        raw = str(declared)
        if raw.startswith("/work/"):
            raw = raw[len("/work/") :]
        candidate = ROOT / raw if not Path(raw).is_absolute() else Path(raw)
        if candidate.is_file():
            full_path = candidate
    if full_path is None:
        for path in sorted(lab_dir.glob("*_full.yaml")):
            if protocol_id in path.name or tps_protocol(path) == protocol_id:
                full_path = path
                break
    if full_path is None:
        fulls = sorted(lab_dir.glob("*_full.yaml"))
        if len(fulls) == 1:
            full_path = fulls[0]
    quick_path: Path | None = None
    if full_path is not None:
        guessed = Path(str(full_path).replace("_full.yaml", "_quick.yaml"))
        if guessed.is_file():
            quick_path = guessed
    if quick_path is None:
        for path in sorted(lab_dir.glob("*_quick.yaml")):
            if protocol_id in path.name or tps_protocol(path) == protocol_id:
                quick_path = path
                break
    if quick_path is None:
        quicks = sorted(lab_dir.glob("*_quick.yaml"))
        if len(quicks) == 1:
            quick_path = quicks[0]
    return (rel(quick_path) if quick_path else None, rel(full_path) if full_path else None)


def discover_units() -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    hubs = sorted([p for p in REPORTS.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
    created = now_iso()
    for hub in hubs:
        benchmark_id = hub.name
        lab_dir = LABS / benchmark_id
        inventory_path = lab_dir / "inventory.yaml"
        upstream = extract_upstream(hub)
        label = heading(hub)
        single = report_is_single_layout(hub)
        if not inventory_path.is_file():
            protocol_dirs = [
                p for p in hub.iterdir() if p.is_dir() and p.name not in {"quick", "full", "static", "proof"}
            ]
            protocol_id = protocol_dirs[0].name if len(protocol_dirs) == 1 else "legacy"
            report_rel = rel(hub if single or protocol_id == "legacy" else protocol_dirs[0])
            unit_id = f"{benchmark_id}-{protocol_id}"
            latest = (
                LATEST_ROOT / benchmark_id
                if protocol_id == "legacy" or single
                else LATEST_ROOT / benchmark_id / protocol_id
            )
            archive = ARCHIVE_ROOT / benchmark_id if protocol_id == "legacy" or single else ARCHIVE_ROOT / benchmark_id / protocol_id
            units.append(
                {
                    "unit_id": unit_id,
                    "benchmark_id": benchmark_id,
                    "protocol_id": protocol_id,
                    "proof_label": label,
                    "upstream_repo": upstream,
                    "upstream_default_branch": None,
                    "upstream_commit": None,
                    "current_report_path": report_rel,
                    "archive_path": rel(archive),
                    "latest_path": rel(latest),
                    "lab_dir": rel(lab_dir) if lab_dir.is_dir() else "",
                    "inventory_path": "",
                    "quick_tps_path": None,
                    "full_tps_path": None,
                    "fixture_path": match_fixture(benchmark_id, protocol_id),
                    "class_name": None,
                    "target_host": None,
                    "target_port": None,
                    "refreshability_status": "legacy-not-refreshed",
                    "assigned_agent": None,
                    "created_at": created,
                    "updated_at": created,
                    "upstream_ref_policy": "default-branch-head",
                    "telemetry_required": False,
                    "expected_runtime_strategy": "none",
                    "layout": "single" if single or protocol_id == "legacy" else "multi",
                }
            )
            continue

        inventory = load_yaml(inventory_path)
        sites = inventory.get("sites") or {}
        multi = (not single) or len(sites) > 1
        for site_id, site in sites.items():
            declared = site.get("tps")
            if declared:
                raw = str(declared)
                if raw.startswith("/work/"):
                    raw = raw[len("/work/") :]
                tps_file = ROOT / raw if not Path(raw).is_absolute() else Path(raw)
                try:
                    tps_file.resolve().relative_to(lab_dir.resolve())
                except ValueError:
                    # Stray site copied from another lab inventory — skip.
                    continue
            protocol_id = str(site.get("protocol") or site_id.split("-")[-1])
            quick_tps, full_tps = pair_tps(lab_dir, protocol_id, site)
            if quick_tps and full_tps:
                status = "refreshable"
            elif full_tps or quick_tps:
                status = "blocked-pre-run"
            else:
                status = "blocked-pre-run"
            if multi:
                report_path = hub / protocol_id if (hub / protocol_id).is_dir() else hub
                latest = LATEST_ROOT / benchmark_id / protocol_id
                archive = ARCHIVE_ROOT / benchmark_id / protocol_id
            else:
                report_path = hub
                latest = LATEST_ROOT / benchmark_id
                archive = ARCHIVE_ROOT / benchmark_id
            unit_id = f"{benchmark_id}-{protocol_id}"
            proof = f"{label} ({protocol_id})" if multi else label
            units.append(
                {
                    "unit_id": unit_id,
                    "benchmark_id": benchmark_id,
                    "protocol_id": protocol_id,
                    "proof_label": proof,
                    "upstream_repo": upstream,
                    "upstream_default_branch": None,
                    "upstream_commit": None,
                    "current_report_path": rel(report_path),
                    "archive_path": rel(archive),
                    "latest_path": rel(latest),
                    "lab_dir": rel(lab_dir),
                    "inventory_path": rel(inventory_path),
                    "quick_tps_path": quick_tps,
                    "full_tps_path": full_tps,
                    "fixture_path": match_fixture(benchmark_id, protocol_id),
                    "class_name": site.get("class"),
                    "target_host": site.get("host"),
                    "target_port": site.get("port"),
                    "refreshability_status": status,
                    "assigned_agent": None,
                    "created_at": created,
                    "updated_at": created,
                    "upstream_ref_policy": "default-branch-head",
                    "telemetry_required": bool(site.get("telemetry_dir")),
                    "expected_runtime_strategy": "upstream-image-or-wrapper",
                    "layout": "multi" if multi else "single",
                    "inventory_site_id": site_id,
                    "container_image": site.get("container_image"),
                }
            )
    return units


def write_manifest(units: list[dict[str, Any]], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    refreshable = sum(1 for u in units if u["refreshability_status"] == "refreshable")
    legacy = sum(1 for u in units if u["refreshability_status"] == "legacy-not-refreshed")
    blocked = sum(1 for u in units if str(u["refreshability_status"]).startswith("blocked"))
    hubs = sorted({u["benchmark_id"] for u in units})
    payload = {
        "version": "results-5.0.1",
        "uhbs_version": "5.0.1",
        "generated_at": now_iso(),
        "counts": {
            "hubs": len(hubs),
            "units": len(units),
            "refreshable_units": refreshable,
            "legacy_units": legacy,
            "blocked_units": blocked,
        },
        "units": units,
    }
    dest.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def fetch_units(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(execute(conn, "SELECT * FROM benchmark_units ORDER BY benchmark_id, protocol_id").fetchall())


def render_ledger(
    conn: sqlite3.Connection,
    dest: Path,
    *,
    gate_d_open: bool | None = None,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows = fetch_units(conn)
    refreshable = [r for r in rows if r["refreshability_status"] == "refreshable"]
    assigned = [r for r in rows if r["assigned_agent"]]
    legacy = [r for r in rows if r["refreshability_status"] == "legacy-not-refreshed"]
    blocked = [r for r in rows if str(r["refreshability_status"]).startswith("blocked")]
    hubs = {r["benchmark_id"] for r in rows}
    if gate_d_open is None:
        existing = dest.read_text(encoding="utf-8") if dest.is_file() else ""
        gate_d_open = "Gate D:** OPEN" in existing or "Gate D: OPEN" in existing
    gate_line = (
        "**Gate D:** OPEN — workers may claim refreshable units with "
        "`python scripts/tracker.py claim-next --agent <id>`."
        if gate_d_open
        else "**Gate D:** CLOSED — coordinator bootstrap is still in progress. Do not claim units."
    )
    lines = [
        "# RUN-LEDGER — `docs/conformance/latest/results-5.0.1`",
        "",
        f"Updated: {now_iso()}",
        "",
        gate_line,
        "",
        "## Counts",
        "",
        f"- Hubs: **{len(hubs)}**",
        f"- Units: **{len(rows)}**",
        f"- Refreshable: **{len(refreshable)}**",
        f"- Legacy / not refreshed: **{len(legacy)}**",
        f"- Blocked: **{len(blocked)}**",
        f"- Assigned: **{len(assigned)}**",
        "",
        "SQLite: `.local/benchmark-refresh/results-5.0.1.sqlite3`",
        "Manifest: `docs/conformance/latest/results-5.0.1/benchmark-manifest.yaml`",
        "",
        "## Units",
        "",
        "| unit_id | benchmark | protocol | status | agent | latest | archive |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        agent = row["assigned_agent"] or ""
        lines.append(
            f"| `{row['unit_id']}` | `{row['benchmark_id']}` | `{row['protocol_id']}` | "
            f"`{row['refreshability_status']}` | {agent} | `{row['latest_path']}` | `{row['archive_path']}` |"
        )
    blockers = execute(
        conn,
        "SELECT * FROM blockers WHERE is_resolved = 0 ORDER BY created_at",
    ).fetchall()
    classification = [b for b in blockers if b["blocker_type"] == "classification"]
    open_blockers = [b for b in blockers if b["blocker_type"] != "classification"]
    lines += ["", "## Open blockers", ""]
    if not open_blockers:
        lines.append("_None._")
    else:
        lines.append("| unit_id | stage | summary | log |")
        lines.append("| --- | --- | --- | --- |")
        for b in open_blockers:
            lines.append(
                f"| `{b['unit_id']}` | `{b['blocker_stage']}` | {b['summary']} | `{b['log_path'] or ''}` |"
            )
    lines += ["", "## Notes", ""]
    if classification or legacy:
        lines += [
            "Legacy hubs are explicitly closed as `legacy-not-refreshed` (no executable lab). "
            "No UHQS scores were invented. Historical proof remains under "
            "`docs/conformance/archive/v5.0.0/`.",
            "",
            "| unit_id | benchmark | note |",
            "| --- | --- | --- |",
        ]
        note_by_unit = {b["unit_id"]: b["summary"] for b in classification}
        for row in legacy:
            note = note_by_unit.get(
                row["unit_id"],
                "legacy-not-refreshed (no executable lab)",
            ).replace("|", "\\|")
            lines.append(
                f"| `{row['unit_id']}` | `{row['benchmark_id']}` | {note} |"
            )
    else:
        lines.append("_No legacy-closure notes._")
    lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")


def import_manifest(conn: sqlite3.Connection, manifest_path: Path) -> int:
    migrate_schema(conn)
    data = load_yaml(manifest_path)
    units = data.get("units") or []
    count = 0
    for unit in units:
        values = []
        for col in UNIT_COLUMNS:
            val = unit.get(col)
            if col in {"created_at", "updated_at"} and not val:
                val = now_iso()
            if col == "telemetry_required":
                val = 1 if val in (True, 1, "1", "true", "True") else 0
            values.append(val)
        placeholders = ",".join("?" for _ in UNIT_COLUMNS)
        cols = ",".join(UNIT_COLUMNS)
        execute(
            conn,
            f"INSERT OR REPLACE INTO benchmark_units ({cols}) VALUES ({placeholders})",
            tuple(values),
        )
        count += 1
    return count


def get_unit(conn: sqlite3.Connection, unit_id: str) -> sqlite3.Row | None:
    return execute(conn, "SELECT * FROM benchmark_units WHERE unit_id = ?", (unit_id,)).fetchone()


def claim_unit(
    conn: sqlite3.Connection, unit_id: str, agent: str, *, force: bool = False
) -> sqlite3.Row | None:
    ts = now_iso()
    execute(conn, "BEGIN IMMEDIATE")
    try:
        current = get_unit(conn, unit_id)
        if current is None:
            conn.execute("ROLLBACK")
            return None
        if current["assigned_agent"] == agent and not force:
            conn.execute("COMMIT")
            return current
        if force:
            cur = execute(
                conn,
                """
                UPDATE benchmark_units
                SET assigned_agent = ?,
                    refreshability_status = 'assigned',
                    updated_at = ?
                WHERE unit_id = ?
                """,
                (agent, ts, unit_id),
            )
        else:
            cur = execute(
                conn,
                """
                UPDATE benchmark_units
                SET assigned_agent = ?,
                    refreshability_status = 'assigned',
                    updated_at = ?
                WHERE unit_id = ?
                  AND assigned_agent IS NULL
                  AND refreshability_status IN ('refreshable', 'pending')
                """,
                (agent, ts, unit_id),
            )
        if cur.rowcount != 1:
            conn.execute("ROLLBACK")
            return None
        conn.execute("COMMIT")
        return get_unit(conn, unit_id)
    except Exception:
        conn.execute("ROLLBACK")
        raise


def claim_next(conn: sqlite3.Connection, agent: str) -> sqlite3.Row | None:
    execute(conn, "BEGIN IMMEDIATE")
    try:
        row = execute(
            conn,
            """
            SELECT unit_id FROM benchmark_units
            WHERE assigned_agent IS NULL
              AND refreshability_status IN ('refreshable', 'pending')
            ORDER BY unit_id
            LIMIT 1
            """,
        ).fetchone()
        if row is None:
            conn.execute("COMMIT")
            return None
        unit_id = row["unit_id"]
        ts = now_iso()
        cur = execute(
            conn,
            """
            UPDATE benchmark_units
            SET assigned_agent = ?,
                refreshability_status = 'assigned',
                updated_at = ?
            WHERE unit_id = ?
              AND assigned_agent IS NULL
              AND refreshability_status IN ('refreshable', 'pending')
            """,
            (agent, ts, unit_id),
        )
        if cur.rowcount != 1:
            conn.execute("ROLLBACK")
            return None
        conn.execute("COMMIT")
        return get_unit(conn, unit_id)
    except Exception:
        conn.execute("ROLLBACK")
        raise


def row_public(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    return dict(row)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_scores(report_json: Path) -> dict[str, Any]:
    if not report_json.is_file():
        return {}
    try:
        data = json.loads(report_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    uhqs = data.get("uhqs")
    out: dict[str, Any] = {}
    if isinstance(uhqs, dict):
        out["uhqs"] = uhqs.get("uhqs")
        grade = uhqs.get("grade")
        out["grade"] = grade
        out["delta_c"] = uhqs.get("delta_c")
        out["module_a"] = uhqs.get("S_A")
        out["module_b"] = uhqs.get("S_B")
        out["module_c"] = uhqs.get("S_C")
        out["module_d"] = uhqs.get("C")
        out["module_e"] = uhqs.get("S_E")
        out["module_f"] = uhqs.get("S_F")
    elif isinstance(uhqs, (int, float)):
        out["uhqs"] = uhqs
        out["grade"] = data.get("grade")
    results = data.get("results") or {}
    if "uhqs" in results and out.get("uhqs") is None:
        out["uhqs"] = results.get("uhqs")
        out["grade"] = results.get("grade")
        out["delta_c"] = results.get("delta_c")
        mods = results.get("module_scores") or {}
        out["module_a"] = mods.get("A")
        out["module_b"] = mods.get("B")
        out["module_c"] = mods.get("C")
        out["module_d"] = mods.get("D")
        out["module_e"] = mods.get("E")
        out["module_f"] = mods.get("F")
    return out


ARTIFACT_NAMES = {
    "README.md": "readme",
    "SCORECARD.txt": "scorecard",
    "REPORT.txt": "report_txt",
    "report.json": "report_json",
    "MANIFEST.json": "manifest",
    "run-meta.json": "run_meta",
    "uhbs-run.log": "run_log",
    "proof/full-run.cast": "cast",
}


def log_run_start(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    unit = get_unit(conn, args.unit_id)
    if unit is None:
        raise SystemExit(f"unknown unit_id: {args.unit_id}")
    run_id = new_id()
    ts = now_iso()
    execute(
        conn,
        """
        INSERT INTO run_executions (
          run_id, unit_id, run_mode, run_status, started_at, uhbs_version,
          grader_image, target_image, base_image, base_image_reason,
          container_runtime_strategy, telemetry_mode, airgap_attested, notes
        ) VALUES (?, ?, ?, 'running', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            args.unit_id,
            args.mode,
            ts,
            args.uhbs_version,
            args.grader_image,
            args.target_image,
            args.base_image,
            args.base_image_reason,
            args.strategy,
            args.telemetry_mode,
            1 if args.airgap_attested else 0,
            args.notes,
        ),
    )
    execute(
        conn,
        "UPDATE benchmark_units SET refreshability_status = 'running', updated_at = ? WHERE unit_id = ?",
        (ts, args.unit_id),
    )
    return {"run_id": run_id, "unit_id": args.unit_id, "run_mode": args.mode, "started_at": ts}


def latest_open_run(conn: sqlite3.Connection, unit_id: str, mode: str) -> sqlite3.Row | None:
    return execute(
        conn,
        """
        SELECT * FROM run_executions
        WHERE unit_id = ? AND run_mode = ? AND run_status = 'running'
        ORDER BY started_at DESC
        LIMIT 1
        """,
        (unit_id, mode),
    ).fetchone()


def log_run_finish(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    run = latest_open_run(conn, args.unit_id, args.mode)
    if run is None:
        run_id = new_id()
        execute(
            conn,
            """
            INSERT INTO run_executions (run_id, unit_id, run_mode, run_status, started_at)
            VALUES (?, ?, ?, 'running', ?)
            """,
            (run_id, args.unit_id, args.mode, now_iso()),
        )
        run = execute(conn, "SELECT * FROM run_executions WHERE run_id = ?", (run_id,)).fetchone()
    assert run is not None
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    cast_path = args.cast_path
    if args.mode == "full" and not cast_path:
        candidate = out_dir / "proof" / "full-run.cast"
        if candidate.exists():
            cast_path = str(candidate)
    scores = parse_scores(out_dir / "report.json")
    ts = now_iso()
    status = args.status
    execute(
        conn,
        """
        UPDATE run_executions SET
          run_status = ?, finished_at = ?,
          scorecard_path = ?, report_txt_path = ?, report_json_path = ?,
          manifest_path = ?, run_meta_path = ?, run_log_path = ?, cast_path = ?,
          uhqs = COALESCE(?, uhqs), grade = COALESCE(?, grade),
          delta_c = COALESCE(?, delta_c),
          module_a = COALESCE(?, module_a), module_b = COALESCE(?, module_b),
          module_c = COALESCE(?, module_c), module_d = COALESCE(?, module_d),
          module_e = COALESCE(?, module_e), module_f = COALESCE(?, module_f)
        WHERE run_id = ?
        """,
        (
            status,
            ts,
            rel(out_dir / "SCORECARD.txt") if (out_dir / "SCORECARD.txt").exists() else None,
            rel(out_dir / "REPORT.txt") if (out_dir / "REPORT.txt").exists() else None,
            rel(out_dir / "report.json") if (out_dir / "report.json").exists() else None,
            rel(out_dir / "MANIFEST.json") if (out_dir / "MANIFEST.json").exists() else None,
            rel(out_dir / "run-meta.json") if (out_dir / "run-meta.json").exists() else None,
            rel(out_dir / "uhbs-run.log") if (out_dir / "uhbs-run.log").exists() else None,
            rel(cast_path) if cast_path else None,
            scores.get("uhqs"),
            scores.get("grade"),
            scores.get("delta_c"),
            scores.get("module_a"),
            scores.get("module_b"),
            scores.get("module_c"),
            scores.get("module_d"),
            scores.get("module_e"),
            scores.get("module_f"),
            run["run_id"],
        ),
    )
    recorded = []
    for name, atype in ARTIFACT_NAMES.items():
        if args.mode != "full" and atype == "cast":
            continue
        path = out_dir / name
        exists = path.is_file()
        artifact_id = new_id()
        digest = sha256_file(path) if exists else None
        size = path.stat().st_size if exists else None
        execute(
            conn,
            """
            INSERT INTO artifacts (
              artifact_id, run_id, artifact_type, rel_path, sha256,
              file_size_bytes, exists_on_disk, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact_id,
                run["run_id"],
                atype,
                rel(path) if exists else name,
                digest,
                size,
                1 if exists else 0,
                ts,
            ),
        )
        recorded.append({"artifact_id": artifact_id, "type": atype, "exists": exists})
    unit_status = "ran" if status in {"succeeded", "success", "ok"} else "blocked"
    execute(
        conn,
        "UPDATE benchmark_units SET refreshability_status = ?, updated_at = ? WHERE unit_id = ?",
        (unit_status, ts, args.unit_id),
    )
    return {
        "run_id": run["run_id"],
        "unit_id": args.unit_id,
        "run_mode": args.mode,
        "run_status": status,
        "artifacts": recorded,
    }


def log_blocker(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    if get_unit(conn, args.unit_id) is None:
        raise SystemExit(f"unknown unit_id: {args.unit_id}")
    ts = now_iso()
    blocker_id = new_id()
    execute(
        conn,
        """
        INSERT INTO blockers (
          blocker_id, unit_id, blocker_type, blocker_stage, summary, details,
          log_path, is_resolved, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """,
        (
            blocker_id,
            args.unit_id,
            args.blocker_type,
            args.stage,
            args.summary,
            args.details,
            args.log_path,
            ts,
            ts,
        ),
    )
    status = args.status or f"blocked-{args.stage}"
    execute(
        conn,
        "UPDATE benchmark_units SET refreshability_status = ?, updated_at = ? WHERE unit_id = ?",
        (status, ts, args.unit_id),
    )
    return {"blocker_id": blocker_id, "unit_id": args.unit_id, "stage": args.stage}


def set_fixture(conn: sqlite3.Connection, unit_id: str, fixture_path: str) -> None:
    if get_unit(conn, unit_id) is None:
        raise SystemExit(f"unknown unit_id: {unit_id}")
    execute(
        conn,
        "UPDATE benchmark_units SET fixture_path = ?, updated_at = ? WHERE unit_id = ?",
        (rel(fixture_path), now_iso(), unit_id),
    )


def set_unit_meta(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    unit = get_unit(conn, args.unit_id)
    if unit is None:
        raise SystemExit(f"unknown unit_id: {args.unit_id}")
    fields = {
        "upstream_repo": args.upstream_repo,
        "upstream_default_branch": args.upstream_branch,
        "upstream_commit": args.upstream_commit,
    }
    assignments = []
    values: list[Any] = []
    for col, val in fields.items():
        if val is not None:
            assignments.append(f"{col} = ?")
            values.append(val)
    if assignments:
        assignments.append("updated_at = ?")
        values.append(now_iso())
        values.append(args.unit_id)
        execute(conn, f"UPDATE benchmark_units SET {', '.join(assignments)} WHERE unit_id = ?", tuple(values))
    if any([args.base_image, args.base_image_reason, args.strategy]):
        execute(
            conn,
            """
            UPDATE run_executions SET
              base_image = COALESCE(?, base_image),
              base_image_reason = COALESCE(?, base_image_reason),
              container_runtime_strategy = COALESCE(?, container_runtime_strategy)
            WHERE unit_id = ?
            """,
            (args.base_image, args.base_image_reason, args.strategy, args.unit_id),
        )
    return row_public(get_unit(conn, args.unit_id))


PLACEHOLDER_INDEX = """# {title}

**Status:** placeholder — awaiting refresh (`{status}`)

- Benchmark: `{benchmark_id}`
- Protocol: `{protocol_id}`
- Archive: [`{archive_path}`](../../../../{archive_path})
- Latest path: `{latest_path}`

Do not treat this page as a published UHQS grade. Workers replace these placeholders after a successful claim, clone, Ubuntu Docker run, and `python scripts/validate_unit.py --unit-id {unit_id}`.
"""

PLACEHOLDER_DOC = """# {title}

Placeholder generated during Gate D skeleton initialization.

Replace this document with the actual {kind} after the unit is executed. Do not copy archived 4.x letter grades.
"""

PLACEHOLDER_STEPS = """# Execution steps — `{unit_id}`

Status: **placeholder**. After claiming this unit, replace this file with the exact commands used, including:

1. `GIT_TERMINAL_PROMPT=0 git clone --depth 1 <upstream> .local/labs/<benchmark>`
2. `git rev-parse HEAD` and default branch name
3. Docker build/run on `uhbs-lab`
4. Quick grader command (`uhbs:5.0.1`)
5. Full grader + `asciinema rec` command (`uhbs:5.0.1-full`)
6. `python scripts/validate_unit.py --unit-id {unit_id}`

See `.trae/documents/benchmark_refresh_results_v1_plan.md`.
"""


def write_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def generate_skeleton(conn: sqlite3.Connection) -> dict[str, int]:
    created_dirs = 0
    created_docs = 0
    hubs_done: set[str] = set()
    for row in fetch_units(conn):
        latest = ROOT / row["latest_path"]
        hub = LATEST_ROOT / row["benchmark_id"]
        ctx = {
            "title": row["proof_label"] or row["unit_id"],
            "status": row["refreshability_status"],
            "benchmark_id": row["benchmark_id"],
            "protocol_id": row["protocol_id"],
            "archive_path": row["archive_path"],
            "latest_path": row["latest_path"],
            "unit_id": row["unit_id"],
        }
        if row["benchmark_id"] not in hubs_done:
            write_if_missing(hub / "index.md", PLACEHOLDER_INDEX.format(**ctx))
            write_if_missing(hub / "TUTORIAL.md", PLACEHOLDER_DOC.format(**ctx, kind="tutorial"))
            write_if_missing(hub / "METHODOLOGY.md", PLACEHOLDER_DOC.format(**ctx, kind="methodology"))
            created_docs += 3
            hubs_done.add(row["benchmark_id"])
        write_if_missing(latest / "index.md", PLACEHOLDER_INDEX.format(**ctx))
        write_if_missing(latest / "EXECUTION-STEPS.md", PLACEHOLDER_STEPS.format(**ctx))
        created_docs += 2
        if row["refreshability_status"] == "refreshable" or row["refreshability_status"] in {
            "assigned",
            "pending",
            "running",
        }:
            for sub in (latest / "quick", latest / "full" / "proof", latest / "full" / "static"):
                sub.mkdir(parents=True, exist_ok=True)
                created_dirs += 1
    index = LATEST_ROOT / "index.md"
    write_if_missing(
        index,
        (
            "# Published grades — results-5.0.1\n\n"
            "Active UHBS 5.0.1 refresh line. Historical proof is preserved under "
            "`docs/conformance/archive/v5.0.0/` and "
            "`docs/conformance/latest/results-5.0.0/`.\n\n"
            "See [benchmark-manifest.yaml](benchmark-manifest.yaml) and [RUN-LEDGER.md](RUN-LEDGER.md).\n"
        ),
    )
    return {"hubs": len(hubs_done), "docs_touched": created_docs, "dirs": created_dirs}


def cmd_init_db(args: argparse.Namespace) -> int:
    init_db(Path(args.db))
    return 0


def cmd_generate_manifest(args: argparse.Namespace) -> int:
    units = discover_units()
    dest = Path(args.manifest)
    write_manifest(units, dest)
    hubs = {u["benchmark_id"] for u in units}
    refreshable_hubs = {u["benchmark_id"] for u in units if u["refreshability_status"] == "refreshable"}
    legacy_hubs = {u["benchmark_id"] for u in units if u["refreshability_status"] == "legacy-not-refreshed"}
    emit(
        {
            "manifest": rel(dest),
            "hubs": len(hubs),
            "units": len(units),
            "refreshable_hubs": len(refreshable_hubs),
            "legacy_hubs": len(legacy_hubs),
            "refreshable_units": sum(1 for u in units if u["refreshability_status"] == "refreshable"),
            "legacy_units": sum(1 for u in units if u["refreshability_status"] == "legacy-not-refreshed"),
            "blocked_units": sum(1 for u in units if str(u["refreshability_status"]).startswith("blocked")),
        }
    )
    return 0


def cmd_import_manifest(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        init_db_silent = False
        n = execute(conn, "SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_units'").fetchone()
        if n is None:
            conn.executescript(SCHEMA_SQL)
            init_db_silent = True
        count = import_manifest(conn, Path(args.manifest))
        emit({"imported": count, "manifest": args.manifest, "schema_created": init_db_silent})
    finally:
        conn.close()
    return 0


def cmd_claim_next(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        row = claim_next(conn, args.agent)
        if row is None:
            emit({"unit_id": None, "message": "no claimable units"})
            return 0
        emit({"unit_id": row["unit_id"], "unit": row_public(row), "agent": args.agent})
    finally:
        conn.close()
    return 0


def cmd_claim_unit(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        row = claim_unit(conn, args.unit_id, args.agent, force=bool(getattr(args, "force", False)))
        if row is None:
            emit(
                {"unit_id": args.unit_id, "agent": args.agent, "claimed": False, "message": "claim failed"},
                ok=False,
            )
            return 2
        emit({"unit_id": row["unit_id"], "unit": row_public(row), "agent": args.agent, "claimed": True})
    finally:
        conn.close()
    return 0


def cmd_log_run_start(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        emit(log_run_start(conn, args))
    finally:
        conn.close()
    return 0


def cmd_log_run_finish(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        emit(log_run_finish(conn, args))
    finally:
        conn.close()
    return 0


def cmd_log_blocker(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        emit(log_blocker(conn, args))
    finally:
        conn.close()
    return 0


def cmd_set_fixture(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        set_fixture(conn, args.unit_id, args.fixture_path)
        emit({"unit_id": args.unit_id, "fixture_path": rel(args.fixture_path)})
    finally:
        conn.close()
    return 0


def cmd_set_unit_meta(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        emit({"unit": set_unit_meta(conn, args)})
    finally:
        conn.close()
    return 0


def cmd_sync_ledger(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        gate_d = True if args.declare_gate_d_open else None
        if args.declare_gate_d_closed:
            gate_d = False
        render_ledger(conn, Path(args.ledger), gate_d_open=gate_d)
        emit({"ledger": args.ledger, "gate_d_open": bool(gate_d) if gate_d is not None else "unchanged"})
    finally:
        conn.close()
    return 0


def cmd_generate_skeleton(args: argparse.Namespace) -> int:
    conn = connect(Path(args.db))
    try:
        stats = generate_skeleton(conn)
        emit(stats)
    finally:
        conn.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UHBS benchmark-refresh tracker")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-db", help="Create schema, WAL, busy_timeout")
    p.set_defaults(func=cmd_init_db)

    p = sub.add_parser("generate-manifest", help="Enumerate reports×labs into benchmark-manifest.yaml")
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p.set_defaults(func=cmd_generate_manifest)

    p = sub.add_parser("import-manifest", help="Load units from YAML into SQLite")
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p.set_defaults(func=cmd_import_manifest)

    p = sub.add_parser("claim-next", help="Atomically claim the next refreshable unit")
    p.add_argument("--agent", required=True)
    p.set_defaults(func=cmd_claim_next)

    p = sub.add_parser("claim-unit", help="Atomically claim a specific unit")
    p.add_argument("--unit-id", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--force", action="store_true", help="Re-claim even if already assigned/ran")
    p.set_defaults(func=cmd_claim_unit)

    p = sub.add_parser("log-run-start", help="Insert a running execution row")
    p.add_argument("--unit-id", required=True)
    p.add_argument("--mode", required=True, choices=["quick", "full"])
    p.add_argument("--uhbs-version", default="5.0.1")
    p.add_argument("--grader-image", default=None)
    p.add_argument("--target-image", default=None)
    p.add_argument("--base-image", default=None)
    p.add_argument("--base-image-reason", default=None)
    p.add_argument("--strategy", default=None, dest="strategy")
    p.add_argument("--telemetry-mode", default=None)
    p.add_argument("--airgap-attested", action="store_true")
    p.add_argument("--notes", default=None)
    p.set_defaults(func=cmd_log_run_start)

    p = sub.add_parser("log-run-finish", help="Record outputs, hashes, and scores for a run")
    p.add_argument("--unit-id", required=True)
    p.add_argument("--mode", required=True, choices=["quick", "full"])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--cast-path", default=None)
    p.add_argument("--status", default="succeeded")
    p.set_defaults(func=cmd_log_run_finish)

    p = sub.add_parser("log-blocker", help="Record a blocker and mark the unit blocked")
    p.add_argument("--unit-id", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--log-path", default=None)
    p.add_argument("--details", default=None)
    p.add_argument("--blocker-type", default="execution")
    p.add_argument("--status", default=None, help="Optional refreshability_status override")
    p.set_defaults(func=cmd_log_blocker)

    p = sub.add_parser("set-fixture", help="Bind a canonical fixture path to a unit")
    p.add_argument("--unit-id", required=True)
    p.add_argument("--fixture-path", required=True)
    p.set_defaults(func=cmd_set_fixture)

    p = sub.add_parser("set-unit-meta", help="Record upstream SHA / runtime metadata")
    p.add_argument("--unit-id", required=True)
    p.add_argument("--upstream-repo", default=None)
    p.add_argument("--upstream-branch", default=None)
    p.add_argument("--upstream-commit", default=None)
    p.add_argument("--base-image", default=None)
    p.add_argument("--base-image-reason", default=None)
    p.add_argument("--strategy", default=None)
    p.set_defaults(func=cmd_set_unit_meta)

    p = sub.add_parser("sync-ledger", help="Rewrite RUN-LEDGER.md from SQLite")
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    p.add_argument("--declare-gate-d-open", action="store_true")
    p.add_argument("--declare-gate-d-closed", action="store_true")
    p.set_defaults(func=cmd_sync_ledger)

    p = sub.add_parser("generate-skeleton", help="Create latest/results-5.0.1 placeholder trees")
    p.set_defaults(func=cmd_generate_skeleton)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
