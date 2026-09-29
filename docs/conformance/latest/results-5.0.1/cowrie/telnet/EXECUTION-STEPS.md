# Execution steps — `cowrie-telnet`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `cowrie-telnet`
- benchmark: `cowrie` · protocol: `telnet` · class: `Low-Interaction`
- upstream: `https://github.com/cowrie/cowrie.git`
- branch/commit: `main` / `fef0d620962e23194a9d34a048488f9c76c85835`
- latest path: `docs/conformance/latest/results-5.0.1/cowrie/telnet`
- strategy: `upstream-docker` · base: `cowrie/cowrie:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/cowrie/telnet/Dockerfile.pin -t cowrie/cowrie:latest docs/conformance/latest/results-5.0.1/cowrie/telnet

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/cowrie/telnet/Dockerfile -t cowrie/cowrie:latest .local/labs/cowrie
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull cowrie/cowrie:latest
docker rm -f uhbs-target-cowrie-telnet 2>/dev/null || true
mkdir -p .local/labs/cowrie-telemetry && touch .local/labs/cowrie-telemetry/egress-gateway.log
docker run -d --name uhbs-target-cowrie-telnet --label uhbs.unit=cowrie-telnet --network uhbs-lab --network-alias cowrie-lab -p 0.0.0.0:2223:2223 -v "$PWD/.local/labs/cowrie-telemetry:/telemetry:rw" cowrie/cowrie:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

