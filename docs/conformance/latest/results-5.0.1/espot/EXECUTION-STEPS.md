# Execution steps — `espot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `espot-http`
- benchmark: `espot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/mycert/ESPot.git`
- branch/commit: `master` / `0b126a7783da69d543239606df59211c5d21f1db`
- latest path: `docs/conformance/latest/results-5.0.1/espot`
- strategy: `upstream-docker` · base: `espot:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/espot/Dockerfile.pin -t espot:uhbs-lab docs/conformance/latest/results-5.0.1/espot

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/espot/Dockerfile -t espot:uhbs-lab .local/labs/espot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t espot:uhbs-lab .local/labs/espot
docker rm -f uhbs-target-espot-http 2>/dev/null || true
mkdir -p .local/labs/espot-telemetry && touch .local/labs/espot-telemetry/egress-gateway.log
docker run -d --name uhbs-target-espot-http --label uhbs.unit=espot-http --network uhbs-lab --network-alias espot-lab -p 0.0.0.0:9200:9200 -v "$PWD/.local/labs/espot-telemetry:/telemetry:rw" espot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

