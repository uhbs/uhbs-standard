# Execution steps — `mysql-honeypotd-mysql`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `mysql-honeypotd-mysql`
- benchmark: `mysql-honeypotd` · protocol: `mysql` · class: `Low-Interaction`
- upstream: `https://github.com/sjinks/mysql-honeypotd.git`
- default branch: `master`
- commit: `955ecce4ce22c8588da1f023dfd790099755d575`
- workspace clone: `.local/labs/mysql-honeypotd`
- telemetry: `.local/labs/mysql-honeypotd-telemetry`
- latest path: `docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql`
- container: `uhbs-target-mysql-honeypotd-mysql` · alias `mysql-honeypotd-lab`:3306
- strategy: `upstream-docker` · base: `scratch`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/sjinks/mysql-honeypotd.git .local/labs/mysql-honeypotd
git -C .local/labs/mysql-honeypotd rev-parse --abbrev-ref HEAD   # master
git -C .local/labs/mysql-honeypotd rev-parse HEAD                # 955ecce4ce22c8588da1f023dfd790099755d575
```

Docs reviewed: `README.md`, `Dockerfile`.

## 2. Runtime decision

`upstream-docker`. upstream-docker: alpine:3.24 build, scratch static release (MINIMALISTIC_BUILD). Do not pass -f/-x; those flags are unrecognized in the minimal binary.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/mysql-honeypotd-telemetry
touch .local/labs/mysql-honeypotd-telemetry/egress-gateway.log
docker build -t mysql-honeypotd:uhbs-lab .local/labs/mysql-honeypotd
docker rm -f uhbs-target-mysql-honeypotd-mysql 2>/dev/null || true
docker run -d \
  --name uhbs-target-mysql-honeypotd-mysql \
  --network uhbs-lab \
  --network-alias mysql-honeypotd-lab \
  mysql-honeypotd:uhbs-lab
```

Smoke from `uhbs:5.0.1` on `uhbs-lab` against `mysql-honeypotd-lab:3306`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id mysql-honeypotd-mysql --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image mysql-honeypotd:uhbs-lab \
  --base-image scratch --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/mysql-honeypotd:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/mysql-honeypotd/inventory.yaml \
    --target mysql-honeypotd-mysql \
    --tps /work/docs/conformance/labs/mysql-honeypotd/low_interaction_mysql_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/quick \
    --environment "Quick Docker lab: mysql-honeypotd-mysql" \
  > docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/mysql-honeypotd-telemetry/egress-gateway.log
docker logs uhbs-target-mysql-honeypotd-mysql >> .local/labs/mysql-honeypotd-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.1-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id mysql-honeypotd-mysql --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image mysql-honeypotd:uhbs-lab \
  --base-image scratch --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/full/proof/full-run.cast \
  -c /tmp/uhbs-full-mysql-honeypotd-mysql.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/mysql-honeypotd:/honeypot:ro" \
  -v "$PWD/.local/labs/mysql-honeypotd-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.1-full lab \
    --inventory /work/docs/conformance/labs/mysql-honeypotd/inventory.yaml \
    --target mysql-honeypotd-mysql \
    --tps /work/docs/conformance/labs/mysql-honeypotd/low_interaction_mysql_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/full \
    --environment "Full Docker lab: mysql-honeypotd-mysql" \
  2>&1 | tee docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/mysql-honeypotd-mysql.scorecard.json --strict
python scripts/validate_unit.py --unit-id mysql-honeypotd-mysql
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/quick/`
- full: `docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/full/`
- cast: `docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/mysql-honeypotd-mysql.scorecard.json`

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
