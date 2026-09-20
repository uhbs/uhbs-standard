#!/usr/bin/env python3
"""Module C — Telemetry Assurance (UHBS v5.0.0).

C1: Declared-format structural conformance (native JSON / ECS / OCSF / OTLP / STIX)
C2: Sink-side injection resilience
C3: Required observable coverage (per profile class)
C4: Ground-truth completeness / timeliness
C5: CTI semantics (pinned ATT&CK) when mappings are claimed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Optional

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from uhbs_core.check_scoring import summarize_checks  # noqa: E402
from uhbs_core.hqs import pass_status  # noqa: E402
from uhbs_core.models import CheckOutcome, CheckResult, ModuleResult, TargetSpec  # noqa: E402
from uhbs_core.ssh_session import run_ssh_command  # noqa: E402
from uhbs_core.telemetry.attack import (  # noqa: E402
    extract_technique_ids,
    validate_technique_id,
)
from uhbs_core.telemetry.formats import (  # noqa: E402
    looks_like_stix_candidate,
    normalize_format,
    validate_records,
    validate_stix21,
)
from uhbs_core.telemetry.groundtruth import (  # noqa: E402
    assess_sink_resilience,
    injection_payloads,
    make_tagged_interactions,
    match_ground_truth,
    new_run_id,
)
from uhbs_core.tps import TPS  # noqa: E402

_OBS_PATH = Path(__file__).resolve().parent / "data" / "observables" / "required_by_class.json"


def _iter_jsonl_lines(text: str, *, limit: int, rows: list[Any]) -> None:
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"__malformed__": line[:120]})
        if len(rows) >= limit:
            return


def _iter_records(path: Path, limit: int = 800) -> List[Any]:
    rows: List[Any] = []
    files: List[Path]
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted(path.rglob("*.jsonl")) + sorted(path.rglob("*.json"))
    else:
        return rows
    for fp in files[:60]:
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if fp.suffix == ".json":
            try:
                rows.append(json.loads(text))
            except json.JSONDecodeError:
                before = len(rows)
                _iter_jsonl_lines(text, limit=limit, rows=rows)
                if len(rows) == before:
                    rows.append({"__malformed__": str(fp)})
            if len(rows) >= limit:
                return rows
            continue
        _iter_jsonl_lines(text, limit=limit, rows=rows)
        if len(rows) >= limit:
            return rows
    return rows


def _flatten(obj: Any) -> List[Any]:
    if isinstance(obj, list):
        out: List[Any] = []
        for x in obj:
            out.extend(_flatten(x))
        return out
    if isinstance(obj, dict):
        if "objects" in obj and isinstance(obj["objects"], list):
            return _flatten(obj["objects"]) + [obj]
        return [obj]
    return []


def _load_required_observables(profile_class: str) -> list[str]:
    if _OBS_PATH.is_file():
        data = json.loads(_OBS_PATH.read_text(encoding="utf-8"))
        return list(data.get(profile_class) or data.get("Low-Interaction") or [])
    return ["event_time", "source_endpoint", "protocol_action"]


def _declared_formats(target: TargetSpec, tps: Optional[TPS]) -> list[str]:
    formats: list[str] = []
    native = target.native_event_format
    exports = list(target.export_formats or [])
    if tps is not None:
        # TPS may expose telemetry dict on raw profile
        raw = getattr(tps, "raw", None) or {}
        tel = raw.get("telemetry") if isinstance(raw, dict) else None
        if isinstance(tel, dict):
            native = native or tel.get("native_event_format")
            exp = tel.get("export_formats") or []
            if isinstance(exp, list):
                exports.extend(str(x) for x in exp)
    if native:
        formats.append(str(native))
    formats.extend(str(x) for x in exports)
    # Dedupe
    seen: set[str] = set()
    out: list[str] = []
    for f in formats:
        n = normalize_format(f) or f
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _observable_coverage(flat: list[Any], required: list[str]) -> tuple[float, str]:
    if not required:
        return 1.0, "no required observables"
    blob = json.dumps(flat, default=str).lower()
    # Heuristic field synonyms
    synonyms = {
        "event_time": ["timestamp", "@timestamp", "event_time", "time", "created"],
        "source_endpoint": ["src", "source", "src_ip", "client_ip", "srcip"],
        "destination_endpoint": ["dst", "destination", "dest", "dst_ip"],
        "protocol_action": ["action", "event.action", "verb", "method", "command"],
        "authentication_result": ["auth", "login", "password", "accepted", "failed"],
        "command_content": ["command", "cmd", "input", "message"],
        "request_content": ["request", "path", "query", "body", "message"],
        "session_id": ["session", "session_id", "sid", "connection_id"],
    }
    hits = 0
    missing: list[str] = []
    for field in required:
        keys = synonyms.get(field, [field])
        if any(k.lower() in blob for k in keys):
            hits += 1
        else:
            missing.append(field)
    ratio = hits / len(required)
    detail = f"{hits}/{len(required)} observables present"
    if missing:
        detail += f" missing={missing[:5]}"
    return ratio, detail


def run(target: TargetSpec, tps: Optional[TPS] = None) -> ModuleResult:
    checks: List[CheckResult] = []
    notes: list[str] = [
        "UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4",
    ]
    run_id = new_run_id()
    profile_class = (tps.profile_class if tps else None) or target.profile_class

    tdir = Path(target.telemetry_dir).expanduser() if target.telemetry_dir else None
    has_telemetry = bool(tdir and tdir.exists())

    if not has_telemetry:
        # Applicable telemetry assurance cannot complete without a sink.
        checks.append(
            CheckResult.make(
                id="c1.telemetry_dir",
                team="blue",
                outcome=CheckOutcome.NOT_TESTED,
                detail="telemetry_dir missing — Module C incomplete until sink is provided",
                mandatory=True,
                catalog_id="C1",
            )
        )
        checks.append(
            CheckResult.make(
                id="c4.ground_truth",
                team="blue",
                outcome=CheckOutcome.NOT_TESTED,
                detail="no telemetry sink for ground-truth matching",
                mandatory=True,
                catalog_id="C4",
            )
        )
        agg = summarize_checks(checks)
        return ModuleResult(
            module="C",
            dimension="telemetry",
            score=0.0,
            status="INCOMPLETE",
            checks=checks,
            notes=notes,
            complete=False,
            applicable_checks=agg.applicable,
            scored_checks=agg.scored,
            metrics={
                "collection_capability": {"status": "INCOMPLETE", "reason": "no_telemetry_dir"},
                "coverage": agg.coverage,
                "not_tested": agg.not_tested,
            },
        )

    rows = _iter_records(tdir)  # type: ignore[arg-type]
    flat: list[Any] = []
    malformed = 0
    for r in rows:
        if isinstance(r, dict) and "__malformed__" in r:
            malformed += 1
        else:
            flat.extend(_flatten(r))
    dict_rows = [x for x in flat if isinstance(x, dict)]

    # C1 — parse cleanliness always applicable when sink exists
    total = max(len(rows), 1)
    parse_score = 100.0 * (1.0 - malformed / total)
    checks.append(
        CheckResult.make(
            id="c1.json_parse_clean",
            team="blue",
            outcome=CheckOutcome.PASS if malformed == 0 else CheckOutcome.FAIL,
            detail=f"{malformed} malformed / {len(rows)} records",
            score=parse_score,
            catalog_id="C1",
        )
    )

    declared = _declared_formats(target, tps)
    if not declared:
        # No format claimed → native_json best-effort only; STIX not required
        declared = ["native_json"]
        notes.append("no native_event_format declared — validating as native_json only")

    for fmt in declared:
        result = validate_records(fmt, dict_rows)
        if result.checked == 0:
            checks.append(
                CheckResult.make(
                    id=f"c1.format.{result.format_id}",
                    team="blue",
                    outcome=CheckOutcome.FAIL,
                    detail=f"declared {result.format_id} but no matching records",
                    score=0.0,
                    catalog_id="C1",
                    evidence=[f"schema={result.schema_uri}", f"validator={result.validator_version}"],
                )
            )
        else:
            ratio = result.passed / result.checked
            checks.append(
                CheckResult.make(
                    id=f"c1.format.{result.format_id}",
                    team="blue",
                    outcome=CheckOutcome.PASS if ratio >= 0.95 else CheckOutcome.FAIL,
                    detail=(
                        f"{result.format_id} ok={result.passed}/{result.checked}; "
                        f"errors={result.errors[:3]}"
                    ),
                    score=100.0 * ratio,
                    catalog_id="C1",
                    evidence=[
                        f"schema={result.schema_uri}",
                        f"version={result.schema_version}",
                        f"validator={result.validator_version}",
                    ],
                )
            )

    # Guard: never award STIX credit for non-STIX honeypot types (regression)
    if "stix21" not in declared and "stix" not in declared:
        false_stix = 0
        for obj in dict_rows:
            if "type" in obj and not looks_like_stix_candidate(obj):
                ok, _ = validate_stix21(obj)
                if ok:
                    false_stix += 1
        if false_stix > 0:
            checks.append(
                CheckResult.make(
                    id="c1.stix_false_positive",
                    team="blue",
                    outcome=CheckOutcome.FAIL,
                    detail=(
                        f"{false_stix} non-STIX records incorrectly validated as STIX"
                    ),
                    score=0.0,
                    catalog_id="C1",
                    mandatory=True,
                )
            )
        else:
            checks.append(
                CheckResult.make(
                    id="c1.stix_not_required",
                    team="blue",
                    outcome=CheckOutcome.NOT_APPLICABLE,
                    detail="STIX not declared — format credit not claimed for non-STIX logs",
                    score=0.0,
                    catalog_id="C1",
                    mandatory=False,
                    applicability_rationale=(
                        "STIX 2.1 not in declared native_event_format"
                    ),
                )
            )

    # C2 — sink-side injection resilience
    port = target.shell_exec_port()
    payload_ids: list[str] = []
    rows_after_flat: list[Any] | None = None
    if target.host and port is not None:
        for pid, cmd in injection_payloads(run_id):
            payload_ids.append(pid)
            out = run_ssh_command(
                target.host,
                port,
                target.user,
                target.password,
                cmd,
                timeout=15,
                known_hosts=target.known_hosts_path(),
            )
            # Shell acceptance is evidence of delivery attempt, not the score.
            _ = out
        # Re-read sink after injection — subsequent checks must use this snapshot.
        rows_after = _iter_records(tdir)  # type: ignore[arg-type]
        flat_after: list[Any] = []
        for r in rows_after:
            if isinstance(r, dict) and "__malformed__" not in r:
                flat_after.extend(_flatten(r))
            elif isinstance(r, dict) and "__malformed__" in r:
                flat_after.append(r)
        rows_after_flat = flat_after
        dict_rows = [x for x in flat_after if isinstance(x, dict)]
        assessment = assess_sink_resilience(flat_after, run_id, payload_ids)
        checks.append(
            CheckResult.make(
                id="c2.sink_injection_resilience",
                team="red",
                outcome=CheckOutcome.PASS if assessment["ok"] else CheckOutcome.FAIL,
                detail=(
                    f"markers={assessment['markers_found']} "
                    f"malformed={assessment['malformed_records']}"
                ),
                score=100.0 if assessment["ok"] else 0.0,
                catalog_id="C2",
                evidence=[json.dumps(assessment)[:500]],
            )
        )
    else:
        checks.append(
            CheckResult.make(
                id="c2.sink_injection_resilience",
                team="red",
                outcome=CheckOutcome.NOT_TESTED,
                detail="no SSH exec surface to deliver injection payloads",
                mandatory=True,
                catalog_id="C2",
            )
        )

    # Prefer post-injection sink for C3–C5 when available
    sink_rows = dict_rows if rows_after_flat is None else [
        x for x in rows_after_flat if isinstance(x, dict)
    ]

    # C3 — required observables
    required = _load_required_observables(profile_class)
    ratio, detail = _observable_coverage(sink_rows, required)
    checks.append(
        CheckResult.make(
            id="c3.observable_coverage",
            team="blue",
            outcome=CheckOutcome.PASS if ratio >= 0.6 else CheckOutcome.FAIL,
            detail=detail,
            score=100.0 * ratio,
            catalog_id="C3",
        )
    )

    # C4 — ground-truth (manifest recorded; match against post-injection sink)
    manifest = make_tagged_interactions(run_id, count=4)
    gt = match_ground_truth(manifest, sink_rows, required_fields=required[:3])
    if payload_ids and target.host and port is not None:
        proxy_manifest = make_tagged_interactions(run_id, count=len(payload_ids))
        for i, pid in enumerate(payload_ids):
            if i < len(proxy_manifest.events):
                proxy_manifest.events[i].tag = f"UHBS_INJECT:{run_id}"
                proxy_manifest.events[i].kind = pid
        gt = match_ground_truth(proxy_manifest, sink_rows, required_fields=required[:3])

    checks.append(
        CheckResult.make(
            id="c4.ground_truth_recall",
            team="blue",
            outcome=CheckOutcome.PASS if gt.recall >= 0.5 else CheckOutcome.FAIL,
            detail=gt.detail,
            score=100.0 * gt.recall,
            catalog_id="C4",
            evidence=[json.dumps(manifest.to_dict())[:800]],
        )
    )
    checks.append(
        CheckResult.make(
            id="c4.field_accuracy",
            team="blue",
            outcome=CheckOutcome.PASS if gt.field_accuracy >= 0.4 else CheckOutcome.FAIL,
            detail=f"field_accuracy={gt.field_accuracy}",
            score=100.0 * gt.field_accuracy,
            catalog_id="C4",
            mandatory=False,
        )
    )

    # C5 — ATT&CK only when claimed in telemetry text
    blob = json.dumps(sink_rows, default=str)
    claimed_ids = extract_technique_ids(blob)
    # Reject bare-word "attack" / "mitre" credit (v4 regression)
    if not claimed_ids:
        checks.append(
            CheckResult.make(
                id="c5.attack_mapping",
                team="blue",
                outcome=CheckOutcome.NOT_APPLICABLE,
                detail="no ATT&CK technique IDs claimed in telemetry",
                applicability_rationale="CTI mapping only evaluated when technique IDs are present",
                catalog_id="C5",
                mandatory=False,
            )
        )
    else:
        valid_n = 0
        details = []
        for tid in claimed_ids[:20]:
            rec = validate_technique_id(tid, mapping_basis="observed")
            if rec.valid:
                valid_n += 1
            details.append(f"{tid}:{rec.detail}")
        ratio_atk = valid_n / len(claimed_ids[:20])
        checks.append(
            CheckResult.make(
                id="c5.attack_mapping",
                team="blue",
                outcome=CheckOutcome.PASS if ratio_atk >= 0.9 else CheckOutcome.FAIL,
                detail=f"valid={valid_n}/{len(claimed_ids[:20])} ({'; '.join(details[:5])})",
                score=100.0 * ratio_atk,
                catalog_id="C5",
                mandatory=False,
                evidence=[f"bundle={validate_technique_id(claimed_ids[0]).bundle_version}"],
            )
        )

    agg = summarize_checks(checks)
    # Point-sum normalized among scored checks (equal weight via geometric mean)
    score = agg.score if agg.complete else 0.0
    status = "INCOMPLETE" if not agg.complete else pass_status(score)

    collection = {
        "recall": gt.recall,
        "observable_coverage": ratio,
        "duplicate_rate": gt.duplicate_rate,
        "declared_formats": declared,
        "status": "COMPLETE" if agg.complete else "INCOMPLETE",
    }

    return ModuleResult(
        module="C",
        dimension="telemetry",
        score=round(score, 2),
        status=status,
        checks=checks,
        notes=notes,
        complete=agg.complete,
        applicable_checks=agg.applicable,
        scored_checks=agg.scored,
        metrics={
            "ground_truth": {
                "recall": gt.recall,
                "field_accuracy": gt.field_accuracy,
                "duplicate_rate": gt.duplicate_rate,
                "matched": gt.matched,
                "expected": gt.expected,
            },
            "collection_capability": collection,
            "coverage": agg.coverage,
        },
    )


def main() -> int:
    p = argparse.ArgumentParser(description="UHBS Module C: Telemetry Assurance")
    p.add_argument("--target", default="")
    p.add_argument("--port", type=int, default=2222)
    p.add_argument("--user", default="root")
    p.add_argument("--password", default="root")
    p.add_argument("--telemetry-dir", default=None)
    args = p.parse_args()
    t = TargetSpec(
        name=args.target or "telemetry-only",
        kind="generic",
        host=args.target or None,
        port=args.port,
        user=args.user,
        password=args.password,
        telemetry_dir=args.telemetry_dir,
        protocol="ssh",
        protocols=["ssh"],
        ports_map={"ssh": args.port},
    )
    result = run(t)
    print(f"Module C telemetry score={result.score} status={result.status}")
    for c in result.checks:
        print(f"  [{c.team}] {c.id}: {c.outcome.value if c.outcome else c.passed} — {c.detail}")
    return 0 if result.status not in {"FAILED", "INCOMPLETE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
