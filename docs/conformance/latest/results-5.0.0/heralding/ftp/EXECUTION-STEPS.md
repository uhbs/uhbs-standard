# Execution steps — `heralding-ftp`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `heralding-ftp`
- benchmark: `heralding` · protocol: `ftp` · class: `Low-Interaction`
- upstream: `https://github.com/johnnykv/heralding.git`
- default branch: `master`
- commit: `ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0`
- workspace clone: `.local/labs/heralding`
- telemetry: `.local/labs/heralding-telemetry`
- latest path: `docs/conformance/latest/results-5.0.1/heralding/ftp`
- container: `uhbs-target-heralding-ftp` · alias `heralding-lab`:21
- strategy: `custom-base` · base: `python:3.11-slim-bookworm`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/johnnykv/heralding.git .local/labs/heralding
git -C .local/labs/heralding rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/heralding rev-parse HEAD                # ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0
```

Docs reviewed: `README.md`, `Dockerfile`, `heralding/heralding.yaml`, `setup.py`.

## 2. Runtime decision

`custom-base`. custom-base: upstream python:3.9-slim-bullseye apt indexes 404; ubuntu:latest + CPython 3.14 failed psycopg2-binary.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/heralding-telemetry
touch .local/labs/heralding-telemetry/egress-gateway.log
cp docs/conformance/labs/heralding/Dockerfile.lab .local/labs/heralding/Dockerfile.lab
cp docs/conformance/labs/heralding/heralding-lab.yml .local/labs/heralding/heralding-lab.yml
docker build -f .local/labs/heralding/Dockerfile.lab -t heralding:uhbs-lab .local/labs/heralding
docker rm -f uhbs-target-heralding-ftp 2>/dev/null || true
docker run -d \
  --name uhbs-target-heralding-ftp \
  --network uhbs-lab \
  --network-alias heralding-lab \
  -v "$PWD/docs/conformance/labs/heralding/heralding-lab.yml:/config/heralding.yml:ro" \
  -v "$PWD/.local/labs/heralding-telemetry:/telemetry:rw" \
  heralding:uhbs-lab heralding -c /config/heralding.yml
```

Smoke from `uhbs:5.0.1` on `uhbs-lab` against `heralding-lab:21`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id heralding-ftp --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image heralding:uhbs-lab \
  --base-image python:3.11-slim-bookworm --strategy custom-base --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/heralding:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/heralding/inventory.yaml \
    --target heralding-ftp \
    --tps /work/docs/conformance/labs/heralding/low_interaction_ftp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/heralding/ftp/quick \
    --environment "Quick Docker lab: heralding-ftp" \
  > docs/conformance/latest/results-5.0.1/heralding/ftp/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/heralding-telemetry/egress-gateway.log
docker logs uhbs-target-heralding-ftp >> .local/labs/heralding-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.1-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id heralding-ftp --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image heralding:uhbs-lab \
  --base-image python:3.11-slim-bookworm --strategy custom-base --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/heralding/ftp/full/proof/full-run.cast \
  -c /tmp/uhbs-full-heralding-ftp.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/heralding:/honeypot:ro" \
  -v "$PWD/.local/labs/heralding-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.1-full lab \
    --inventory /work/docs/conformance/labs/heralding/inventory.yaml \
    --target heralding-ftp \
    --tps /work/docs/conformance/labs/heralding/low_interaction_ftp_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/heralding/ftp/full \
    --environment "Full Docker lab: heralding-ftp" \
  2>&1 | tee docs/conformance/latest/results-5.0.1/heralding/ftp/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/heralding-ftp.scorecard.json --strict
python scripts/validate_unit.py --unit-id heralding-ftp
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.1/heralding/ftp/quick/`
- full: `docs/conformance/latest/results-5.0.1/heralding/ftp/full/`
- cast: `docs/conformance/latest/results-5.0.1/heralding/ftp/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/heralding-ftp.scorecard.json`

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
