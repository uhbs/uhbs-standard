#!/usr/bin/env bash
# Provision Spot A (target) + Spot B (probe) in us-east-1 for UHBS 5.0.1.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

require_cmd aws
require_cmd jq
require_cmd python3

REGION="$(aws_region)"
NAME_PREFIX="${UHBS_SPOT_PREFIX:-uhbs-501}"
INSTANCE_TYPE="${UHBS_SPOT_TYPE:-c6i.xlarge}"
KEY_NAME="${UHBS_KEY_NAME:-${NAME_PREFIX}-key}"
OPERATOR_CIDR="$(operator_cidr)"
AMI_ID="${UHBS_AMI_ID:-}"

if [[ -z "${AMI_ID}" ]]; then
  AMI_ID="$(aws ec2 describe-images --region "${REGION}" --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd*/ubuntu-noble-24.04-amd64-server-*" \
              "Name=state,Values=available" \
    --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)"
fi
[[ "${AMI_ID}" != "None" && -n "${AMI_ID}" ]] || die "could not resolve Ubuntu 24.04 AMI"

log "region=${REGION} ami=${AMI_ID} operator=${OPERATOR_CIDR} type=${INSTANCE_TYPE}"

# Key pair
if ! aws ec2 describe-key-pairs --region "${REGION}" --key-names "${KEY_NAME}" >/dev/null 2>&1; then
  mkdir -p "${STATE_DIR}/keys"
  aws ec2 create-key-pair --region "${REGION}" --key-name "${KEY_NAME}" \
    --query 'KeyMaterial' --output text >"${STATE_DIR}/keys/${KEY_NAME}.pem"
  chmod 600 "${STATE_DIR}/keys/${KEY_NAME}.pem"
  log "created key pair ${KEY_NAME}"
fi

# Security groups
VPC_ID="$(aws ec2 describe-vpcs --region "${REGION}" --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text)"
[[ -n "${VPC_ID}" && "${VPC_ID}" != "None" ]] || die "no default VPC"

SG_PROBE_NAME="${NAME_PREFIX}-probe-sg"
SG_TARGET_NAME="${NAME_PREFIX}-target-sg"

ensure_sg() {
  local name="$1" desc="$2"
  local id
  id="$(aws ec2 describe-security-groups --region "${REGION}" \
    --filters "Name=group-name,Values=${name}" "Name=vpc-id,Values=${VPC_ID}" \
    --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)"
  if [[ -z "${id}" || "${id}" == "None" ]]; then
    id="$(aws ec2 create-security-group --region "${REGION}" --group-name "${name}" \
      --description "${desc}" --vpc-id "${VPC_ID}" --query GroupId --output text)"
  fi
  echo "${id}"
}

SG_PROBE="$(ensure_sg "${SG_PROBE_NAME}" "UHBS 5.0.1 probe host")"
SG_TARGET="$(ensure_sg "${SG_TARGET_NAME}" "UHBS 5.0.1 target host")"

# Operator SSH to both
for sg in "${SG_PROBE}" "${SG_TARGET}"; do
  aws ec2 authorize-security-group-ingress --region "${REGION}" --group-id "${sg}" \
    --protocol tcp --port 22 --cidr "${OPERATOR_CIDR}" 2>/dev/null || true
done
# Probe can SSH to target (optional) and open honeypot ports from probe SG only
aws ec2 authorize-security-group-ingress --region "${REGION}" --group-id "${SG_TARGET}" \
  --protocol tcp --port 22 --source-group "${SG_PROBE}" 2>/dev/null || true
# Broad lab listener range only from probe SG (not 0.0.0.0/0)
aws ec2 authorize-security-group-ingress --region "${REGION}" --group-id "${SG_TARGET}" \
  --ip-permissions "IpProtocol=tcp,FromPort=1,ToPort=65535,UserIdGroupPairs=[{GroupId=${SG_PROBE}}]" \
  2>/dev/null || true
