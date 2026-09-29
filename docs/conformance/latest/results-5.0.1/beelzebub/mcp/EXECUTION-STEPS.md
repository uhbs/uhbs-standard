# Execution steps — `beelzebub-mcp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `beelzebub-mcp`
- benchmark: `beelzebub` · protocol: `mcp` · class: `Web-API`
- upstream: `https://github.com/beelzebub-labs/beelzebub.git`
- branch/commit: `main` / `67d5632a754f39f7b14c703d3009193150440116`
- latest path: `docs/conformance/latest/results-5.0.1/beelzebub/mcp`
- strategy: `upstream-docker` · base: `beelzebub:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/beelzebub/mcp/Dockerfile.pin -t beelzebub:uhbs-lab docs/conformance/latest/results-5.0.1/beelzebub/mcp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/beelzebub/mcp/Dockerfile -t beelzebub:uhbs-lab .local/labs/beelzebub
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t beelzebub:uhbs-lab .local/labs/beelzebub
docker rm -f uhbs-target-beelzebub-mcp 2>/dev/null || true
mkdir -p .local/labs/beelzebub-telemetry && touch .local/labs/beelzebub-telemetry/egress-gateway.log
docker run -d --name uhbs-target-beelzebub-mcp --label uhbs.unit=beelzebub-mcp --network uhbs-lab --network-alias beelzebub-lab -p 0.0.0.0:8000:8000 -v "$PWD/.local/labs/beelzebub-telemetry:/telemetry:rw" beelzebub:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

