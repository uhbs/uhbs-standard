# Execution steps — `nosqlpot-redis`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `nosqlpot-redis`
- benchmark: `nosqlpot` · protocol: `redis` · class: `Low-Interaction`
- upstream: `https://github.com/torque59/nosqlpot.git`
- branch/commit: `master` / `225ab5ab3e9d47bbdbe4153573c2eba56c5426ac`
- latest path: `docs/conformance/latest/results-5.0.1/nosqlpot/redis`
- strategy: `lab-dockerfile` · base: `python:3.11-slim-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/nosqlpot/redis/Dockerfile.pin -t nosqlpot:uhbs-lab docs/conformance/latest/results-5.0.1/nosqlpot/redis

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/nosqlpot/redis/Dockerfile -t nosqlpot:uhbs-lab .local/labs/nosqlpot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/nosqlpot/Dockerfile.lab -t nosqlpot:uhbs-lab .local/labs/nosqlpot
docker build -f .local/labs/nosqlpot/Dockerfile.lab -t nosqlpot:uhbs-lab .local/labs/nosqlpot
docker rm -f nosqlpot-lab 2>/dev/null || true
docker run -d --name nosqlpot-lab --network uhbs-lab --network-alias nosqlpot-lab nosqlpot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

