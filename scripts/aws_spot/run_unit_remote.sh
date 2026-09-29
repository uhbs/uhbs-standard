#!/usr/bin/env bash
# Run one unit (or repair stages) on Spot A/B with tracker claim/finish + S3 raw sync.
#
# Usage:
#   ./run_unit_remote.sh --unit-id HellPot-http [--mode both|quick|full]
#   ./run_unit_remote.sh --unit-id HellPot-http --force --mode full
#   ./run_unit_remote.sh --repair-missing
#   ./run_unit_remote.sh --phase s3 --unit-id HellPot-http
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

DB="${DB_DEFAULT}"
UNIT_ID=""
MODE="both"
FORCE=0
REPAIR=0
PHASE=""
AGENT="${UHBS_AGENT_ID:-spot-orchestrator}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db) DB="$2"; shift 2 ;;
    --unit-id) UNIT_ID="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --repair-missing) REPAIR=1; shift ;;
    --phase) PHASE="$2"; shift 2 ;;
    --agent) AGENT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0"; exit 0 ;;
    *) die "unknown arg: $1" ;;
  esac
done

require_cmd python3
require_cmd aws
STATE="$(read_state)"
KEY="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("key_path",""))' <<<"${STATE}" || true)"
TARGET_IP="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("public_ips",{}).get("target",""))' <<<"${STATE}" || true)"
PROBE_IP="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("public_ips",{}).get("probe",""))' <<<"${STATE}" || true)"
TARGET_PRIV="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("private_ips",{}).get("target",""))' <<<"${STATE}" || true)"
BUCKET="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("s3_bucket","'"$(s3_bucket)"'"))' <<<"${STATE}" || true)"

[[ -n "${KEY}" && -n "${TARGET_IP}" ]] || die "missing Spot state — run provision.sh"

ssh_t() { ssh -i "${KEY}" -o StrictHostKeyChecking=accept-new "ubuntu@${TARGET_IP}" "$@"; }
ssh_p() { ssh -i "${KEY}" -o StrictHostKeyChecking=accept-new "ubuntu@${PROBE_IP}" "$@"; }

claim_unit() {
  local uid="$1"
  if [[ "${FORCE}" -eq 1 ]]; then
    .venv/bin/python scripts/tracker.py --db "${DB}" claim-unit --unit-id "${uid}" --agent "${AGENT}" --force 2>/dev/null \
      || .venv/bin/python scripts/tracker.py --db "${DB}" claim-unit --unit-id "${uid}" --agent "${AGENT}"
  else
    .venv/bin/python scripts/tracker.py --db "${DB}" claim-unit --unit-id "${uid}" --agent "${AGENT}"
  fi
}

unit_row_json() {
  .venv/bin/python - <<PY
import json, sqlite3
conn = sqlite3.connect("${DB}")
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT * FROM benchmark_units WHERE unit_id=?", ("${UNIT_ID}",)).fetchone()
print(json.dumps(dict(row) if row else {}))
PY
}

