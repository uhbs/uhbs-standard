# Execution steps — `miniprint-pjl`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `miniprint-pjl`
- benchmark: `miniprint` · protocol: `pjl` · class: `Low-Interaction`
- upstream: `https://github.com/sa7mon/miniprint.git`
- branch/commit: `master` / `494d2fc75b94c19345c2db55d03b5cf74f75e3c2`
- latest path: `docs/conformance/latest/results-5.0.1/miniprint`
- strategy: `upstream-docker` · base: `miniprint:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/miniprint/Dockerfile.pin -t miniprint:uhbs-lab docs/conformance/latest/results-5.0.1/miniprint

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/miniprint/Dockerfile -t miniprint:uhbs-lab .local/labs/miniprint
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t miniprint:uhbs-lab .local/labs/miniprint
docker rm -f uhbs-target-miniprint-pjl 2>/dev/null || true
mkdir -p .local/labs/miniprint-telemetry && touch .local/labs/miniprint-telemetry/egress-gateway.log
docker run -d --name uhbs-target-miniprint-pjl --label uhbs.unit=miniprint-pjl --network uhbs-lab --network-alias miniprint-lab -p 0.0.0.0:9100:9100 -v "$PWD/.local/labs/miniprint-telemetry:/telemetry:rw" miniprint:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

