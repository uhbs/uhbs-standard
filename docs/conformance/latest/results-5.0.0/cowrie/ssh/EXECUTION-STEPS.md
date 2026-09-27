# Execution steps — `cowrie-ssh`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `cowrie-ssh`
- benchmark: `cowrie` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/cowrie/cowrie.git`
- default branch: `main`
- commit: `fef0d620962e23194a9d34a048488f9c76c85835`
- workspace clone: `.local/labs/cowrie`
- telemetry: `.local/labs/cowrie-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/cowrie/ssh`
- container: `uhbs-target-cowrie-ssh` · alias `cowrie-lab`:2222
- strategy: `upstream-docker` · base: `gcr.io/distroless/python3-debian13`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/cowrie/cowrie.git .local/labs/cowrie
git -C .local/labs/cowrie rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/cowrie rev-parse HEAD                # fef0d620962e23194a9d34a048488f9c76c85835
```

Docs reviewed: `README.md`, `docs/cowrie.rst`, `INSTALL.rst`, `etc/cowrie.cfg.dist`.

## 2. Runtime decision

`upstream-docker`. Official cowrie/cowrie:latest (OCI base gcr.io/distroless/python3-debian13); lab overlay enables Telnet :2223.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/cowrie-telemetry
touch .local/labs/cowrie-telemetry/egress-gateway.log
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/cowrie-telemetry
touch .local/labs/cowrie-telemetry/egress-gateway.log
docker rm -f uhbs-target-cowrie-ssh 2>/dev/null || true
docker run -d \
  --name uhbs-target-cowrie-ssh \
  --network uhbs-lab \
  --network-alias cowrie-lab \
  -e COWRIE_TELNET_ENABLED=yes \
  -v "$PWD/docs/conformance/labs/cowrie/cowrie.cfg:/cowrie/cowrie-git/etc/cowrie.cfg:ro" \
  -v "$PWD/.local/labs/cowrie-telemetry:/cowrie/cowrie-git/var/log/cowrie" \
  cowrie/cowrie:latest
# known_hosts: docs/conformance/labs/cowrie/known_hosts (mode 644; `[cowrie-lab]:2222`)
```

Smoke from `uhbs:5.0.0` on `uhbs-lab` against `cowrie-lab:2222`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id cowrie-ssh --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image cowrie/cowrie:latest \
  --base-image gcr.io/distroless/python3-debian13 --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/cowrie:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/cowrie/inventory.yaml \
    --target cowrie-ssh \
    --tps /work/docs/conformance/labs/cowrie/low_interaction_ssh_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/cowrie/ssh/quick \
    --environment "Quick Docker lab: cowrie-ssh" \
  > docs/conformance/latest/results-5.0.0/cowrie/ssh/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/cowrie-telemetry/egress-gateway.log
docker logs uhbs-target-cowrie-ssh >> .local/labs/cowrie-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.0-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id cowrie-ssh --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image cowrie/cowrie:latest \
  --base-image gcr.io/distroless/python3-debian13 --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/cowrie/ssh/full/proof/full-run.cast \
  -c /tmp/uhbs-full-cowrie-ssh.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/cowrie:/honeypot:ro" \
  -v "$PWD/.local/labs/cowrie-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  -e UHBS_SSH_KNOWN_HOSTS=/work/docs/conformance/labs/cowrie/known_hosts \
  uhbs:5.0.0-full lab \
    --inventory /work/docs/conformance/labs/cowrie/inventory.yaml \
    --target cowrie-ssh \
    --tps /work/docs/conformance/labs/cowrie/low_interaction_ssh_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.0/cowrie/ssh/full \
    --environment "Full Docker lab: cowrie-ssh" \
  2>&1 | tee docs/conformance/latest/results-5.0.0/cowrie/ssh/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/cowrie-ssh.scorecard.json --strict
python scripts/validate_unit.py --unit-id cowrie-ssh
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/cowrie/ssh/quick/`
- full: `docs/conformance/latest/results-5.0.0/cowrie/ssh/full/`
- cast: `docs/conformance/latest/results-5.0.0/cowrie/ssh/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/cowrie-ssh.scorecard.json`

Honest UHBS 5.0.0 outcome: **COMPLETE / GATE_FAILED (OOB LEAK) / ungraded**. Assessment `COMPLETE` · Critical controls `GATE_FAILED`. Do not copy archived 4.x grades.
