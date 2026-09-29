# Execution steps — `Log4Pot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `Log4Pot-http`
- benchmark: `Log4Pot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/thomaspatzke/Log4Pot.git`
- branch/commit: `master` / `5002b1fe0f82359ef32dbc3a899e8a701dc3256e`
- latest path: `docs/conformance/latest/results-5.0.1/Log4Pot/http`
- strategy: `ubuntu-wrapper` · base: `ubuntu:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/Log4Pot/http/Dockerfile.pin -t log4pot:uhbs-lab docs/conformance/latest/results-5.0.1/Log4Pot/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/Log4Pot/http/Dockerfile -t log4pot:uhbs-lab .local/labs/Log4Pot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/Log4Pot/Dockerfile.lab .local/labs/Log4Pot/Dockerfile.lab
docker build -f .local/labs/Log4Pot/Dockerfile.lab -t log4pot:uhbs-lab .local/labs/Log4Pot
docker rm -f Log4Pot-lab 2>/dev/null || true
mkdir -p .local/labs/Log4Pot-telemetry && touch .local/labs/Log4Pot-telemetry/egress-gateway.log
docker run -d --name Log4Pot-lab --label uhbs.unit=Log4Pot-http --network uhbs-lab --network-alias Log4Pot-lab -p 0.0.0.0:18083:8080 -v "$PWD/.local/labs/Log4Pot-telemetry:/telemetry:rw" log4pot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