aws ec2 authorize-security-group-ingress --region "${REGION}" --group-id "${SG_TARGET}" \
  --ip-permissions "IpProtocol=udp,FromPort=1,ToPort=65535,UserIdGroupPairs=[{GroupId=${SG_PROBE}}]" \
  2>/dev/null || true

USERDATA_B64="$(base64 <"${SCRIPT_DIR}/userdata-docker.sh" | tr -d '\n')"

request_spot() {
  local role="$1" sg="$2"
  local spec
  spec="$(python3 - <<PY
import json
print(json.dumps({
  "ImageId": "${AMI_ID}",
  "InstanceType": "${INSTANCE_TYPE}",
  "KeyName": "${KEY_NAME}",
  "SecurityGroupIds": ["${sg}"],
  "UserData": "${USERDATA_B64}",
}))
PY
)"
  aws ec2 request-spot-instances --region "${REGION}" \
    --instance-count 1 \
    --type one-time \
    --launch-specification "${spec}" \
    --query 'SpotInstanceRequests[0].SpotInstanceRequestId' --output text
}

SIR_TARGET="$(request_spot target "${SG_TARGET}")"
SIR_PROBE="$(request_spot probe "${SG_PROBE}")"
log "spot requests target=${SIR_TARGET} probe=${SIR_PROBE}"

wait_instance() {
  local sir="$1"
  local iid=""
  for _ in $(seq 1 60); do
    iid="$(aws ec2 describe-spot-instance-requests --region "${REGION}" \
      --spot-instance-request-ids "${sir}" \
      --query 'SpotInstanceRequests[0].InstanceId' --output text)"
    if [[ -n "${iid}" && "${iid}" != "None" ]]; then
      echo "${iid}"
      return 0
    fi
    sleep 5
  done
  die "timed out waiting for spot ${sir}"
}

IID_TARGET="$(wait_instance "${SIR_TARGET}")"
IID_PROBE="$(wait_instance "${SIR_PROBE}")"
aws ec2 wait instance-running --region "${REGION}" --instance-ids "${IID_TARGET}" "${IID_PROBE}"

aws ec2 create-tags --region "${REGION}" --resources "${IID_TARGET}" \
  --tags "Key=Name,Value=${NAME_PREFIX}-target" "Key=uhbs,Value=5.0.1" "Key=uhbs-role,Value=target" || true
aws ec2 create-tags --region "${REGION}" --resources "${IID_PROBE}" \
  --tags "Key=Name,Value=${NAME_PREFIX}-probe" "Key=uhbs,Value=5.0.1" "Key=uhbs-role,Value=probe" || true

pub() {
  aws ec2 describe-instances --region "${REGION}" --instance-ids "$1" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
}
PRIV() {
  aws ec2 describe-instances --region "${REGION}" --instance-ids "$1" \
    --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text
}

TARGET_IP="$(pub "${IID_TARGET}")"
PROBE_IP="$(pub "${IID_PROBE}")"
TARGET_PRIV="$(PRIV "${IID_TARGET}")"
PROBE_PRIV="$(PRIV "${IID_PROBE}")"

python3 - <<PY | write_state
import json, datetime
print(json.dumps({
  "paused": False,
  "current_unit_id": None,
  "updated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
  "region": "${REGION}",
  "key_name": "${KEY_NAME}",
  "key_path": "${STATE_DIR}/keys/${KEY_NAME}.pem",
  "sg_target": "${SG_TARGET}",
  "sg_probe": "${SG_PROBE}",
  "spot_ids": {"target": "${SIR_TARGET}", "probe": "${SIR_PROBE}"},
  "instance_ids": {"target": "${IID_TARGET}", "probe": "${IID_PROBE}"},
  "public_ips": {"target": "${TARGET_IP}", "probe": "${PROBE_IP}"},
  "private_ips": {"target": "${TARGET_PRIV}", "probe": "${PROBE_PRIV}"},
  "s3_bucket": "$(s3_bucket)",
}, indent=2))
PY

log "provisioned target=${TARGET_IP} probe=${PROBE_IP}"
log "state written to ${WAVE_STATE}"
cat "${WAVE_STATE}"
