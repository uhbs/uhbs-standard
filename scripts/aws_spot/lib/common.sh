#!/usr/bin/env bash
# Shared helpers for UHBS 5.0.1 AWS Spot dual-vantage ops.
set -euo pipefail

# Cursor/sandbox local proxies break AWS SDK; prefer direct egress.
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy || true
export NO_PROXY="${NO_PROXY:-*}"
export no_proxy="${no_proxy:-*}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
AWS_SPOT_DIR="${ROOT}/scripts/aws_spot"
STATE_DIR="${ROOT}/.local/aws-spot"
WAVE_STATE="${STATE_DIR}/wave.state.json"
DB_DEFAULT="${ROOT}/.local/benchmark-refresh/results-5.0.1.sqlite3"
RESULTS_ROOT="${ROOT}/docs/conformance/latest/results-5.0.1"
S3_BUCKET_DEFAULT="uhbs-lab-raw-650825122703-us-east-1"
REGION_DEFAULT="us-east-1"
UHBS_VERSION="5.0.1"

mkdir -p "${STATE_DIR}"

die() { echo "ERROR: $*" >&2; exit 1; }
log() { echo "[aws_spot $(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" >&2; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

aws_region() {
  echo "${AWS_REGION:-${REGION_DEFAULT}}"
}

s3_bucket() {
  echo "${UHBS_S3_RAW_BUCKET:-${S3_BUCKET_DEFAULT}}"
}

read_state() {
  if [[ -f "${WAVE_STATE}" ]]; then
    cat "${WAVE_STATE}"
  else
    echo '{}'
  fi
}

write_state() {
  local tmp
  tmp="$(mktemp)"
  cat >"${tmp}"
  mv "${tmp}" "${WAVE_STATE}"
}

json_get() {
  # json_get <json-string> <python-expr-on-obj>
  python3 -c 'import json,sys; o=json.load(sys.stdin); print('"$2"')' <<<"$1"
}

operator_cidr() {
  if [[ -n "${UHBS_OPERATOR_CIDR:-}" ]]; then
    echo "${UHBS_OPERATOR_CIDR}"
    return
  fi
  local ip
  ip="$(curl -fsS --max-time 5 https://checkip.amazonaws.com 2>/dev/null | tr -d '[:space:]' || true)"
  if [[ -z "${ip}" ]]; then
    die "cannot detect operator IP; set UHBS_OPERATOR_CIDR=x.x.x.x/32"
  fi
  echo "${ip}/32"
}
