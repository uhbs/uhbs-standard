# Execution steps — `honeyagents-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `honeyagents-ssh`
- benchmark: `honeyagents` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/mrwadams/honeyagents.git`
- branch/commit: `main` / `43d4114fe8b235c1646571f7bc50bacc7a32533a`
- latest path: `docs/conformance/latest/results-5.0.1/honeyagents/ssh`
- strategy: `upstream-image` · base: `cowrie/cowrie:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/honeyagents/ssh/Dockerfile.pin -t cowrie/cowrie:latest docs/conformance/latest/results-5.0.1/honeyagents/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/honeyagents/ssh/Dockerfile -t cowrie/cowrie:latest .local/labs/honeyagents
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull cowrie/cowrie:latest
docker pull cowrie/cowrie:latest
docker rm -f honeyagents-honeypot 2>/dev/null || true
docker run -d --name honeyagents-honeypot --network uhbs-lab --network-alias honeyagents-honeypot cowrie/cowrie:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

