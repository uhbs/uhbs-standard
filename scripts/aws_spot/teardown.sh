#!/usr/bin/env bash
# Cancel Spot requests / terminate instances / leave S3 raw intact.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

require_cmd aws
STATE="$(read_state)"
REGION="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("region","'"$(aws_region)"'"))' <<<"${STATE}")"

IIDS="$(python3 - <<'PY' <<<"${STATE}"
import json,sys
o=json.load(sys.stdin)
ids=list((o.get("instance_ids") or {}).values())
print(" ".join(i for i in ids if i))
PY
)"
SIRS="$(python3 - <<'PY' <<<"${STATE}"
import json,sys
o=json.load(sys.stdin)
ids=list((o.get("spot_ids") or {}).values())
print(" ".join(i for i in ids if i))
PY
)"

if [[ -n "${SIRS}" ]]; then
  log "cancel spot requests: ${SIRS}"
  # shellcheck disable=SC2086
  aws ec2 cancel-spot-instance-requests --region "${REGION}" --spot-instance-request-ids ${SIRS} || true
fi
if [[ -n "${IIDS}" ]]; then
  log "terminate instances: ${IIDS}"
  # shellcheck disable=SC2086
  aws ec2 terminate-instances --region "${REGION}" --instance-ids ${IIDS} || true
fi

log "teardown done (S3 raw bucket $(s3_bucket) retained; SQLite done flags retained)"
python3 - <<PY | write_state
import json, datetime
o=json.loads('''${STATE}''')
o["paused"]=True
o["teardown_at"]=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
o["instance_ids"]={}
o["public_ips"]={}
print(json.dumps(o, indent=2))
PY
