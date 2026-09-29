# Execution steps — `portlurker-generic`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `portlurker-generic`
- benchmark: `portlurker` · protocol: `generic` · class: `Low-Interaction`
- upstream: `https://github.com/bartnv/portlurker.git`
- branch/commit: `master` / `001afa93312749222af4a76bbcfd46ea179dea82`
- latest path: `docs/conformance/latest/results-5.0.1/portlurker/generic`
- strategy: `upstream-dockerfile` · base: `debian:bullseye-slim`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/portlurker/generic/Dockerfile.pin -t portlurker:uhbs-lab docs/conformance/latest/results-5.0.1/portlurker/generic

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/portlurker/generic/Dockerfile -t portlurker:uhbs-lab .local/labs/portlurker
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/portlurker/Dockerfile.lab -t portlurker:uhbs-lab .local/labs/portlurker
docker build -f .local/labs/portlurker/Dockerfile.lab -t portlurker:uhbs-lab .local/labs/portlurker
docker rm -f portlurker-lab 2>/dev/null || true
docker run -d --name portlurker-lab --network uhbs-lab --network-alias portlurker-lab portlurker:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