s3_sync_raw() {
  local uid="$1" run_id="$2"
  local prefix="s3://${BUCKET}/results-5.0.1/${uid}/${run_id}/"
  log "s3 sync raw → ${prefix}"
  local tele_local="${ROOT}/.local/labs"
  if [[ -d "${tele_local}" ]]; then
    aws s3 sync "${tele_local}/" "${prefix}labs/" --region "$(aws_region)" --exclude "*" --include "*-telemetry/*" || true
  fi
  if [[ -n "${KEY}" && -n "${TARGET_IP}" ]]; then
    ssh_t "sudo tar -C /opt/uhbs/uhbs-standard/.local/labs -czf /tmp/uhbs-labs-tele.tgz . 2>/dev/null || true; sudo tar -C /telemetry -czf /tmp/uhbs-telemetry.tgz . 2>/dev/null || true" || true
    scp -i "${KEY}" -o StrictHostKeyChecking=accept-new \
      "ubuntu@${TARGET_IP}:/tmp/uhbs-labs-tele.tgz" "/tmp/${uid}-${run_id}-labs.tgz" 2>/dev/null || true
    scp -i "${KEY}" -o StrictHostKeyChecking=accept-new \
      "ubuntu@${TARGET_IP}:/tmp/uhbs-telemetry.tgz" "/tmp/${uid}-${run_id}-telemetry.tgz" 2>/dev/null || true
    [[ -f "/tmp/${uid}-${run_id}-labs.tgz" ]] && aws s3 cp "/tmp/${uid}-${run_id}-labs.tgz" "${prefix}labs.tgz" --region "$(aws_region)" || true
    [[ -f "/tmp/${uid}-${run_id}-telemetry.tgz" ]] && aws s3 cp "/tmp/${uid}-${run_id}-telemetry.tgz" "${prefix}telemetry.tgz" --region "$(aws_region)" || true
  fi
  # curated docs copy
  local latest
  latest="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("latest_path",""))' <<<"$(unit_row_json)")"
  if [[ -n "${latest}" && -d "${ROOT}/${latest}" ]]; then
    aws s3 sync "${ROOT}/${latest}/" "${prefix}docs/" --region "$(aws_region)" || true
  fi
  echo "${prefix}"
}

sync_db_to_target() {
  ssh_t "mkdir -p /opt/uhbs/uhbs-standard/.local/benchmark-refresh"
  scp -i "${KEY}" -o StrictHostKeyChecking=accept-new \
    "${DB}" "ubuntu@${TARGET_IP}:/opt/uhbs/uhbs-standard/.local/benchmark-refresh/results-5.0.1.sqlite3"
  rsync -az -e "ssh -i ${KEY} -o StrictHostKeyChecking=accept-new" \
    "${ROOT}/scripts/aws_spot/" "ubuntu@${TARGET_IP}:/opt/uhbs/uhbs-standard/scripts/aws_spot/"
}

pull_artifacts() {
  local latest="$1"
  mkdir -p "${ROOT}/${latest}"
  rsync -az -e "ssh -i ${KEY} -o StrictHostKeyChecking=accept-new" \
    "ubuntu@${TARGET_IP}:/opt/uhbs/uhbs-standard/${latest}/" "${ROOT}/${latest}/"
  # hub docs one level up when protocol nested
  local hub
  hub="$(dirname "${latest}")"
  if [[ "${hub}" != "." && "${hub}" != "docs/conformance/latest/results-5.0.1" ]]; then
    rsync -az -e "ssh -i ${KEY} -o StrictHostKeyChecking=accept-new" \
      --include 'index.md' --include 'TUTORIAL.md' --include 'METHODOLOGY.md' --exclude '*' \
      "ubuntu@${TARGET_IP}:/opt/uhbs/uhbs-standard/${hub}/" "${ROOT}/${hub}/" || true
  fi
}

run_remote_probe() {
  local uid="$1" port="$2" host_alias="$3"
  [[ -n "${PROBE_IP}" && -n "${TARGET_PRIV}" ]] || { log "skip remote probe"; return 0; }
  log "remote Module A/B smoke from ${PROBE_IP} → ${TARGET_PRIV}:${port}"
  ssh_p bash -s <<REMOTE || true
set -euo pipefail
# Network-facing reachability check (dual-vantage evidence). Full A/B remains in on-box report;
# this records remote vantage separately.
mkdir -p /tmp/uhbs-remote
{
  echo "target_priv=${TARGET_PRIV}"
  echo "port=${port}"
  echo "unit=${uid}"
  timeout 5 bash -c "echo >/dev/tcp/${TARGET_PRIV}/${port}" && echo REACHABLE=1 || echo REACHABLE=0
  docker run --rm --network host "uhbs:${UHBS_VERSION}" --version || true
} > "/tmp/uhbs-remote/${uid}.log" 2>&1
REMOTE
  scp -i "${KEY}" -o StrictHostKeyChecking=accept-new \
    "ubuntu@${PROBE_IP}:/tmp/uhbs-remote/${uid}.log" \
    "${ROOT}/.local/aws-spot/remote-${uid}.log" 2>/dev/null || true
}

