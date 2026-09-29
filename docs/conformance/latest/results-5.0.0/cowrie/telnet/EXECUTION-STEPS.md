# Execution steps — `cowrie-telnet`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `cowrie-telnet`
- benchmark: `cowrie` · protocol: `telnet` · class: `Low-Interaction`
- upstream: `https://github.com/cowrie/cowrie.git`
- default branch: `main`
- commit: `fef0d620962e23194a9d34a048488f9c76c85835`
- workspace clone: `.local/labs/cowrie`
- telemetry: `.local/labs/cowrie-telemetry`
- latest path: `docs/conformance/latest/results-5.0.1/cowrie/telnet`
- container: `uhbs-target-cowrie-ssh` · alias `cowrie-lab`:2223
- strategy: `upstream-docker` · base: `gcr.io/distroless/python3-debian13`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/cowrie/cowrie.git .local/labs/cowrie
git -C .local/labs/cowrie rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/cowrie rev-parse HEAD                # fef0d620962e23194a9d34a048488f9c76c85835
```

Docs reviewed: `README.md`, `INSTALL.rst`, `docs/conformance/labs/cowrie/cowrie.cfg`.

## 2. Runtime decision

`upstream-docker`. Same official cowrie/cowrie:latest container as SSH; Telnet enabled via cowrie.cfg overlay.

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/cowrie-telemetry
touch .local/labs/cowrie-telemetry/egress-gateway.log
Shares `uhbs-target-cowrie-ssh` / alias `cowrie-lab` (Telnet :2223 on the same image).
```

Smoke from `uhbs:5.0.1` on `uhbs-lab` against `cowrie-lab:2223`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id cowrie-telnet --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image cowrie/cowrie:latest \
  --base-image gcr.io/distroless/python3-debian13 --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/cowrie:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/cowrie/inventory.yaml \
    --target cowrie-telnet \
    --tps /work/docs/conformance/labs/cowrie/low_interaction_telnet_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/cowrie/telnet/quick \
    --environment "Quick Docker lab: cowrie-telnet" \
  > docs/conformance/latest/results-5.0.1/cowrie/telnet/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/cowrie-telemetry/egress-gateway.log
docker logs uhbs-target-cowrie-ssh >> .local/labs/cowrie-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.1-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id cowrie-telnet --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image cowrie/cowrie:latest \
  --base-image gcr.io/distroless/python3-debian13 --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/cowrie/telnet/full/proof/full-run.cast \
  -c /tmp/uhbs-full-cowrie-telnet.sh
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
  uhbs:5.0.1-full lab \
    --inventory /work/docs/conformance/labs/cowrie/inventory.yaml \
    --target cowrie-telnet \
    --tps /work/docs/conformance/labs/cowrie/low_interaction_telnet_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/cowrie/telnet/full \
    --environment "Full Docker lab: cowrie-telnet" \
  2>&1 | tee docs/conformance/latest/results-5.0.1/cowrie/telnet/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/cowrie-telnet.scorecard.json --strict
python scripts/validate_unit.py --unit-id cowrie-telnet
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.1/cowrie/telnet/quick/`
- full: `docs/conformance/latest/results-5.0.1/cowrie/telnet/full/`
- cast: `docs/conformance/latest/results-5.0.1/cowrie/telnet/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/cowrie-telnet.scorecard.json`

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
