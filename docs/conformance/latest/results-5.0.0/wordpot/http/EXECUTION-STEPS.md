# Execution steps — `wordpot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `wordpot-http`
- benchmark: `wordpot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/gbrindisi/wordpot.git`
- default branch: `master`
- commit: `e96889bd5a35bbdd9fb2dd4cd583475cf7d25962`
- latest path: `docs/conformance/latest/results-5.0.1/wordpot/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/gbrindisi/wordpot.git .local/labs/wordpot
git -C .local/labs/wordpot rev-parse --abbrev-ref HEAD
git -C .local/labs/wordpot rev-parse HEAD
```

Docs reviewed: README.md, wordpot.py, wordpot.conf, requirements.txt.

## 2. Runtime

Strategy `custom-base` · base `python:2.7-slim`. Upstream is Python 2 (print statements) + Flask 0.10. Ubuntu latest has no Python 2, so python:2.7-slim is required.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/wordpot/Dockerfile.lab -t wordpot:uhbs-lab .local/labs/wordpot
docker rm -f wordpot-lab 2>/dev/null || true
docker run -d --name wordpot-lab --network uhbs-lab --network-alias wordpot-lab \
  -p 127.0.0.1:18082:8080 wordpot:uhbs-lab
curl -sS -m 5 http://127.0.0.1:18082/
```

## 4. Quick (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id wordpot-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image wordpot:uhbs-lab \
  --base-image python:2.7-slim --strategy custom-base --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/wordpot:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/wordpot/inventory.yaml \
    --target wordpot-http \
    --tps /work/docs/conformance/labs/wordpot/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/wordpot/http/quick \
    --environment "Quick Docker lab: wordpot-http" \
  > docs/conformance/latest/results-5.0.1/wordpot/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/wordpot/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/wordpot-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/wordpot-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id wordpot-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
