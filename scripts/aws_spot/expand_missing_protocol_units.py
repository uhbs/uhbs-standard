#!/usr/bin/env python3
"""Expand inventory/TPS/recipes/DB for missing UHBS-supported protocol units.

Reads `.local/benchmark-refresh/protocol-audit/coverage.json` and adds units for
each `missing_gradable` row that has a known default port.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "aws_spot"))
from lab_recipes import RECIPES  # noqa: E402

PORTS: dict[str, int] = {
    "ftp": 21,
    "ssh": 22,
    "telnet": 23,
    "dns": 53,
    "smtp": 25,
    "http": 80,
    "pop3": 110,
    "imap": 143,
    "ldap": 389,
    "https": 443,
    "smb": 445,
    "modbus": 502,
    "ipp": 631,
    "tftp": 69,
    "ntp": 123,
    "snmp": 161,
    "irc": 6667,
    "dhcp": 67,
    "sip": 5060,
    "mqtt": 1883,
    "mssql": 1433,
    "mysql": 3306,
    "rdp": 3389,
    "postgres": 5432,
    "vnc": 5900,
    "redis": 6379,
    "memcache": 11211,
    "mongodb": 27017,
    "elasticsearch": 9200,
    "socks5": 1080,
    "pjl": 9100,
    "mcp": 8000,
    "git": 9418,
    "oracle": 1521,
    "s7comm": 102,
    "httpproxy": 8080,
    "bacnet": 47808,
    "pptp": 1723,
    "upnp": 1900,
}

CLASS_FOR: dict[str, str] = {
    "http": "Web-API",
    "https": "Web-API",
    "httpproxy": "Web-API",
    "mcp": "Web-API",
    "elasticsearch": "Web-API",
    "modbus": "ICS-SCADA",
    "s7comm": "ICS-SCADA",
    "bacnet": "ICS-SCADA",
    "mysql": "Database",
    "mssql": "Database",
    "postgres": "Database",
    "mongodb": "Database",
    "redis": "Database",
    "memcache": "Database",
    "oracle": "Database",
}


def tps_body(proto: str, cls: str, mode: str) -> str:
    samples = 50 if mode == "quick" else 200
    return (
        f"# {mode.title()} TPS — {cls}-{proto.upper()} / {cls} / {proto}\n"
        "target_metadata:\n"
        f'  name: "{cls}-{proto.upper()}"\n'
        f'  class: "{cls}"\n'
        f'  protocol: "{proto}"\n'
        f'  protocols: ["{proto}"]\n'
        "\n"
        "performance_baseline:\n"
        "  expected_p95_latency_ms: 150\n"
        "  strict_rfc_enforcement: true\n"
        f"  timing_samples: {samples}\n"
        "\n"
        "safety_boundary:\n"
        "  allowed_outbound_traffic: false\n"
        "  allow_local_code_execution: false\n"
    )


def ensure_tps(lab_dir: Path, proto: str, cls: str) -> tuple[str, str]:
    prefix = {
        "Web-API": "web_api",
        "ICS-SCADA": "ics_scada",
        "Database": "database",
        "Low-Interaction": "low_interaction",
        "POSIX-Shell": "posix_shell",
        "GenAI-Shell": "genai_shell",
    }.get(cls, "low_interaction")
    quick = lab_dir / f"{prefix}_{proto}_quick.yaml"
    full = lab_dir / f"{prefix}_{proto}_full.yaml"
    if not quick.is_file():
        quick.write_text(tps_body(proto, cls, "quick"), encoding="utf-8")
    if not full.is_file():
        full.write_text(tps_body(proto, cls, "full"), encoding="utf-8")
    return (
        str(quick.relative_to(ROOT)),
        str(full.relative_to(ROOT)),
    )


def upsert_inventory_site(
    inv_path: Path,
    *,
    unit_id: str,
    proto: str,
    port: int,
    cls: str,
    alias: str,
    image: str,
    full_tps: str,
) -> None:
    inv_path.parent.mkdir(parents=True, exist_ok=True)
    block = (
        f"  {unit_id}:\n"
        f"    kind: generic\n"
        f"    class: {cls}\n"
        f"    host: {alias}\n"
        f"    protocol: {proto}\n"
        f"    protocols: [{proto}]\n"
        f"    port: {port}\n"
        f"    ports:\n"
        f"      {proto}: {port}\n"
        f"    source_root: /honeypot\n"
        f"    telemetry_dir: /telemetry\n"
        f"    tps: /work/{full_tps}\n"
        f"    container_image: {image}\n"
    )
    if inv_path.is_file():
        text = inv_path.read_text(encoding="utf-8")
        if f"  {unit_id}:" in text:
            return
        if not text.rstrip().endswith("\n"):
            text += "\n"
        if "sites:" not in text:
            text = "sites:\n" + text
        inv_path.write_text(text + block, encoding="utf-8")
    else:
        inv_path.write_text("# Auto-expanded multi-protocol inventory\nsites:\n" + block, encoding="utf-8")


def add_recipe(
    *,
    unit_id: str,
    template: dict,
    proto: str,
    port: int,
) -> None:
    if unit_id in RECIPES:
        return
    bench = template["bench"]
    alias = template.get("alias") or f"{bench}-lab"
    container = f"uhbs-target-{unit_id}"
    image = template["image"]
    telem = template.get("telemetry_mount") or f".local/labs/{bench}-telemetry"
    honeypot = template.get("honeypot_mount") or f".local/labs/{bench}"
    build = list(template.get("build") or [])
    # Prefer pull/build from template; start is unit-specific.
    start = [
        f"docker rm -f {container} 2>/dev/null || true",
        f'mkdir -p {telem} && touch {telem}/egress-gateway.log',
        (
            f"docker run -d --name {container} --label uhbs.unit={unit_id} "
            f"--network uhbs-lab --network-alias {alias} "
            f"-p 0.0.0.0:{port}:{port} "
            f'-v "$PWD/{telem}:/telemetry:rw" {image}'
        ),
    ]
    RECIPES[unit_id] = {
        "bench": bench,
        "repo": template["repo"],
        "image": image,
        "container": container,
        "alias": alias,
        "port": port,
        "publish": True,
        "strategy": template.get("strategy", "upstream-docker"),
        "base_image": template.get("base_image", image),
        "base_image_reason": template.get(
            "base_image_reason", "Expanded from documented protocol surface."
        ),
        "build": build,
        "start": start,
        "honeypot_mount": honeypot,
        "telemetry_mount": telem,
    }


def rewrite_recipes_py() -> None:
    path = ROOT / "scripts" / "aws_spot" / "lab_recipes.py"
    # Use repr so Python True/False/None stay valid (json.dumps breaks import).
    body = (
        '"""Auto-generated Spot lab start recipes for UHBS 5.0.1."""\n'
        "from __future__ import annotations\n\n"
        f"RECIPES: dict[str, dict] = {repr(RECIPES)}\n\n\n"
        "def recipe_for(unit_id: str) -> dict | None:\n"
        "    return RECIPES.get(unit_id)\n"
    )
    path.write_text(body, encoding="utf-8")


def upsert_db_row(
    *,
    unit_id: str,
    bench: str,
    proto: str,
    inv: str,
    quick_tps: str,
    full_tps: str,
    cls: str,
    port: int,
    repo: str,
) -> None:
    db = ROOT / ".local" / "benchmark-refresh" / "results-5.0.1.sqlite3"
    conn = sqlite3.connect(db)
    latest = f"docs/conformance/latest/results-5.0.1/{bench}/{proto}"
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    exists = conn.execute(
        "SELECT 1 FROM benchmark_units WHERE unit_id=?", (unit_id,)
    ).fetchone()
    if exists:
        conn.execute(
            """
            UPDATE benchmark_units SET
              protocol_id=?, inventory_path=?, quick_tps_path=?, full_tps_path=?,
              latest_path=?, class_name=?, target_port=?, updated_at=?
            WHERE unit_id=?
            """,
            (proto, inv, quick_tps, full_tps, latest, cls, port, now, unit_id),
        )
    else:
        report_path = f"docs/conformance/reports/{bench}/{proto}"
        conn.execute(
            """
            INSERT INTO benchmark_units (
              unit_id, benchmark_id, protocol_id, proof_label, upstream_repo,
              current_report_path, archive_path, latest_path, lab_dir,
              inventory_path, quick_tps_path, full_tps_path, fixture_path,
              class_name, target_host, target_port, refreshability_status,
              created_at, updated_at, telemetry_required
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                unit_id,
                bench,
                proto,
                f"{bench} ({proto})",
                repo,
                report_path,
                f"docs/conformance/archive/v5.0.1/{bench}/{proto}",
                latest,
                f"docs/conformance/labs/{bench}",
                inv,
                quick_tps,
                full_tps,
                f"docs/conformance/fixtures/{unit_id}.scorecard.json",
                cls,
                f"{bench}-lab",
                port,
                "local-docker",
                now,
                now,
                1,
            ),
        )
    conn.commit()
    conn.close()


