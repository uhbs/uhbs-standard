# Execution steps — `express-honeypot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `express-honeypot-http`
- benchmark: `express-honeypot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/christophe77/express-honeypot.git`
- default branch: `main`
- commit: `618c9696f5548b63676c661fd97ef4cb79fde1d3`
- latest path: `docs/conformance/latest/results-5.0.1/express-honeypot/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/christophe77/express-honeypot.git .local/labs/express-honeypot
git -C .local/labs/express-honeypot rev-parse --abbrev-ref HEAD
git -C .local/labs/express-honeypot rev-parse HEAD
```

Docs reviewed: readme.md, package.json, express/config.js.

## 2. Runtime

Strategy `custom-base` · base `node:20-bookworm-slim`. No upstream Dockerfile; README is Node/yarn. Ubuntu apt nodejs is a huge package set; official Node 20 image is the documented runtime.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/express-honeypot/Dockerfile.lab -t express-honeypot:uhbs-lab .local/labs/express-honeypot
docker rm -f express-honeypot-lab 2>/dev/null || true
docker run -d --name express-honeypot-lab --network uhbs-lab --network-alias express-honeypot-lab \
  -p 127.0.0.1:13001:3001 express-honeypot:uhbs-lab
curl -sS -m 5 http://127.0.0.1:13001/
```

## 4. Quick (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id express-honeypot-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image express-honeypot:uhbs-lab \
  --base-image node:20-bookworm-slim --strategy custom-base --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/express-honeypot:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/express-honeypot/inventory.yaml \
    --target express-honeypot-http \
    --tps /work/docs/conformance/labs/express-honeypot/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/express-honeypot/http/quick \
    --environment "Quick Docker lab: express-honeypot-http" \
  > docs/conformance/latest/results-5.0.1/express-honeypot/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/express-honeypot/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/express-honeypot-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/express-honeypot-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id express-honeypot-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
