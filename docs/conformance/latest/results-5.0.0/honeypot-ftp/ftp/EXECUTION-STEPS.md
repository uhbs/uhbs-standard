# Execution steps — `honeypot-ftp-ftp`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `honeypot-ftp-ftp`
- benchmark: `honeypot-ftp` · protocol: `ftp` · class: `Low-Interaction`
- upstream: `https://github.com/alexbredo/honeypot-ftp.git`
- default branch: `master`
- commit: `c7b7cbed4c52d3d84b62676dd1a359c6d9da2696`
- workspace clone: `.local/labs/honeypot-ftp`
- telemetry: `.local/labs/honeypot-ftp-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp`
- container: `uhbs-target-honeypot-ftp-ftp` · alias `honeypot-ftp-lab`:21
- strategy: `ubuntu-wrapper` · base: `ubuntu:latest`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/alexbredo/honeypot-ftp.git .local/labs/honeypot-ftp
git -C .local/labs/honeypot-ftp rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/honeypot-ftp rev-parse HEAD                # c7b7cbed4c52d3d84b62676dd1a359c6d9da2696
```

Docs reviewed: `README.md`, `ftp.py`.

## 2. Runtime decision

`ubuntu-wrapper`. ubuntu-wrapper: no upstream Dockerfile; Twisted FTP lab entry ftp_lab.py plus base/handler stubs.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/honeypot-ftp-telemetry
touch .local/labs/honeypot-ftp-telemetry/egress-gateway.log
cp docs/conformance/labs/honeypot-ftp/Dockerfile.lab .local/labs/honeypot-ftp/
cp docs/conformance/labs/honeypot-ftp/ftp_lab.py .local/labs/honeypot-ftp/
cp -R docs/conformance/labs/honeypot-ftp/base docs/conformance/labs/honeypot-ftp/handler .local/labs/honeypot-ftp/
docker build -f .local/labs/honeypot-ftp/Dockerfile.lab -t honeypot-ftp:uhbs-lab .local/labs/honeypot-ftp
mkdir -p .local/labs/honeypot-ftp-telemetry
touch .local/labs/honeypot-ftp-telemetry/egress-gateway.log
docker rm -f uhbs-target-honeypot-ftp-ftp 2>/dev/null || true
docker run -d \
  --name uhbs-target-honeypot-ftp-ftp \
  --network uhbs-lab \
  --network-alias honeypot-ftp-lab \
  -v "$PWD/.local/labs/honeypot-ftp-telemetry:/telemetry:rw" \
  honeypot-ftp:uhbs-lab
```

Smoke from `uhbs:5.0.0` on `uhbs-lab` against `honeypot-ftp-lab:21`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id honeypot-ftp-ftp --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image honeypot-ftp:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/honeypot-ftp:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/honeypot-ftp/inventory.yaml \
    --target honeypot-ftp-ftp \
    --tps /work/docs/conformance/labs/honeypot-ftp/low_interaction_ftp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/quick \
    --environment "Quick Docker lab: honeypot-ftp-ftp" \
  > docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/honeypot-ftp-telemetry/egress-gateway.log
docker logs uhbs-target-honeypot-ftp-ftp >> .local/labs/honeypot-ftp-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.0-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id honeypot-ftp-ftp --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image honeypot-ftp:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/full/proof/full-run.cast \
  -c /tmp/uhbs-full-honeypot-ftp-ftp.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/honeypot-ftp:/honeypot:ro" \
  -v "$PWD/.local/labs/honeypot-ftp-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.0-full lab \
    --inventory /work/docs/conformance/labs/honeypot-ftp/inventory.yaml \
    --target honeypot-ftp-ftp \
    --tps /work/docs/conformance/labs/honeypot-ftp/low_interaction_ftp_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/full \
    --environment "Full Docker lab: honeypot-ftp-ftp" \
  2>&1 | tee docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/honeypot-ftp-ftp.scorecard.json --strict
python scripts/validate_unit.py --unit-id honeypot-ftp-ftp
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/quick/`
- full: `docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/full/`
- cast: `docs/conformance/latest/results-5.0.0/honeypot-ftp/ftp/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/honeypot-ftp-ftp.scorecard.json`

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
