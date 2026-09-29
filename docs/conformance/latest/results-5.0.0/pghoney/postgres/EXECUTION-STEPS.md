# Execution steps — `pghoney-postgres`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `pghoney-postgres`
- benchmark: `pghoney` · protocol: `postgres` · class: `Low-Interaction`
- upstream: `https://github.com/betheroot/pghoney.git`
- default branch: `master`
- commit: `f5d367f749f7e9353421aaf44dad856df490c441`
- workspace clone: `.local/labs/pghoney`
- telemetry: `.local/labs/pghoney-telemetry`
- latest path: `docs/conformance/latest/results-5.0.1/pghoney/postgres`
- container: `uhbs-target-pghoney-postgres` · alias `pghoney-lab`:5432
- strategy: `ubuntu-wrapper` · base: `ubuntu:latest`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/betheroot/pghoney.git .local/labs/pghoney
git -C .local/labs/pghoney rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/pghoney rev-parse HEAD                # f5d367f749f7e9353421aaf44dad856df490c441
```

Docs reviewed: `README.md`, `pghoney.go`, `pghoney.conf`.

## 2. Runtime decision

`ubuntu-wrapper`. ubuntu-wrapper Go build; hpfeeds disabled; bind 0.0.0.0; go get github.com/lib/pq.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/pghoney-telemetry
touch .local/labs/pghoney-telemetry/egress-gateway.log
cp docs/conformance/labs/pghoney/Dockerfile.lab .local/labs/pghoney/
cp docs/conformance/labs/pghoney/pghoney.lab.conf .local/labs/pghoney/pghoney.lab.conf
docker build -f .local/labs/pghoney/Dockerfile.lab -t pghoney:uhbs-lab .local/labs/pghoney
mkdir -p .local/labs/pghoney-telemetry
touch .local/labs/pghoney-telemetry/egress-gateway.log
docker rm -f uhbs-target-pghoney-postgres 2>/dev/null || true
docker run -d \
  --name uhbs-target-pghoney-postgres \
  --network uhbs-lab \
  --network-alias pghoney-lab \
  -v "$PWD/.local/labs/pghoney-telemetry:/telemetry:rw" \
  pghoney:uhbs-lab
```

Smoke from `uhbs:5.0.1` on `uhbs-lab` against `pghoney-lab:5432`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id pghoney-postgres --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image pghoney:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/pghoney:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/pghoney/inventory.yaml \
    --target pghoney-postgres \
    --tps /work/docs/conformance/labs/pghoney/database_postgres_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/pghoney/postgres/quick \
    --environment "Quick Docker lab: pghoney-postgres" \
  > docs/conformance/latest/results-5.0.1/pghoney/postgres/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/pghoney-telemetry/egress-gateway.log
docker logs uhbs-target-pghoney-postgres >> .local/labs/pghoney-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.1-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id pghoney-postgres --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image pghoney:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/pghoney/postgres/full/proof/full-run.cast \
  -c /tmp/uhbs-full-pghoney-postgres.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/pghoney:/honeypot:ro" \
  -v "$PWD/.local/labs/pghoney-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.1-full lab \
    --inventory /work/docs/conformance/labs/pghoney/inventory.yaml \
    --target pghoney-postgres \
    --tps /work/docs/conformance/labs/pghoney/database_postgres_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/pghoney/postgres/full \
    --environment "Full Docker lab: pghoney-postgres" \
  2>&1 | tee docs/conformance/latest/results-5.0.1/pghoney/postgres/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/pghoney-postgres.scorecard.json --strict
python scripts/validate_unit.py --unit-id pghoney-postgres
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.1/pghoney/postgres/quick/`
- full: `docs/conformance/latest/results-5.0.1/pghoney/postgres/full/`
- cast: `docs/conformance/latest/results-5.0.1/pghoney/postgres/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/pghoney-postgres.scorecard.json`

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
