# Execution steps — `honeyup-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `honeyup-http`
- benchmark: `honeyup` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/LogoiLab/honeyup.git`
- default branch: `master`
- commit: `2d0169da30e76eed979a9a0950015b90f0454740`
- latest path: `docs/conformance/latest/results-5.0.1/honeyup/http`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/LogoiLab/honeyup.git .local/labs/honeyup
git -C .local/labs/honeyup rev-parse --abbrev-ref HEAD
git -C .local/labs/honeyup rev-parse HEAD
```

Docs reviewed: README.md, Dockerfile.dev, docker-compose.yml, entrypoint.sh.

## 2. Runtime

Strategy `ubuntu-wrapper` · base `ubuntu:latest`. Upstream docker-compose + Dockerfile.dev reclones GitHub during build. Lab builds the cloned HEAD tree on ubuntu:latest with cargo.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/honeyup/Dockerfile.lab -t honeyup:uhbs-lab .local/labs/honeyup
docker rm -f honeyup-lab 2>/dev/null || true
docker run -d --name honeyup-lab --network uhbs-lab --network-alias honeyup-lab \
  -p 127.0.0.1:18091:4000 honeyup:uhbs-lab
curl -sS -m 5 http://127.0.0.1:18091/uploads
```

## 4. Quick (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id honeyup-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image honeyup:uhbs-lab \
  --base-image ubuntu:latest --strategy ubuntu-wrapper --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/honeyup:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/honeyup/inventory.yaml \
    --target honeyup-http \
    --tps /work/docs/conformance/labs/honeyup/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/honeyup/http/quick \
    --environment "Quick Docker lab: honeyup-http" \
  > docs/conformance/latest/results-5.0.1/honeyup/http/quick/uhbs-run.log 2>&1
```

## 5. Full + asciinema (`uhbs:5.0.1-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/honeyup/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/honeyup-http-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/honeyup-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id honeyup-http
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / INCOMPLETE**. Do not copy archived 4.x letter grades.
