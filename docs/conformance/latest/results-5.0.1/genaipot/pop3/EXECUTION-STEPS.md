# Execution steps — `genaipot-pop3`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `genaipot-pop3`
- benchmark: `genaipot` · protocol: `pop3` · class: `Low-Interaction`
- upstream: `https://github.com/ls1911/GenAIPot.git`
- branch/commit: `main` / `205ffe40008f2e76e0decdb01bc19bf8e00acd8a`
- latest path: `docs/conformance/latest/results-5.0.1/genaipot/pop3`
- strategy: `upstream-docker` · base: `annls/genaipot:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/genaipot/pop3/Dockerfile.pin -t annls/genaipot:latest docs/conformance/latest/results-5.0.1/genaipot/pop3

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/genaipot/pop3/Dockerfile -t annls/genaipot:latest .local/labs/genaipot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull annls/genaipot:latest
docker rm -f uhbs-target-genaipot-pop3 2>/dev/null || true
mkdir -p .local/labs/genaipot-telemetry && touch .local/labs/genaipot-telemetry/egress-gateway.log
docker run -d --name uhbs-target-genaipot-pop3 --label uhbs.unit=genaipot-pop3 --network uhbs-lab --network-alias genaipot-lab -p 0.0.0.0:110:110 -v "$PWD/.local/labs/genaipot-telemetry:/telemetry:rw" annls/genaipot:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