stamp_vantage() {
  local latest="$1" mode="$2" raw_uri="$3" remote_ok="$4"
  python3 - <<PY
import json, pathlib, datetime
p = pathlib.Path("${ROOT}/${latest}/${mode}/run-meta.json")
meta = {}
if p.is_file():
    try: meta = json.loads(p.read_text())
    except Exception: meta = {}
meta["uhbs_version"] = "${UHBS_VERSION}"
meta["vantage_onbox"] = True
meta["vantage_remote"] = bool(int("${remote_ok}"))
meta["raw_s3_uri"] = "${raw_uri}"
meta["updated_at"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(meta, indent=2) + "\n")
PY
}

repair_missing() {
  log "repair-missing scan"
  .venv/bin/python - <<PY
import sqlite3, subprocess, sys
from pathlib import Path
root = Path("${ROOT}")
db = Path("${DB}")
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
rows = conn.execute(
  "SELECT unit_id FROM benchmark_units WHERE refreshability_status='refreshable' ORDER BY unit_id"
).fetchall()
for row in rows:
    uid = row["unit_id"]
    rc = subprocess.call(
        [str(root/".venv/bin/python"), "scripts/validate_unit.py", "--unit-id", uid, "--db", str(db)],
        cwd=str(root),
    )
    if rc != 0:
        print(f"REPAIR {uid}")
        subprocess.check_call(
            ["bash", "scripts/aws_spot/run_unit_remote.sh", "--unit-id", uid, "--force", "--mode", "both"],
            cwd=str(root),
        )
    else:
        print(f"ACCEPT {uid}")
PY
}

# --- main ---
cd "${ROOT}"

if [[ "${REPAIR}" -eq 1 ]]; then
  repair_missing
  exit 0
fi

[[ -n "${UNIT_ID}" ]] || die "--unit-id required (or --repair-missing)"

if [[ "${PHASE}" == "s3" ]]; then
  s3_sync_raw "${UNIT_ID}" "manual-$(date +%s)"
  exit 0
fi

if [[ "${PHASE}" == "validate" ]]; then
  .venv/bin/python scripts/validate_unit.py --unit-id "${UNIT_ID}" --db "${DB}"
  exit $?
fi

claim_unit "${UNIT_ID}" || log "claim soft-failed; continuing"
python3 - <<PY | write_state
import json, datetime
o=json.loads('''${STATE}''')
o["current_unit_id"]="${UNIT_ID}"
o["updated_at"]=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
print(json.dumps(o, indent=2))
PY

ROW="$(unit_row_json)"
LATEST="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["latest_path"])' <<<"${ROW}")"
PORT="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("target_port") or 0)' <<<"${ROW}")"
HOST_ALIAS="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("target_host") or "")' <<<"${ROW}")"
RECIPE_META="$(python3 -c 'import json,sys; sys.path.insert(0,"scripts/aws_spot"); from lab_recipes import recipe_for; r=recipe_for(sys.argv[1]) or {}; print(json.dumps(r))' "${UNIT_ID}")"

start_mode() {
  local m="$1"
  .venv/bin/python scripts/tracker.py --db "${DB}" log-run-start \
    --unit-id "${UNIT_ID}" --mode "${m}" --uhbs-version "${UHBS_VERSION}" \
    --grader-image "uhbs:${UHBS_VERSION}$([[ ${m} == full ]] && echo -full || true)" \
    --target-image "$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("image",""))' <<<"${RECIPE_META}")" \
    --base-image "$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("base_image",""))' <<<"${RECIPE_META}")" \
    --base-image-reason "$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("base_image_reason",""))' <<<"${RECIPE_META}")" \
    --strategy "$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("strategy",""))' <<<"${RECIPE_META}")" \
    --telemetry-mode mounted --airgap-attested --notes "spot dual-vantage ${m}" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin).get("run_id",""))'
}

RUN_ID=""
case "${MODE}" in
  quick) RUN_ID="$(start_mode quick)" ;;
  full) RUN_ID="$(start_mode full)" ;;
  both)
    start_mode quick >/dev/null
    RUN_ID="$(start_mode full)"
    ;;
