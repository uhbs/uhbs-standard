# Execution steps — `Log4Pot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `Log4Pot-http`
- benchmark: `Log4Pot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/thomaspatzke/Log4Pot.git`
- default branch: `master`
- commit: `5002b1fe0f82359ef32dbc3a899e8a701dc3256e`
- latest path: `docs/conformance/latest/results-5.0.1/Log4Pot/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/thomaspatzke/Log4Pot.git .local/labs/Log4Pot
git -C .local/labs/Log4Pot rev-parse --abbrev-ref HEAD
git -C .local/labs/Log4Pot rev-parse HEAD
```

Docs reviewed: README.md, log4pot-server.py, log4pot.conf.example, pyproject.toml.

## 2. Runtime

Strategy `ubuntu-wrapper` · base `ubuntu:latest`. No upstream Dockerfile. README allows running without Azure extras via python log4pot-server.py. Ubuntu latest + python3 (stdlib HTTP server).

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/Log4Pot/Dockerfile.lab -t log4pot:uhbs-lab .local/labs/Log4Pot
docker rm -f Log4Pot-lab 2>/dev/null || true
docker run -d --name Log4Pot-lab --network uhbs-lab --network-alias Log4Pot-lab \
  -p 127.0.0.1:18083:8080 log4pot:uhbs-lab
curl -sS -m 5 http://127.0.0.1:18083/
```

## 4. Quick (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id Log4Pot-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image log4pot:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/Log4Pot:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/Log4Pot/inventory.yaml \
    --target Log4Pot-http \
    --tps /work/docs/conformance/labs/Log4Pot/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/Log4Pot/http/quick \
    --environment "Quick Docker lab: Log4Pot-http" \
  > docs/conformance/latest/results-5.0.1/Log4Pot/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/Log4Pot/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/Log4Pot-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/log4pot-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id Log4Pot-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
