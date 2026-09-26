# Execution steps — `HellPot-http`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `HellPot-http`
- benchmark: `HellPot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/yunginnanet/HellPot.git`
- default branch: `main`
- commit: `0ba62c99ea4599ec32474e4982a8ea4d4105c471`
- latest path: `docs/conformance/latest/results-5.0.0/HellPot/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/yunginnanet/HellPot.git .local/labs/HellPot
git -C .local/labs/HellPot rev-parse --abbrev-ref HEAD
git -C .local/labs/HellPot rev-parse HEAD
```

Docs reviewed: README.md, Dockerfile, docker_config.toml.

## 2. Runtime

Strategy `ubuntu-wrapper` · base `ubuntu:latest`. Upstream Dockerfile is golang:1.23 + distroless; lab uses golang:1.23 builder then ubuntu:latest runtime with catch-all bind and no curl UA blacklist.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/HellPot/Dockerfile.lab -t hellpot:uhbs-lab .local/labs/HellPot
docker rm -f HellPot-lab 2>/dev/null || true
docker run -d --name HellPot-lab --network uhbs-lab --network-alias HellPot-lab \
  -p 127.0.0.1:18180:8080 hellpot:uhbs-lab
curl -sS -m 5 http://127.0.0.1:18180/
```

## 4. Quick (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id HellPot-http --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image hellpot:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/HellPot:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/HellPot/inventory.yaml \
    --target HellPot-http \
    --tps /work/docs/conformance/labs/HellPot/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.0/HellPot/http/quick \
    --environment "Quick Docker lab: HellPot-http" \
  > docs/conformance/latest/results-5.0.0/HellPot/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.0-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.0/HellPot/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/HellPot-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/hellpot-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id HellPot-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.0 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
