# Execution steps — `trapster-rdp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `trapster-rdp`
- benchmark: `trapster` · protocol: `rdp` · class: `Low-Interaction`
- upstream: `https://github.com/0xBallpoint/trapster-community.git`
- branch/commit: `main` / `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`
- latest path: `docs/conformance/latest/results-5.0.1/trapster/rdp`
- strategy: `upstream-docker` · base: `trapster:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/trapster/rdp/Dockerfile.pin -t trapster:uhbs-lab docs/conformance/latest/results-5.0.1/trapster/rdp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/trapster/rdp/Dockerfile -t trapster:uhbs-lab .local/labs/trapster
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t trapster:uhbs-lab .local/labs/trapster
docker rm -f uhbs-target-trapster-rdp 2>/dev/null || true
mkdir -p .local/labs/trapster-telemetry && touch .local/labs/trapster-telemetry/egress-gateway.log
docker run -d --name uhbs-target-trapster-rdp --label uhbs.unit=trapster-rdp --network uhbs-lab --network-alias trapster-lab -p 0.0.0.0:3389:3389 -v "$PWD/.local/labs/trapster-telemetry:/telemetry:rw" trapster:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

