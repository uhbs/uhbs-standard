# Execution steps — `honeymcp-mcp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `honeymcp-mcp`
- benchmark: `honeymcp` · protocol: `mcp` · class: `Web-API`
- upstream: `https://github.com/kosiorkosa47/honeymcp.git`
- branch/commit: `main` / `966bb908d140809957ba01e05132631c514ade5d`
- latest path: `docs/conformance/latest/results-5.0.1/honeymcp/mcp`
- strategy: `upstream-docker` · base: `honeymcp:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/honeymcp/mcp/Dockerfile.pin -t honeymcp:uhbs-lab docs/conformance/latest/results-5.0.1/honeymcp/mcp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/honeymcp/mcp/Dockerfile -t honeymcp:uhbs-lab .local/labs/honeymcp
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t honeymcp:uhbs-lab .local/labs/honeymcp
docker rm -f uhbs-target-honeymcp-mcp 2>/dev/null || true
mkdir -p .local/labs/honeymcp-telemetry && touch .local/labs/honeymcp-telemetry/egress-gateway.log
docker run -d --name uhbs-target-honeymcp-mcp --label uhbs.unit=honeymcp-mcp --network uhbs-lab --network-alias honeymcp-lab -p 0.0.0.0:8080:8080 -v "$PWD/.local/labs/honeymcp-telemetry:/telemetry:rw" honeymcp:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

