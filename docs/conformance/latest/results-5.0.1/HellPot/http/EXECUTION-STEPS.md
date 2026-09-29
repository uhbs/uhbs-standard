# Execution steps — `HellPot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `HellPot-http`
- benchmark: `HellPot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/yunginnanet/HellPot.git`
- branch/commit: `main` / `0ba62c99ea4599ec32474e4982a8ea4d4105c471`
- latest path: `docs/conformance/latest/results-5.0.1/HellPot/http`
- strategy: `ubuntu-wrapper` · base: `ubuntu:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/HellPot/http/Dockerfile.pin -t hellpot:uhbs-lab docs/conformance/latest/results-5.0.1/HellPot/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/HellPot/http/Dockerfile -t hellpot:uhbs-lab .local/labs/HellPot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/HellPot/Dockerfile.lab .local/labs/HellPot/Dockerfile.lab
cp -f docs/conformance/labs/HellPot/docker_config.toml .local/labs/HellPot/docker_config.toml
docker build -f .local/labs/HellPot/Dockerfile.lab -t hellpot:uhbs-lab .local/labs/HellPot
docker rm -f HellPot-lab 2>/dev/null || true
mkdir -p .local/labs/HellPot-telemetry && touch .local/labs/HellPot-telemetry/egress-gateway.log
docker run -d --name HellPot-lab --label uhbs.unit=HellPot-http --network uhbs-lab --network-alias HellPot-lab -p 0.0.0.0:18180:8080 -v "$PWD/.local/labs/HellPot-telemetry:/telemetry:rw" hellpot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

