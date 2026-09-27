# Execution steps — `honeymcp-mcp`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root. Do not transplant archived 4.x letter grades.

## Identity

- unit_id: `honeymcp-mcp`
- benchmark: `honeymcp` · protocol: `mcp` · class: `Web-API`
- upstream: `https://github.com/kosiorkosa47/honeymcp.git`
- default branch: `main`
- commit: `966bb908d140809957ba01e05132631c514ade5d`
- workspace clone: `.local/labs/honeymcp`
- telemetry: `.local/labs/honeymcp-telemetry`
- latest path: `docs/conformance/latest/results-5.0.0/honeymcp/mcp`
- container: `uhbs-target-honeymcp-mcp` · alias `honeymcp-lab`:8080
- strategy: `upstream-docker` · base: `debian:bookworm-slim`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/kosiorkosa47/honeymcp.git .local/labs/honeymcp
git -C .local/labs/honeymcp rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/honeymcp rev-parse HEAD                # 966bb908d140809957ba01e05132631c514ade5d
```

Docs reviewed: `README.md`, `Dockerfile`, `src/transport/http.rs`.

## 2. Runtime decision

`upstream-docker`. Upstream Dockerfile (rust:1.89-slim-bookworm builder, debian:bookworm-slim runtime). Lab patch raises governor per_second(50)/burst_size(500).

## 3. Build and start target

```bash
docker network create uhbs-lab 2>/dev/null || true
mkdir -p .local/labs/honeymcp-telemetry
touch .local/labs/honeymcp-telemetry/egress-gateway.log
git -C .local/labs/honeymcp apply ../../docs/conformance/labs/honeymcp/rate-limit-lab.patch
docker build -t honeymcp:uhbs-lab .local/labs/honeymcp
mkdir -p .local/labs/honeymcp-telemetry
touch .local/labs/honeymcp-telemetry/egress-gateway.log
docker rm -f uhbs-target-honeymcp-mcp 2>/dev/null || true
docker run -d \
  --name uhbs-target-honeymcp-mcp \
  --network uhbs-lab \
  --network-alias honeymcp-lab \
  -v "$PWD/.local/labs/honeymcp-telemetry:/var/lib/honeymcp" \
  honeymcp:uhbs-lab
```

Smoke from `uhbs:5.0.0` on `uhbs-lab` against `honeymcp-lab:8080`. No host `-p` publish.

## 4. Quick run (`uhbs:5.0.0`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id honeymcp-mcp --mode quick --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0 --target-image honeymcp:uhbs-lab \
  --base-image debian:bookworm-slim --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/honeymcp:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/honeymcp/inventory.yaml \
    --target honeymcp-mcp \
    --tps /work/docs/conformance/labs/honeymcp/web_api_mcp_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.0/honeymcp/mcp/quick \
    --environment "Quick Docker lab: honeymcp-mcp" \
  > docs/conformance/latest/results-5.0.0/honeymcp/mcp/quick/uhbs-run.log 2>&1
```

## 5. Telemetry seed

```bash
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/honeymcp-telemetry/egress-gateway.log
docker logs uhbs-target-honeymcp-mcp >> .local/labs/honeymcp-telemetry/target.log 2>&1 || true
```

## 6. Full run + asciinema (`uhbs:5.0.0-full`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.0.sqlite3 log-run-start \
  --unit-id honeymcp-mcp --mode full --uhbs-version 5.0.0 \
  --grader-image uhbs:5.0.0-full --target-image honeymcp:uhbs-lab \
  --base-image debian:bookworm-slim --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.0/honeymcp/mcp/full/proof/full-run.cast \
  -c /tmp/uhbs-full-honeymcp-mcp.sh
```

Inner command:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/honeymcp:/honeypot:ro" \
  -v "$PWD/.local/labs/honeymcp-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.0-full lab \
    --inventory /work/docs/conformance/labs/honeymcp/inventory.yaml \
    --target honeymcp-mcp \
    --tps /work/docs/conformance/labs/honeymcp/web_api_mcp_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.0/honeymcp/mcp/full \
    --environment "Full Docker lab: honeymcp-mcp" \
  2>&1 | tee docs/conformance/latest/results-5.0.0/honeymcp/mcp/full/uhbs-run.log
```

## 7. Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/honeymcp-mcp.scorecard.json --strict
python scripts/validate_unit.py --unit-id honeymcp-mcp
python scripts/rebuild_mkdocs_nav.py
```

## Output paths

- quick: `docs/conformance/latest/results-5.0.0/honeymcp/mcp/quick/`
- full: `docs/conformance/latest/results-5.0.0/honeymcp/mcp/full/`
- cast: `docs/conformance/latest/results-5.0.0/honeymcp/mcp/full/proof/full-run.cast`
- fixture: `docs/conformance/fixtures/honeymcp-mcp.scorecard.json`

Honest UHBS 5.0.0 outcome: **INCOMPLETE / ungraded (non-SSH Module D)**. Assessment `INCOMPLETE` · Critical controls `INCOMPLETE`. Do not copy archived 4.x grades.