esac
[[ -n "${RUN_ID}" ]] || RUN_ID="$(uuidgen | tr '[:upper:]' '[:lower:]')"

log "sync db + grade scripts → ${TARGET_IP}"
sync_db_to_target

log "on-box grade ${UNIT_ID} mode=${MODE}"
ssh_t bash -s <<REMOTE
set -euo pipefail
cd /opt/uhbs/uhbs-standard
export UHBS_ROOT=/opt/uhbs/uhbs-standard
python3 scripts/aws_spot/grade_unit.py --unit-id "${UNIT_ID}" --mode "${MODE}" \
  --db .local/benchmark-refresh/results-5.0.1.sqlite3
REMOTE

pull_artifacts "${LATEST}"

# Remote vantage smoke
REMOTE_OK=0
if run_remote_probe "${UNIT_ID}" "${PORT}" "${HOST_ALIAS}"; then
  if [[ -f "${ROOT}/.local/aws-spot/remote-${UNIT_ID}.log" ]] && grep -q 'REACHABLE=1' "${ROOT}/.local/aws-spot/remote-${UNIT_ID}.log"; then
    REMOTE_OK=1
  fi
fi

RAW_URI="$(s3_sync_raw "${UNIT_ID}" "${RUN_ID}" | tail -n1)"
case "${MODE}" in
  quick) stamp_vantage "${LATEST}" quick "${RAW_URI}" "${REMOTE_OK}" ;;
  full) stamp_vantage "${LATEST}" full "${RAW_URI}" "${REMOTE_OK}" ;;
  both)
    stamp_vantage "${LATEST}" quick "${RAW_URI}" "${REMOTE_OK}"
    stamp_vantage "${LATEST}" full "${RAW_URI}" "${REMOTE_OK}"
    ;;
esac

UPSTREAM_SHA="$(python3 -c 'import json,pathlib; p=pathlib.Path("'"${LATEST}"'/full/run-meta.json");
p=p if p.is_file() else pathlib.Path("'"${LATEST}"'/quick/run-meta.json");
print(json.loads(p.read_text()).get("upstream_commit","") if p.is_file() else "")')"
STRAT="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("strategy",""))' <<<"${RECIPE_META}")"
BASE_IMG="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("base_image",""))' <<<"${RECIPE_META}")"
BASE_REASON="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("base_image_reason",""))' <<<"${RECIPE_META}")"
REPO="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("repo",""))' <<<"${RECIPE_META}")"

.venv/bin/python scripts/tracker.py --db "${DB}" set-unit-meta \
  --unit-id "${UNIT_ID}" \
  --upstream-repo "${REPO}" \
  --upstream-branch main \
  --upstream-commit "${UPSTREAM_SHA}" \
  --base-image "${BASE_IMG}" \
  --base-image-reason "${BASE_REASON}" \
  --strategy "${STRAT}" || true

# Finish tracker rows
if [[ "${MODE}" == "quick" || "${MODE}" == "both" ]]; then
  .venv/bin/python scripts/tracker.py --db "${DB}" log-run-finish \
    --unit-id "${UNIT_ID}" --mode quick --out-dir "${LATEST}/quick" --status succeeded || true
fi
if [[ "${MODE}" == "full" || "${MODE}" == "both" ]]; then
  .venv/bin/python scripts/tracker.py --db "${DB}" log-run-finish \
    --unit-id "${UNIT_ID}" --mode full --out-dir "${LATEST}/full" \
    --cast-path "${LATEST}/full/proof/full-run.cast" --status succeeded || true
fi

# Cleanup target container on Spot A
ssh_t "docker ps -q --filter label=uhbs.unit=${UNIT_ID} | xargs -r docker rm -f; docker ps -aq --filter name=${HOST_ALIAS} | xargs -r docker rm -f" || true

.venv/bin/python scripts/validate_unit.py --unit-id "${UNIT_ID}" --db "${DB}" || {
  log "validate_unit REJECT for ${UNIT_ID}"
  exit 1
}
log "ACCEPT ${UNIT_ID}"
