# Execution steps — `honeyhttpd-http`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `honeyhttpd-http`
- benchmark: `honeyhttpd` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/bocajspear1/honeyhttpd.git`
- default branch: `master`
- commit: `edec2700f3248b73fce00893a9ed6f2833ac05fd`
- latest path: `docs/conformance/latest/results-5.0.0/honeyhttpd/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/bocajspear1/honeyhttpd.git .local/labs/honeyhttpd
git -C .local/labs/honeyhttpd rev-parse --abbrev-ref HEAD
git -C .local/labs/honeyhttpd rev-parse HEAD
```

Docs reviewed: README.md, requirements.txt, config.json.default, start.py.

## 2. Runtime

Strategy `ubuntu-wrapper` · base `ubuntu:latest`. No upstream Dockerfile. README: pip + python3 start.py. Ubuntu latest.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/honeyhttpd/Dockerfile.lab -t honeyhttpd:uhbs-lab .local/labs/honeyhttpd
docker rm -f honeyhttpd-lab 2>/dev/null || true
docker run -d --name honeyhttpd-lab --network uhbs-lab --network-alias honeyhttpd-lab \
  -p 127.0.0.1:18084:8080 honeyhttpd:uhbs-lab
curl -sS -m 5 http://127.0.0.1:18084/
```

## 4. Quick (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id honeyhttpd-http --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image honeyhttpd:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/honeyhttpd:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/honeyhttpd/inventory.yaml \
    --target honeyhttpd-http \
    --tps /work/docs/conformance/labs/honeyhttpd/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.0/honeyhttpd/http/quick \
    --environment "Quick Docker lab: honeyhttpd-http" \
  > docs/conformance/latest/results-5.0.0/honeyhttpd/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.0-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.0/honeyhttpd/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/honeyhttpd-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/honeyhttpd-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id honeyhttpd-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.0 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
