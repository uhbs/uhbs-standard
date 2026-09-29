# Execution steps — `sticky_elephant-postgres`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `sticky_elephant-postgres`
- benchmark: `sticky_elephant` · protocol: `postgres` · class: `Low-Interaction`
- upstream: `https://github.com/betheroot/sticky_elephant.git`
- branch/commit: `master` / `59c01aa91b05de07dc37e8547af8222cc3ac1af0`
- latest path: `docs/conformance/latest/results-5.0.1/sticky_elephant/postgres`
- strategy: `lab-dockerfile` · base: `ruby:3.2-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/sticky_elephant/postgres/Dockerfile.pin -t sticky_elephant:uhbs-lab docs/conformance/latest/results-5.0.1/sticky_elephant/postgres

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/sticky_elephant/postgres/Dockerfile -t sticky_elephant:uhbs-lab .local/labs/sticky_elephant
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/sticky_elephant/Dockerfile.lab -t sticky_elephant:uhbs-lab .local/labs/sticky_elephant
docker build -f .local/labs/sticky_elephant/Dockerfile.lab -t sticky_elephant:uhbs-lab .local/labs/sticky_elephant
docker rm -f sticky_elephant-lab 2>/dev/null || true
docker run -d --name sticky_elephant-lab --network uhbs-lab --network-alias sticky_elephant-lab sticky_elephant:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

