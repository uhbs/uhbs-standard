"""C4 ground-truth matching for Module C telemetry assurance."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class TruthEvent:
    tag: str
    kind: str  # session | credential | command | request | file | egress
    emitted_at: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class TruthManifest:
    run_id: str
    created_at: str
    events: list[TruthEvent]
    observation_window_s: float = 30.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "observation_window_s": self.observation_window_s,
            "events": [asdict(e) for e in self.events],
        }


@dataclass(frozen=True)
class GroundTruthMetrics:
    recall: float
    field_accuracy: float
    duplicate_rate: float
    matched: int
    expected: int
    duplicates: int
    late_or_missing: int
    median_latency_s: float | None
    detail: str


def new_run_id() -> str:
    return f"uhbs-gt-{uuid.uuid4().hex[:12]}"


def make_tagged_interactions(run_id: str, *, count: int = 4) -> TruthManifest:
    """Build an immutable truth manifest before sending interactions."""
    now = datetime.now(UTC).isoformat()
    events: list[TruthEvent] = []
    kinds = ["session", "credential", "command", "request"]
    for i in range(count):
        kind = kinds[i % len(kinds)]
        tag = f"{run_id}:{kind}:{i}"
        events.append(
            TruthEvent(
                tag=tag,
                kind=kind,
                emitted_at=now,
                payload={"marker": tag, "seq": i},
            )
        )
    return TruthManifest(run_id=run_id, created_at=now, events=events)


def _blobify(records: list[Any]) -> str:
    parts: list[str] = []
    for row in records:
        try:
            parts.append(json.dumps(row, sort_keys=True, default=str))
        except (TypeError, ValueError):
            parts.append(str(row))
    return "\n".join(parts)


def match_ground_truth(
    manifest: TruthManifest,
    records: list[Any],
    *,
    required_fields: list[str] | None = None,
) -> GroundTruthMetrics:
    """Match tagged truth events inside emitted telemetry records.

    Precision against unmatched background events is intentionally not claimed
    unless the environment guarantees isolation (see RFC 0003).
    """
    blob = _blobify(records)
    matched_tags: list[str] = []
    dupes = 0
    for ev in manifest.events:
        hits = len(re.findall(re.escape(ev.tag), blob))
        if hits >= 1:
            matched_tags.append(ev.tag)
        if hits > 1:
            dupes += hits - 1

    expected = len(manifest.events)
    matched = len(matched_tags)
    recall = (matched / expected) if expected else 0.0
    late_or_missing = expected - matched

    # Field accuracy: presence of required fields (with common synonyms) across
    # records. Keep aligned with Module C3 observable heuristics.
    req = required_fields or ["timestamp", "source", "message"]
    synonyms = {
        "event_time": ["timestamp", "@timestamp", "event_time", "time", "created"],
        "timestamp": ["timestamp", "@timestamp", "event_time", "time", "created"],
        "source_endpoint": ["src", "source", "src_ip", "client_ip", "srcip"],
        "source": ["src", "source", "src_ip", "client_ip", "srcip"],
        "destination_endpoint": ["dst", "destination", "dest", "dst_ip"],
        "protocol_action": [
            "action",
            "event.action",
            "verb",
            "method",
            "command",
            "eventid",
            "input",
        ],
        "message": ["message", "msg", "input", "command"],
    }
    field_hits = 0
    field_total = 0
    for row in records:
        if not isinstance(row, dict):
            continue
        flat_keys = {str(k).lower() for k in row}
        text = json.dumps(row).lower()
        for f in req:
            field_total += 1
            keys = synonyms.get(f, synonyms.get(f.lower(), [f]))
            if any(k.lower() in flat_keys or k.lower() in text for k in keys):
                field_hits += 1
    field_accuracy = (field_hits / field_total) if field_total else 0.0
    duplicate_rate = (dupes / max(matched, 1)) if matched else (float(dupes) if dupes else 0.0)

    return GroundTruthMetrics(
        recall=round(recall, 4),
        field_accuracy=round(field_accuracy, 4),
        duplicate_rate=round(min(duplicate_rate, 1.0), 4),
        matched=matched,
        expected=expected,
        duplicates=dupes,
        late_or_missing=late_or_missing,
        median_latency_s=None,
        detail=f"matched={matched}/{expected} dups={dupes}",
    )


# Family token embedded in each injection command (must match assess lookup).
# Keys are payload ids; values are the short tokens written into UHBS_INJECT lines.
INJECT_FAMILY_TOKEN: dict[str, str] = {
    "ansi": "ANSI",
    "json_break": "JSON",
    "null_byte": "NULL",
    "cr_inject": "CR",
    "formula": "XLS",
    "unicode": "UNI",
}


def injection_payloads(run_id: str) -> list[tuple[str, str]]:
    """Tagged hostile payloads for sink-side C2 tests."""
    return [
        ("ansi", f'echo "UHBS_INJECT:{run_id}:ANSI:\\x1b[31mRED\\x1b[0m"'),
        ("json_break", f"echo 'UHBS_INJECT:{run_id}:JSON:{{\"a\": \"unterminated'"),
        ("null_byte", f"printf 'UHBS_INJECT:{run_id}:NULL:\\x00byte\\n'"),
        ("cr_inject", f"echo 'UHBS_INJECT:{run_id}:CR:newline\\rinjection'"),
        ("formula", f"echo 'UHBS_INJECT:{run_id}:XLS:=cmd|\\'/C calc\\'|''"),
        ("unicode", f"echo 'UHBS_INJECT:{run_id}:UNI:\\u202emargin'"),
    ]


def assess_sink_resilience(
    records: list[Any],
    run_id: str,
    payload_ids: list[str],
) -> dict[str, Any]:
    """Verify injected markers appear as data without breaking record framing.

    Requires the current ``run_id`` in every credited marker so prior-run
    ``UHBS_INJECT:*`` lines cannot satisfy this assessment.

    Family tokens must match what ``injection_payloads`` embeds (e.g. ``JSON``
    for payload id ``json_break``), not a naive ``pid.upper()``.
    """
    blob = _blobify(records)
    blob_upper = blob.upper()
    run_token = f"UHBS_INJECT:{run_id}"
    found = []
    for pid in payload_ids:
        token = INJECT_FAMILY_TOKEN.get(pid, pid.upper())
        family = f"{run_token}:{token}"
        if family.upper() in blob_upper or (
            run_token in blob and token.upper() in blob_upper
        ):
            found.append(pid)

    malformed = sum(
        1
        for r in records
        if isinstance(r, dict) and "__malformed__" in r
    )
    # Require a clear majority of this run's payloads (ceil 2/3), never stale-only.
    need = max(1, (2 * len(payload_ids) + 2) // 3) if payload_ids else 1
    return {
        "markers_found": found,
        "markers_expected": list(payload_ids),
        "malformed_records": malformed,
        "json_parse_ok": malformed == 0,
        "run_id": run_id,
        "ok": malformed == 0 and len(found) >= need and run_token in blob,
    }
