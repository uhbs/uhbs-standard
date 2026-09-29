# Execution steps — `elastichoney-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `elastichoney-http`
- benchmark: `elastichoney` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/jordan-wright/elastichoney.git`
- default branch: `master`
- commit: `1b03740e34c6a60991432d53c237773d484571eb`
- latest path: `docs/conformance/latest/results-5.0.1/elastichoney/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/jordan-wright/elastichoney.git .local/labs/elastichoney
git -C .local/labs/elastichoney rev-parse --abbrev-ref HEAD
git -C .local/labs/elastichoney rev-parse HEAD
```

Docs reviewed: README.md, Dockerfile, docker-compose.yml, config.json.

## 2. Runtime

Strategy `ubuntu-wrapper` · base `ubuntu:latest`. Upstream Dockerfile is golang:1.3-onbuild (unusable). Built with golang:1.22 and ran on ubuntu:latest; anonymous=true avoids outbound IP lookup.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/elastichoney/Dockerfile.lab -t elastichoney:uhbs-lab .local/labs/elastichoney
docker rm -f elastichoney-lab 2>/dev/null || true
docker run -d --name elastichoney-lab --network uhbs-lab --network-alias elastichoney-lab \
  -p 127.0.0.1:19201:9200 elastichoney:uhbs-lab
curl -sS -m 5 http://127.0.0.1:19201/
```

## 4. Quick (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id elastichoney-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image elastichoney:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/elastichoney:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/elastichoney/inventory.yaml \
    --target elastichoney-http \
    --tps /work/docs/conformance/labs/elastichoney/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/elastichoney/http/quick \
    --environment "Quick Docker lab: elastichoney-http" \
  > docs/conformance/latest/results-5.0.1/elastichoney/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/elastichoney/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/elastichoney-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/elastichoney-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id elastichoney-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
