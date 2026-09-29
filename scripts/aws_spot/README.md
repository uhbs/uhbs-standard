# AWS Spot dual-vantage ops (UHBS 5.0.1)

Operator laptop orchestrates via SSH. Do **not** expose these scripts via MCP.

## Prereqs

- AWS CLI configured (`us-east-1`), IAM able to request Spot + manage S3
- Repo on branch `v5.0.1`, SQLite `.local/benchmark-refresh/results-5.0.1.sqlite3` imported

## Flow

```bash
# 1) Raw evidence bucket
./scripts/aws_spot/ensure_s3_bucket.sh

# 2) Spot A (target) + Spot B (probe)
./scripts/aws_spot/provision.sh
./scripts/aws_spot/sync_repo.sh

# 3) Pilot
./scripts/aws_spot/run_unit_remote.sh --unit-id HellPot-http --mode both
./scripts/aws_spot/run_wave.sh --pause
./scripts/aws_spot/run_wave.sh --resume
./scripts/aws_spot/run_unit_remote.sh --repair-missing

# 4) Full wave
./scripts/aws_spot/run_wave.sh

# 5) Teardown Spot only (S3 raw retained)
./scripts/aws_spot/teardown.sh
```

State file: `.local/aws-spot/wave.state.json` (mirrored under `s3://…/results-5.0.1/_wave/` when pause runs).

Security groups: SSH from operator CIDR only; honeypot ports only from probe SG.