def main() -> int:
    cov_path = ROOT / ".local" / "benchmark-refresh" / "protocol-audit" / "coverage.json"
    cov = json.loads(cov_path.read_text(encoding="utf-8"))
    missing = cov.get("missing_gradable_units") or []

    # Template recipe per bench (first existing unit).
    templates: dict[str, dict] = {}
    for uid, r in RECIPES.items():
        templates.setdefault(r["bench"], r)

    added = []
    skipped = []
    for row in missing:
        bench = row["bench"]
        proto = row["protocol"]
        unit_id = f"{bench}-{proto}"
        port = PORTS.get(proto)
        if port is None:
            skipped.append({**row, "reason": "no_default_port"})
            continue
        tmpl = templates.get(bench)
        if not tmpl:
            skipped.append({**row, "reason": "no_template_recipe"})
            continue
        cls = CLASS_FOR.get(proto, "Low-Interaction")
        lab_dir = ROOT / "docs" / "conformance" / "labs" / bench
        lab_dir.mkdir(parents=True, exist_ok=True)
        quick_tps, full_tps = ensure_tps(lab_dir, proto, cls)
        inv_rel = f"docs/conformance/labs/{bench}/inventory.yaml"
        inv_path = ROOT / inv_rel
        alias = tmpl.get("alias") or f"{bench}-lab"
        upsert_inventory_site(
            inv_path,
            unit_id=unit_id,
            proto=proto,
            port=port,
            cls=cls,
            alias=alias,
            image=tmpl["image"],
            full_tps=full_tps,
        )
        add_recipe(unit_id=unit_id, template=tmpl, proto=proto, port=port)
        upsert_db_row(
            unit_id=unit_id,
            bench=bench,
            proto=proto,
            inv=inv_rel,
            quick_tps=quick_tps,
            full_tps=full_tps,
            cls=cls,
            port=port,
            repo=tmpl["repo"],
        )
        added.append(unit_id)

    rewrite_recipes_py()
    out = {
        "added": added,
        "skipped": skipped,
        "added_count": len(added),
        "skipped_count": len(skipped),
    }
    out_path = (
        ROOT / ".local" / "benchmark-refresh" / "protocol-audit" / "expanded-units.json"
    )
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
