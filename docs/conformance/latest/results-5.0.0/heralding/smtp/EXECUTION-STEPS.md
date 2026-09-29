# Execution steps — `heralding-smtp`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `heralding-smtp`
- benchmark: `heralding` · protocol: `smtp` · class: `Low-Interaction`
- upstream: `https://github.com/johnnykv/heralding.git`
- default branch: `master`
- commit: `ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0`
- workspace clone: `.local/labs/heralding`
- telemetry: `.local/labs/heralding-telemetry`
- latest path: `docs/conformance/latest/results-5.0.1/heralding/smtp`
- container: `uhbs-target-heralding-smtp` · alias `heralding-smtp-lab`:25
- strategy: `custom-base` · base: `python:3.11-slim-bookworm`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/johnnykv/heralding.git .local/labs/heralding
git -C .local/labs/heralding rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/heralding rev-parse HEAD                # ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0
```

Docs reviewed: `README.md`, `Dockerfile`, `heralding/heralding.yaml`.

## 2. Runtime decision

`custom-base`. Same custom-base image as FTP/SSH; dedicated SMTP-only config on a second alias.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/heralding-telemetry
touch .local/labs/heralding-telemetry/egress-gateway.log
docker rm -f uhbs-target-heralding-smtp 2>/dev/null || true
docker run -d \
  --name uhbs-target-heralding-smtp \
  --network uhbs-lab \
  --network-alias heralding-smtp-lab \
  -v "$PWD/docs/conformance/labs/heralding/heralding-smtp-lab.yml:/config/heralding.yml:ro" \
  -v "$PWD/.local/labs/heralding-telemetry:/telemetry:rw" \
  heralding:uhbs-lab heralding -c /config/heralding.yml
```

Smoke from `uhbs:5.0.1` on `uhbs-lab` against `heralding-smtp-lab:25`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id heralding-smtp --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image heralding:uhbs-lab \
  --base-image python:3.11-slim-bookworm --strategy custom-base --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/heralding:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/heralding/inventory.yaml \
    --target heralding-smtp \
    --tps /work/docs/conformance/labs/heralding/low_interaction_smtp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/heralding/smtp/quick \
    --environment "Quick Docker lab: heralding-smtp" \
  > docs/conformance/latest/results-5.0.1/heralding/smtp/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/heralding-telemetry/egress-gateway.log
docker logs uhbs-target-heralding-smtp >> .local/labs/heralding-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.1-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id heralding-smtp --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image heralding:uhbs-lab \
  --base-image python:3.11-slim-bookworm --strategy custom-base --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/heralding/smtp/full/proof/full-run.cast \
  -c /tmp/uhbs-full-heralding-smtp.sh
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
    --target heralding-smtp \
    --tps /work/docs/conformance/labs/heralding/low_interaction_smtp_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/heralding/smtp/full \
    --environment "Full Docker lab: heralding-smtp" \
  2>&1 | tee docs/conformance/latest/results-5.0.1/heralding/smtp/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/heralding-smtp.scorecard.json --strict
python scripts/validate_unit.py --unit-id heralding-smtp
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.1/heralding/smtp/quick/`
- full: `docs/conformance/latest/results-5.0.1/heralding/smtp/full/`
- cast: `docs/conformance/latest/results-5.0.1/heralding/smtp/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/heralding-smtp.scorecard.json`

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
