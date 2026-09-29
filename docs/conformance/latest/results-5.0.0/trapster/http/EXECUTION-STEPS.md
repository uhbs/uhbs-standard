# Execution steps — `trapster-http`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Same clone/image/container as `trapster-ssh`. Commands ran from the UHBS repo root.

## Identity

- unit_id: `trapster-http`
- benchmark: `trapster` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/0xBallpoint/trapster-community.git`
- default branch: `main`
- commit: `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`
- workspace clone: `.local/labs/trapster`
- target: `uhbs-target-trapster` alias `trapster-lab:8080`
- latest path: `docs/conformance/latest/results-5.0.1/trapster/http`

Clone, runtime decision, and `docker build`/`docker run` are identical to [`../ssh/EXECUTION-STEPS.md`](../ssh/EXECUTION-STEPS.md) (upstream `python:3.11-slim` Dockerfile; lab `trapster.conf`).

## Quick run (`uhbs:5.0.1`)

```bash
python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id trapster-http --mode quick --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1 --target-image trapster:uhbs-lab \
  --base-image python:3.11-slim --strategy upstream-docker --airgap-attested

docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/trapster:/honeypot:ro" -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/trapster/inventory.yaml \
    --target trapster-http \
    --tps /work/docs/conformance/labs/trapster/web_api_http_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools --concurrency 10 --requests 50 \
    --out /work/docs/conformance/latest/results-5.0.1/trapster/http/quick \
    --environment "Quick Docker lab: trapster-http" \
  > docs/conformance/latest/results-5.0.1/trapster/http/quick/uhbs-run.log 2>&1
```

## Telemetry + full (`uhbs:5.0.1-full`)

```bash
docker logs uhbs-target-trapster > .local/labs/trapster-telemetry/trapster.log 2>&1

python scripts/tracker.py --db .local/benchmark-refresh/results-5.0.1.sqlite3 log-run-start \
  --unit-id trapster-http --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image trapster:uhbs-lab \
  --base-image python:3.11-slim --strategy upstream-docker --airgap-attested

asciinema rec --overwrite \
  docs/conformance/latest/results-5.0.1/trapster/http/full/proof/full-run.cast \
  -c .local/benchmark-refresh/run_trapster_http_full.sh
```

Full docker command inside the wrapper:

```bash
docker run --rm --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/trapster:/honeypot:ro" \
  -v "$PWD/.local/labs/trapster-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:5.0.1-full lab \
    --inventory /work/docs/conformance/labs/trapster/inventory.yaml \
    --target trapster-http \
    --tps /work/docs/conformance/labs/trapster/web_api_http_full.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --concurrency 25 --requests 200 \
    --out /work/docs/conformance/latest/results-5.0.1/trapster/http/full \
    --environment "Full Docker lab: trapster-http"
```

## Fixture + verifier

```bash
uhbs validate-scorecard docs/conformance/fixtures/trapster-http.scorecard.json --strict
python scripts/validate_unit.py --unit-id trapster-http
python scripts/rebuild_mkdocs_nav.py
pytest -q --no-cov tests/test_web_lab_results.py tests/test_conformance.py
```

Honest UHBS 5.0.1 outcome: **INCOMPLETE / ungraded** (Module C declared-format; Module D non-SSH gateway/packet evidence). Do not copy archived 4.x UHQS 63.33 / D.
