# Execution steps — `genaipot-smtp`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `genaipot-smtp`
- benchmark: `genaipot` · protocol: `smtp` · class: `Low-Interaction`
- upstream: `https://github.com/eduardobsg/GenAIPot.git`
- default branch: `main`
- commit: `205ffe40008f2e76e0decdb01bc19bf8e00acd8a`
- workspace clone: `.local/labs/genaipot`
- telemetry: `.local/labs/genaipot-telemetry`
- latest path: `docs/conformance/latest/results-5.0.1/genaipot/smtp`
- container: `uhbs-target-genaipot-smtp` · alias `genaipot-lab`:25
- strategy: `upstream-docker` · base: `python:3.9-slim`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/eduardobsg/GenAIPot.git .local/labs/genaipot
git -C .local/labs/genaipot rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/genaipot rev-parse HEAD                # 205ffe40008f2e76e0decdb01bc19bf8e00acd8a
```

Docs reviewed: `README.md`, `Dockerfile`, `app.py`.

## 2. Runtime decision

`upstream-docker`. upstream-docker Hub image annls/genaipot:latest (Dockerfile FROM python:3.9-slim). ls1911/GenAIPot clone required auth; SHA matches eduardobsg/GenAIPot@205ffe4.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/genaipot-telemetry
touch .local/labs/genaipot-telemetry/egress-gateway.log
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/eduardobsg/GenAIPot.git .local/labs/genaipot
docker rm -f uhbs-target-genaipot-smtp 2>/dev/null || true
mkdir -p .local/labs/genaipot-telemetry
touch .local/labs/genaipot-telemetry/egress-gateway.log
docker run -d \
  --name uhbs-target-genaipot-smtp \
  --network uhbs-lab \
  --network-alias genaipot-lab \
  -v "$PWD/.local/labs/genaipot-telemetry:/telemetry:rw" \
  annls/genaipot:latest
```

Smoke from `uhbs:5.0.1` on `uhbs-lab` against `genaipot-lab:25`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id genaipot-smtp --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image annls/genaipot:latest \
  --base-image python:3.9-slim --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/genaipot:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/genaipot/inventory.yaml \
    --target genaipot-smtp \
    --tps /work/docs/conformance/labs/genaipot/low_interaction_smtp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/genaipot/smtp/quick \
    --environment "Quick Docker lab: genaipot-smtp" \
  > docs/conformance/latest/results-5.0.1/genaipot/smtp/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/genaipot-telemetry/egress-gateway.log
docker logs uhbs-target-genaipot-smtp >> .local/labs/genaipot-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.1-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id genaipot-smtp --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image annls/genaipot:latest \
  --base-image python:3.9-slim --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/genaipot/smtp/full/proof/full-run.cast \
  -c /tmp/uhbs-full-genaipot-smtp.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/genaipot:/honeypot:ro" \
  -v "$PWD/.local/labs/genaipot-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.1-full lab \
    --inventory /work/docs/conformance/labs/genaipot/inventory.yaml \
    --target genaipot-smtp \
    --tps /work/docs/conformance/labs/genaipot/low_interaction_smtp_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/genaipot/smtp/full \
    --environment "Full Docker lab: genaipot-smtp" \
  2>&1 | tee docs/conformance/latest/results-5.0.1/genaipot/smtp/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/genaipot-smtp.scorecard.json --strict
python scripts/validate_unit.py --unit-id genaipot-smtp
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.1/genaipot/smtp/quick/`
- full: `docs/conformance/latest/results-5.0.1/genaipot/smtp/full/`
- cast: `docs/conformance/latest/results-5.0.1/genaipot/smtp/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/genaipot-smtp.scorecard.json`

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
