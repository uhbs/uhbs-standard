# Execution steps — `honeytrap-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `honeytrap-ssh`
- benchmark: `honeytrap` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/honeytrap/honeytrap.git`
- branch/commit: `master` / `05965fc67deab17b48e43873abc5f509067ef098`
- latest path: `docs/conformance/latest/results-5.0.1/honeytrap/ssh`
- strategy: `upstream-dockerfile` · base: `golang:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/honeytrap/ssh/Dockerfile.pin -t honeytrap:uhbs-lab docs/conformance/latest/results-5.0.1/honeytrap/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/honeytrap/ssh/Dockerfile -t honeytrap:uhbs-lab .local/labs/honeytrap
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/honeytrap/Dockerfile.lab -t honeytrap:uhbs-lab .local/labs/honeytrap
docker build -f .local/labs/honeytrap/Dockerfile.lab -t honeytrap:uhbs-lab .local/labs/honeytrap
docker rm -f honeytrap-lab 2>/dev/null || true
docker run -d --name honeytrap-lab --network uhbs-lab --network-alias honeytrap-lab honeytrap:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

