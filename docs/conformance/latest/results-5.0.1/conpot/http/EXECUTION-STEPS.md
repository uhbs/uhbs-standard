# Execution steps — `conpot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `conpot-http`
- benchmark: `conpot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/mushorg/conpot.git`
- branch/commit: `main` / `35e2dfeca70c3b7d961843bd08f35529a75eaed2`
- latest path: `docs/conformance/latest/results-5.0.1/conpot/http`
- strategy: `upstream-docker` · base: `conpot:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/conpot/http/Dockerfile.pin -t conpot:uhbs-lab docs/conformance/latest/results-5.0.1/conpot/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/conpot/http/Dockerfile -t conpot:uhbs-lab .local/labs/conpot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/conpot/Dockerfile.lab .local/labs/conpot/Dockerfile.lab
docker build -f .local/labs/conpot/Dockerfile.lab -t conpot:uhbs-lab .local/labs/conpot
docker rm -f uhbs-target-conpot-http 2>/dev/null || true
mkdir -p .local/labs/conpot-telemetry && touch .local/labs/conpot-telemetry/egress-gateway.log
docker run -d --name uhbs-target-conpot-http --label uhbs.unit=conpot-http --network uhbs-lab --network-alias conpot-lab -p 0.0.0.0:80:80 -v "$PWD/.local/labs/conpot-telemetry:/telemetry:rw" conpot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

