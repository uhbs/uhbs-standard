#!/usr/bin/env bash
# Grade all Spot recipes on the local Docker host (no AWS).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"
DB="${UHBS_DB:-${ROOT}/.local/benchmark-refresh/results-5.0.1.sqlite3}"
MODE="${UHBS_GRADE_MODE:-both}"
export UHBS_LOCAL_DOCKER="${UHBS_LOCAL_DOCKER:-1}"
LOG_DIR="${ROOT}/.local/benchmark-refresh/local-wave"
mkdir -p "${LOG_DIR}"
WAVE_LOG="${LOG_DIR}/wave-$(date -u +%Y%m%dT%H%M%SZ).log"
LEDGER="${LOG_DIR}/ledger.tsv"
# Append across restarts (header once).
if [[ ! -f "${LEDGER}" ]]; then
  echo "unit_id	mode	ok	uhqs	verdict	module_d	started	finished	note" >"${LEDGER}"
fi

UNITS=()
if [[ -n "${UHBS_GRADE_LIST:-}" && -f "${UHBS_GRADE_LIST}" ]]; then
  while IFS= read -r _uid; do
    [[ -n "${_uid}" && "${_uid}" != \#* ]] && UNITS+=("${_uid}")
  done < "${UHBS_GRADE_LIST}"
else
  while IFS= read -r _uid; do
    [[ -n "${_uid}" ]] && UNITS+=("${_uid}")
  done < <(
    python3 - <<'PY'
import sqlite3, sys
from pathlib import Path
sys.path.insert(0, "scripts/aws_spot")
from lab_recipes import RECIPES
db = Path(".local/benchmark-refresh/results-5.0.1.sqlite3")
conn = sqlite3.connect(db)
ids = [r[0] for r in conn.execute("SELECT unit_id FROM benchmark_units ORDER BY unit_id")]
conn.close()
for uid in ids:
    if uid in RECIPES:
        print(uid)
PY
  )
fi


ONLY="${UHBS_ONLY:-}"
SKIP_DONE="${UHBS_SKIP_DONE:-1}"

log() { echo "[local-wave $(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${WAVE_LOG}"; }

log "start units=${#UNITS[@]} mode=${MODE} skip_done=${SKIP_DONE} log=${WAVE_LOG}"

for uid in "${UNITS[@]}"; do
  if [[ -n "${ONLY}" && "${uid}" != "${ONLY}" ]]; then
    continue
  fi
  if [[ "${SKIP_DONE}" == "1" ]]; then
    meta="$(python3 - <<PY
import json, sqlite3
from pathlib import Path
conn = sqlite3.connect("${DB}")
row = conn.execute("SELECT latest_path FROM benchmark_units WHERE unit_id=?", ("${uid}",)).fetchone()
conn.close()
if not row:
    print("")
else:
    p = Path(row[0]) / "full" / "run-meta.json"
    if p.is_file():
        try:
            m = json.loads(p.read_text())
            print("1" if m.get("module_d_inspect_sha256") else "0")
        except Exception:
            print("0")
    else:
        print("0")
PY
)"
    if [[ "${meta}" == "1" ]]; then
      log "SKIP ${uid} (already has Module D digests on full)"
      continue
    fi
  fi

  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  log "GRADE ${uid} mode=${MODE}"
  unit_log="${LOG_DIR}/${uid}.log"
  set +e
  python3 scripts/aws_spot/grade_unit.py --unit-id "${uid}" --mode "${MODE}" --db "${DB}" \
    >"${unit_log}" 2>&1
  rc=$?
  set -e
  finished="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # stop leftover target container from recipe if still running
  cname="$(python3 -c 'import sys; sys.path.insert(0,"scripts/aws_spot"); from lab_recipes import recipe_for; r=recipe_for(sys.argv[1]) or {}; print(r.get("container") or "")' "${uid}")"
  if [[ -n "${cname}" ]]; then
    docker rm -f "${cname}" >/dev/null 2>&1 || true
  fi

  summary="$(python3 - <<PY
import json, sqlite3
from pathlib import Path
uid = "${uid}"
conn = sqlite3.connect("${DB}")
row = conn.execute("SELECT latest_path FROM benchmark_units WHERE unit_id=?", (uid,)).fetchone()
conn.close()
uhqs = verdict = md = ""
note = "rc=${rc}"
if row:
    # prefer full, else quick
    for mode in ("full", "quick"):
        rp = Path(row[0]) / mode / "report.json"
        if not rp.is_file():
            continue
        try:
            r = json.loads(rp.read_text())
        except Exception as e:
            note = f"bad report {mode}: {e}"
            continue
        u = r.get("uhqs") if isinstance(r.get("uhqs"), dict) else {}
        uhqs = u.get("uhqs", r.get("uhqs"))
        verdict = u.get("critical_control_verdict") or r.get("critical_control_verdict")
        mods = r.get("modules")
        d = None
        if isinstance(mods, dict):
            d = mods.get("D")
        elif isinstance(mods, list):
            d = next((m for m in mods if m.get("module") == "D"), None)
        if d:
            md = d.get("score")
        note = mode
        break
print(f"{uhqs}\t{verdict}\t{md}\t{note}")
PY
)"
  IFS=$'\t' read -r uhqs verdict md note <<<"${summary}"
  ok="0"
  [[ "${rc}" -eq 0 ]] && ok="1"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "${uid}" "${MODE}" "${ok}" "${uhqs}" "${verdict}" "${md}" "${started}" "${finished}" "${note}" \
    >>"${LEDGER}"
  log "DONE ${uid} ok=${ok} uhqs=${uhqs} verdict=${verdict} D=${md} (${note})"
done

log "wave complete ledger=${LEDGER}"
