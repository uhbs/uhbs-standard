# Execution steps — `flux-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `flux-http`
- benchmark: `flux` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/andrewmichaelsmith/flux.git`
- default branch: `main`
- commit: `0db4b8b0b87243d2061137212e49311bfbbd38b1`
- latest path: `docs/conformance/latest/results-5.0.1/flux/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/andrewmichaelsmith/flux.git .local/labs/flux
git -C .local/labs/flux rev-parse --abbrev-ref HEAD
git -C .local/labs/flux rev-parse HEAD
```

Docs reviewed: README.md, CONFIG.md, pyproject.toml.

## 2. Runtime

Strategy `custom-base` · base `python:3.12-slim`. No upstream Dockerfile. README is pip install aiohttp; python -m flux (Python 3.11+). python:3.12-slim matches documented runtime; bind patched 0.0.0.0:8080; tarpit disabled so grader probes on /login do not hang.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/flux/Dockerfile.lab -t flux:uhbs-lab .local/labs/flux
docker rm -f flux-lab 2>/dev/null || true
docker run -d --name flux-lab --network uhbs-lab --network-alias flux-lab \
  -p 127.0.0.1:18094:8080 flux:uhbs-lab
curl -sS -m 5 http://127.0.0.1:18094/login
```

## 4. Quick (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id flux-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image flux:uhbs-lab \
  --base-image python:3.12-slim --strategy custom-base --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/flux:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/flux/inventory.yaml \
    --target flux-http \
    --tps /work/docs/conformance/labs/flux/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/flux/http/quick \
    --environment "Quick Docker lab: flux-http" \
  > docs/conformance/latest/results-5.0.1/flux/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/flux/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/flux-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/flux-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id flux-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
