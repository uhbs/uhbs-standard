#!/usr/bin/env bash
# Ensure private S3 bucket for lab raw retention (no public ACL).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

require_cmd aws
REGION="$(aws_region)"
BUCKET="$(s3_bucket)"

if aws s3api head-bucket --bucket "${BUCKET}" 2>/dev/null; then
  log "bucket exists: s3://${BUCKET}"
else
  log "creating s3://${BUCKET} in ${REGION}"
  if [[ "${REGION}" == "us-east-1" ]]; then
    aws s3api create-bucket --bucket "${BUCKET}" --region "${REGION}"
  else
    aws s3api create-bucket --bucket "${BUCKET}" --region "${REGION}" \
      --create-bucket-configuration "LocationConstraint=${REGION}"
  fi
fi

aws s3api put-public-access-block --bucket "${BUCKET}" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api put-bucket-encryption --bucket "${BUCKET}" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws s3api put-bucket-lifecycle-configuration --bucket "${BUCKET}" \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "retain-90d",
      "Status": "Enabled",
      "Filter": {"Prefix": "results-5.0.1/"},
      "Expiration": {"Days": 90}
    }]
  }' || log "lifecycle rule may already exist"

log "S3 raw ready: s3://${BUCKET}/results-5.0.1/"
