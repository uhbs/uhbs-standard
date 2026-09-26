# Execution steps — `trapster-ssh`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `trapster-ssh`
- benchmark: `trapster` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/0xBallpoint/trapster-community.git`
- default branch: `main`
- commit: `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`
- workspace clone: `.local/labs/trapster`
- telemetry: `.local/labs/trapster-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/trapster/ssh`
- lab config: `docs/conformance/labs/trapster/trapster.conf`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 \
  https://github.com/0xBallpoint/trapster-community.git .local/labs/trapster
git -C .local/labs/trapster rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/trapster rev-parse HEAD                # c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7
```

Docs reviewed before runtime: `README.md` (documents `docker compose up --build`), `Dockerfile` (`FROM python:3.11-slim`, `pip install .[ai]`), `docker-compose.yml`, `setup.py`, `trapster/trapster.py`, `trapster/data/trapster.conf`.

## 2. Runtime decision

`upstream-docker`. Upstream ships a maintained Dockerfile and README quick-start via Compose. Base image is `python:3.11-slim`, not `ubuntu:latest`. AI extras install but no `AI_API_KEY` is set (static SSH banner / login capture only). Lab overlay `docs/conformance/labs/trapster/trapster.conf` listens on non-privileged ports (SSH `:2222`, HTTP `:8080`, FTP `:2121`, Telnet `:2323`).

## 3. Build and start target

RSA-3072 host-key generation on first boot takes ~1–2 minutes before `:2222` is open.

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/trapster-telemetry
touch .local/labs/trapster-telemetry/egress-gateway.log
docker rm -f uhbs-target-trapster 2>/dev/null || true
docker build -t trapster:uhbs-lab .local/labs/trapster
docker run -d \
  --name uhbs-target-trapster \
  --network uhbs-lab \
  --network-alias trapster-lab \
  -v "$PWD/docs/conformance/labs/trapster/trapster.conf:/etc/trapster/trapster.conf:ro" \
  -v "$PWD/.local/labs/trapster-telemetry:/telemetry:rw" \
  trapster:uhbs-lab
```

Smoke: `python3` connect to `127.0.0.1:2222` inside the container, or reach `trapster-lab:2222` from `uhbs:5.0.0` on `uhbs-lab`.

## 4. Quick run (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id trapster-ssh --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image trapster:uhbs-lab \
  --base-image python:3.11-slim --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/trapster:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/trapster/inventory.yaml \
    --target trapster-ssh \
    --tps /work/docs/conformance/labs/trapster/low_interaction_ssh_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/trapster/ssh/quick \
    --environment "Quick Docker lab: trapster-ssh" \
  > docs/conformance/latest/results-5.0.0/trapster/ssh/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
docker logs uhbs-target-trapster \
  > .local/labs/trapster-telemetry/trapster.log 2>&1
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/trapster-telemetry/egress-gateway.log
```

Logger in the lab conf is `output: terminal` / `format: default`. Module C still reported `declared native_json but no matching records` against that sink.

## 6. Full run + asciinema (`uhbs:5.0.0-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id trapster-ssh --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image trapster:uhbs-lab \
  --base-image python:3.11-slim --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/trapster/ssh/full/proof/full-run.cast \
  -c .local/benchmark-refresh/run_trapster_ssh_full.sh
```

`run_trapster_ssh_full.sh` runs:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/trapster:/honeypot:ro" \
  -v "$PWD/.local/labs/trapster-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 \
  -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.0-full lab \
    --inventory /work/docs/conformance/labs/trapster/inventory.yaml \
    --target trapster-ssh \
    --tps /work/docs/conformance/labs/trapster/low_interaction_ssh_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.0/trapster/ssh/full \
    --environment "Full Docker lab: trapster-ssh"
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/trapster-ssh.scorecard.json --strict
python scripts/validate_unit.py --unit-id trapster-ssh
python scripts/rebuild_mkdocs_nav.py
pytest -q tests/test_web_lab_results.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/trapster/ssh/quick/`
- full: `docs/conformance/latest/results-5.0.0/trapster/ssh/full/`
- cast: `docs/conformance/latest/results-5.0.0/trapster/ssh/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/trapster-ssh.scorecard.json`

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded** (Module C native_json sink mismatch; Module D critical controls NOT_TESTED/ERROR under attested Docker air-gap). Do not copy archived 4.x UHQS 44.38 / F.
