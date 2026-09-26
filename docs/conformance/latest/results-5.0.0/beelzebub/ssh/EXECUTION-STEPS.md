# Execution steps — `beelzebub-ssh`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `beelzebub-ssh`
- benchmark: `beelzebub` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/beelzebub-labs/beelzebub.git`
- default branch: `main`
- commit: `67d5632a754f39f7b14c703d3009193150440116`
- workspace clone: `.local/labs/beelzebub`
- telemetry: `.local/labs/beelzebub-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/beelzebub/ssh`
- lab overlay: `docs/conformance/labs/beelzebub/configurations/`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 \
  https://github.com/beelzebub-labs/beelzebub.git .local/labs/beelzebub
git -C .local/labs/beelzebub rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/beelzebub rev-parse HEAD                # 67d5632a754f39f7b14c703d3009193150440116
```

Docs reviewed: `README.md`, `Dockerfile` (`golang:alpine` → `scratch`), `docker-compose.yml`, lab overlay YAMLs (static handlers, no LLM keys). `logsPath` is a file.

## 2. Runtime decision

`upstream-docker`. Final image `scratch`. Shared container `uhbs-target-beelzebub` alias `beelzebub-lab`.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/beelzebub-telemetry
touch .local/labs/beelzebub-telemetry/beelzebub.log
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/beelzebub-telemetry/egress-gateway.log
docker build -t beelzebub:uhbs-lab .local/labs/beelzebub
docker run -d \
  --name uhbs-target-beelzebub \
  --network uhbs-lab \
  --network-alias beelzebub-lab \
  -v "$PWD/docs/conformance/labs/beelzebub/configurations:/configurations:ro" \
  -v "$PWD/.local/labs/beelzebub-telemetry/beelzebub.log:/logs:rw" \
  -v "$PWD/.local/labs/beelzebub-telemetry:/telemetry:rw" \
  beelzebub:uhbs-lab
```

## 4. Quick run (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id beelzebub-ssh --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image beelzebub:uhbs-lab \
  --base-image scratch --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/beelzebub:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/beelzebub/inventory.yaml \
    --target beelzebub-ssh \
    --tps /work/docs/conformance/labs/beelzebub/low_interaction_ssh_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/beelzebub/ssh/quick \
    --environment "Quick Docker lab: beelzebub-ssh"
```

## 5. Telemetry seed

```bash
docker logs uhbs-target-beelzebub > .local/labs/beelzebub-telemetry/beelzebub-docker.log 2>&1
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/beelzebub-telemetry/egress-gateway.log
```

## 6. Full run + asciinema (`uhbs:5.0.0-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id beelzebub-ssh --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image beelzebub:uhbs-lab \
  --base-image scratch --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/beelzebub/ssh/full/proof/full-run.cast \
  -c .local/benchmark-refresh/run_beelzebub_ssh_full.sh
```

Full grader: `uhbs:5.0.0-full`, TPS `docs/conformance/labs/beelzebub/low_interaction_ssh_full.yaml`, `--concurrency 25 --requests 200`, `UHBS_AIRGAP_ATTESTED=1`, `UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log`.

## 7. Fixture + verifier

```bash
.venv/bin/uhbs validate-scorecard docs/conformance/fixtures/beelzebub-ssh.scorecard.json --strict
python scripts/validate_unit.py --unit-id beelzebub-ssh
python scripts/rebuild_mkdocs_nav.py
.venv/bin/pytest -q tests/test_web_lab_results.py --no-cov
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/beelzebub/ssh/quick/`
- full: `docs/conformance/latest/results-5.0.0/beelzebub/ssh/full/`
- cast: `docs/conformance/latest/results-5.0.0/beelzebub/ssh/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/beelzebub-ssh.scorecard.json`

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded**. Do not copy archived 4.x 59.88 / D.
