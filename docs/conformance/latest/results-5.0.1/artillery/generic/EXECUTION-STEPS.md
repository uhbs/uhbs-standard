# Execution steps — `artillery-generic`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `artillery-generic`
- benchmark: `artillery` · protocol: `generic` · class: `Low-Interaction`
- upstream: `https://github.com/BinaryDefense/artillery.git`
- branch/commit: `master` / `805a5d858bf1cc3f6de5c3a5083b2d0d21136ebb`
- latest path: `docs/conformance/latest/results-5.0.1/artillery/generic`
- strategy: `lab-dockerfile` · base: `python:3.11-slim-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/artillery/generic/Dockerfile.pin -t artillery:uhbs-lab docs/conformance/latest/results-5.0.1/artillery/generic

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/artillery/generic/Dockerfile -t artillery:uhbs-lab .local/labs/artillery
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/artillery/Dockerfile.lab -t artillery:uhbs-lab .local/labs/artillery
docker build -f .local/labs/artillery/Dockerfile.lab -t artillery:uhbs-lab .local/labs/artillery
docker rm -f artillery-lab 2>/dev/null || true
docker run -d --name artillery-lab --network uhbs-lab --network-alias artillery-lab artillery:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

