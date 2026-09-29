# Execution steps — `kippo-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `kippo-ssh`
- benchmark: `kippo` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/desaster/kippo.git`
- branch/commit: `master` / `b9eb06a2830d4bf94702a97ff31da38115ef990b`
- latest path: `docs/conformance/latest/results-5.0.1/kippo/ssh`
- strategy: `upstream-dockerfile` · base: `alpine:3.15`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/kippo/ssh/Dockerfile.pin -t kippo:uhbs-lab docs/conformance/latest/results-5.0.1/kippo/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/kippo/ssh/Dockerfile -t kippo:uhbs-lab .local/labs/kippo
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/kippo/Dockerfile.lab -t kippo:uhbs-lab .local/labs/kippo
docker build -f .local/labs/kippo/Dockerfile.lab -t kippo:uhbs-lab .local/labs/kippo
docker rm -f kippo-lab 2>/dev/null || true
docker run -d --name kippo-lab --network uhbs-lab --network-alias kippo-lab kippo:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

