#!/usr/bin/env python3
"""Audit Module C telemetry sinks for results-5.0.1 / lab inventory.

Reports, per unit:
  - TPS/inventory telemetry_dir expectation
  - local ``.local/labs/<product>-telemetry`` presence
  - file counts (any vs *.json/*.jsonl)
  - parseable record count (same loader Module C uses)
  - UHBS_INJECT markers present
  - whether SSH inject is possible for this protocol
  - published Module C complete/score from full/report.json

Exit 0 always (informational). Use ``--fail-empty`` to exit 1 when any
``telemetry_required`` unit has an empty/missing sink.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uhbs_core.test_telemetry import _iter_records  # noqa: E402

DEFAULT_RESULTS = ROOT / "docs/conformance/latest/results-5.0.1"
DEFAULT_MANIFEST = DEFAULT_RESULTS / "benchmark-manifest.yaml"
DEFAULT_LABS = ROOT / ".local/labs"
INJECT_RE = re.compile(r"UHBS_INJECT:")
SSH_PROTOS = frozenset({"ssh", "telnet"})  # shell-exec surface for current C2


@dataclass
class UnitAudit:
    unit_id: str
    benchmark_id: str
    protocol_id: str
    telemetry_required: bool
    latest_path: str | None
    local_telemetry_dir: str | None
    local_dir_exists: bool
    files_any: int
    files_json: int
    parseable_records: int
    inject_markers: bool
    inject_capable_ssh: bool
    published_c_score: float | None
    published_c_complete: bool | None
    published_c_detail: str | None
    status: str  # ok | empty_sink | missing_dir | no_json | incomplete_report | legacy


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _product(benchmark_id: str) -> str:
    return benchmark_id


def _count_inject(path: Path) -> bool:
    if not path.exists():
        return False
    files = [path] if path.is_file() else list(path.rglob("*"))
    for fp in files:
        if not fp.is_file() or fp.stat().st_size == 0 or fp.stat().st_size > 80_000_000:
            continue
        try:
            # cheap scan: first/last chunks
            with fp.open("rb") as handle:
                head = handle.read(512_000)
                handle.seek(max(0, fp.stat().st_size - 512_000))
                tail = handle.read(512_000)
            blob = head + tail
            if INJECT_RE.search(blob.decode("utf-8", errors="replace")):
                return True
        except OSError:
            continue
    return False


def _module_c_from_report(report_path: Path) -> tuple[float | None, bool | None, str | None]:
    if not report_path.is_file():
        return None, None, None
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, None, "invalid report.json"
    for mod in data.get("modules") or []:
        if mod.get("module") != "C" and mod.get("dimension") != "telemetry":
            continue
        detail = None
        for check in mod.get("checks") or []:
            cid = str(check.get("id") or "")
            if cid.startswith("c1.") or "telemetry" in cid:
                detail = str(check.get("detail") or "")[:120]
                break
        return (
            float(mod.get("score") or 0.0),
            bool(mod.get("complete")) if "complete" in mod else None,
            detail,
        )
    uhqs = data.get("uhqs") or {}
    if isinstance(uhqs, dict) and "S_C" in uhqs:
        return float(uhqs.get("S_C") or 0.0), None, "from uhqs.S_C only"
    return None, None, "no Module C in report"


def audit_unit(row: dict[str, Any], root: Path, labs: Path) -> UnitAudit:
    unit_id = str(row.get("unit_id") or "")
    benchmark_id = str(row.get("benchmark_id") or unit_id.split("-")[0])
    protocol_id = str(row.get("protocol_id") or "")
    telemetry_required = bool(row.get("telemetry_required"))
    latest_rel = row.get("latest_path")
    latest = (root / latest_rel) if latest_rel else None

    local = labs / f"{_product(benchmark_id)}-telemetry"
    exists = local.is_dir()
    files_any = 0
    files_json = 0
    records = 0
    if exists:
        for fp in local.rglob("*"):
            if fp.is_file() and fp.stat().st_size > 0:
                files_any += 1
                if fp.suffix in {".json", ".jsonl"}:
                    files_json += 1
        records = len(_iter_records(local, limit=800))

    inject = _count_inject(local) if exists else False
    inject_capable = protocol_id.lower() in SSH_PROTOS

    c_score = c_complete = c_detail = None
    if latest and (latest / "full" / "report.json").is_file():
        c_score, c_complete, c_detail = _module_c_from_report(latest / "full" / "report.json")

    if str(row.get("refreshability_status") or "").startswith("legacy"):
        status = "legacy"
    elif not telemetry_required:
        status = "ok"
    elif not exists:
        status = "missing_dir"
    elif records == 0 and files_json == 0:
        status = "no_json" if files_any else "empty_sink"
    elif records == 0:
        status = "empty_sink"
    elif c_complete is False:
        status = "incomplete_report"
    else:
        status = "ok"

    return UnitAudit(
        unit_id=unit_id,
        benchmark_id=benchmark_id,
        protocol_id=protocol_id,
        telemetry_required=telemetry_required,
        latest_path=str(latest_rel) if latest_rel else None,
        local_telemetry_dir=str(local.relative_to(root)) if exists else str(local),
        local_dir_exists=exists,
        files_any=files_any,
        files_json=files_json,
        parseable_records=records,
        inject_markers=inject,
        inject_capable_ssh=inject_capable,
        published_c_score=c_score,
        published_c_complete=c_complete,
        published_c_detail=c_detail,
        status=status,
    )


def load_units(manifest: Path) -> list[dict[str, Any]]:
    data = _load_yaml(manifest)
    return list(data.get("units") or [])


def render_table(rows: list[UnitAudit]) -> str:
    lines = [
        "| unit | proto | req | status | files | json | records | inject | ssh-inject | C score | C complete |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | --- |",
    ]
    for r in rows:
        lines.append(
            f"| `{r.unit_id}` | {r.protocol_id} | {r.telemetry_required} | {r.status} | "
            f"{r.files_any} | {r.files_json} | {r.parseable_records} | "
            f"{r.inject_markers} | {r.inject_capable_ssh} | "
            f"{'' if r.published_c_score is None else r.published_c_score} | "
            f"{r.published_c_complete} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--labs", default=str(DEFAULT_LABS))
    parser.add_argument(
        "--fail-empty",
        action="store_true",
        help="exit 1 if any telemetry_required unit is empty/missing/incomplete",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON array")
    parser.add_argument(
        "--markdown-out",
        default="",
        help="optional path to write a markdown report",
    )
    args = parser.parse_args(argv)
    root = Path(args.root)
    units = load_units(Path(args.manifest))
    audits = [audit_unit(u, root, Path(args.labs)) for u in units]
    required = [a for a in audits if a.telemetry_required]
    status_counts = Counter(a.status for a in required)

    if args.json:
        print(json.dumps([asdict(a) for a in audits], indent=2))
    else:
        print(f"units={len(audits)} telemetry_required={len(required)}")
        print("status mix (required only):", dict(status_counts))
        print()
        # problem rows first
        problems = [a for a in required if a.status != "ok"]
        print(f"problems ({len(problems)}):")
        print(render_table(sorted(problems, key=lambda a: (a.status, a.unit_id))))
        print()
        ok = [a for a in required if a.status == "ok"]
        if ok:
            print(f"ok ({len(ok)}):")
            print(render_table(sorted(ok, key=lambda a: a.unit_id)))

    if args.markdown_out:
        out = Path(args.markdown_out)
        body = [
            "# Telemetry sink audit",
            "",
            f"units={len(audits)} · telemetry_required={len(required)} · "
            f"status={dict(status_counts)}",
            "",
            "## Problems",
            "",
            render_table(sorted([a for a in required if a.status != "ok"], key=lambda a: (a.status, a.unit_id))),
            "",
            "## OK",
            "",
            render_table(sorted([a for a in required if a.status == "ok"], key=lambda a: a.unit_id)),
            "",
        ]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(body), encoding="utf-8")
        print(f"wrote {out}", file=sys.stderr)

    if args.fail_empty and any(a.status != "ok" for a in required):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
