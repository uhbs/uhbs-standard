#!/usr/bin/env bash
# Rsync v5.0.1 tree to Spot A (target) and Spot B (probe); build uhbs:5.0.1 (+full on A).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

require_cmd rsync
require_cmd ssh
STATE="$(read_state)"
[[ "$(python3 -c 'import json,sys; print(bool(json.load(sys.stdin).get("public_ips")))' <<<"${STATE}")" == "True" ]] \
  || die "wave.state.json missing public_ips — run provision.sh first"

KEY="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["key_path"])' <<<"${STATE}")"
TARGET_IP="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["public_ips"]["target"])' <<<"${STATE}")"
PROBE_IP="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["public_ips"]["probe"])' <<<"${STATE}")"

remote() {
  local host="$1"
  shift
  ssh -i "${KEY}" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20 "ubuntu@${host}" "$@"
}

sync_one() {
  local host="$1"
  local build_full="${2:-0}"
  log "prepare ${host}"
  for _ in $(seq 1 60); do
    if remote "${host}" "sudo mkdir -p /opt/uhbs/uhbs-standard /telemetry && sudo chown -R ubuntu:ubuntu /opt/uhbs /telemetry"; then
      break
    fi
    sleep 5
  done
  log "rsync → ${host}"
  rsync -az --delete \
    --exclude '.venv/' --exclude 'node_modules/' --exclude '.git/' \
    --exclude '.local/labs/' --exclude '__pycache__/' \
    --exclude '.local/aws-spot/keys/' \
    -e "ssh -i ${KEY} -o StrictHostKeyChecking=accept-new" \
    "${ROOT}/" "ubuntu@${host}:/opt/uhbs/uhbs-standard/"
  # SQLite + recipes helpers (small)
  rsync -az -e "ssh -i ${KEY} -o StrictHostKeyChecking=accept-new" \
    "${ROOT}/.local/benchmark-refresh/" "ubuntu@${host}:/opt/uhbs/uhbs-standard/.local/benchmark-refresh/" \
    2>/dev/null || true
  log "docker build uhbs:${UHBS_VERSION} on ${host}"
  remote "${host}" bash -s <<REMOTE
set -euo pipefail
cd /opt/uhbs/uhbs-standard
sudo docker build -t uhbs:${UHBS_VERSION} .
if [[ "${build_full}" == "1" ]]; then
  sudo docker build -f Dockerfile.full -t uhbs:${UHBS_VERSION}-full .
fi
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq asciinema git curl ca-certificates >/dev/null || true
sudo chmod 777 /telemetry
docker network create uhbs-lab 2>/dev/null || true
REMOTE
}

sync_one "${TARGET_IP}" 1
sync_one "${PROBE_IP}" 0
log "sync complete"
