#!/usr/bin/env bash
# Wave orchestrator: claim-next loop with pause/resume against results-5.0.1.sqlite3.
#
#   ./run_wave.sh                 # start / continue
#   ./run_wave.sh --pause
#   ./run_wave.sh --resume
#   ./run_wave.sh --repair-missing
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

DB="${DB_DEFAULT}"
AGENT="${UHBS_AGENT_ID:-spot-wave}"
ACTION="run"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db) DB="$2"; shift 2 ;;
    --pause) ACTION="pause"; shift ;;
    --resume) ACTION="resume"; shift ;;
    --repair-missing) ACTION="repair"; shift ;;
    --agent) AGENT="$2"; shift 2 ;;
    *) die "unknown arg: $1" ;;
  esac
done

cd "${ROOT}"
STATE="$(read_state)"

case "${ACTION}" in
  pause)
    python3 - <<PY | write_state
import json, datetime
o=json.loads('''${STATE}''')
o["paused"]=True
o["updated_at"]=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
print(json.dumps(o, indent=2))
PY
    # Mirror pause flag to S3 when configured
    if aws s3 ls "s3://$(s3_bucket)/results-5.0.1/_wave/" >/dev/null 2>&1; then
      aws s3 cp "${WAVE_STATE}" "s3://$(s3_bucket)/results-5.0.1/_wave/wave.state.json" || true
    fi
    log "wave paused"
    exit 0
    ;;
  resume)
    python3 - <<PY | write_state
import json, datetime
o=json.loads('''${STATE}''')
o["paused"]=False
o["updated_at"]=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
print(json.dumps(o, indent=2))
PY
    log "wave resume — continuing claim loop"
    ;;
  repair)
    exec bash "${SCRIPT_DIR}/run_unit_remote.sh" --db "${DB}" --repair-missing
    ;;
esac

paused="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("paused", False))' <<<"$(read_state)")"
if [[ "${paused}" == "True" ]]; then
  die "wave is paused; run with --resume"
fi

log "wave start db=${DB} agent=${AGENT}"
while true; do
  paused="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("paused", False))' <<<"$(read_state)")"
  if [[ "${paused}" == "True" ]]; then
    log "pause observed — exiting claim loop"
    break
  fi
  out="$(.venv/bin/python scripts/tracker.py --db "${DB}" claim-next --agent "${AGENT}" || true)"
  uid="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("unit_id") or "")' <<<"${out}")"
  if [[ -z "${uid}" || "${uid}" == "None" ]]; then
    log "no more claimable units — wave idle"
    break
  fi
  log "claimed ${uid}"
  if ! bash "${SCRIPT_DIR}/run_unit_remote.sh" --db "${DB}" --unit-id "${uid}" --mode both --agent "${AGENT}"; then
    .venv/bin/python scripts/tracker.py --db "${DB}" log-blocker \
      --unit-id "${uid}" --blocker-type grade-fail --stage wave --summary "validate_unit or grade failed" || true
    log "blocker recorded for ${uid}; continuing"
  fi
  .venv/bin/python scripts/tracker.py --db "${DB}" sync-ledger || true
done

# Regenerate always-grade summary stub
python3 - <<'PY'
from pathlib import Path
import sqlite3
root = Path("docs/conformance/latest/results-5.0.1")
db = Path(".local/benchmark-refresh/results-5.0.1.sqlite3")
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
rows = conn.execute(
    """
    SELECT u.unit_id, r.uhqs, r.grade, r.run_status
    FROM benchmark_units u
    LEFT JOIN run_executions r ON r.unit_id=u.unit_id AND r.run_mode='full'
    WHERE u.refreshability_status='refreshable'
    ORDER BY u.unit_id
    """
).fetchall()
lines = ["# ALWAYS-GRADE / REGRADE — results-5.0.1", "", "| Unit | UHQS | Grade | Status |", "| --- | --- | --- | --- |"]
for r in rows:
    lines.append(f"| {r['unit_id']} | {r['uhqs'] if r['uhqs'] is not None else ''} | {r['grade'] or ''} | {r['run_status'] or 'pending'} |")
(root / "ALWAYS-GRADE-REGRADE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote ALWAYS-GRADE-REGRADE.md", len(rows))
PY

log "wave loop finished"
