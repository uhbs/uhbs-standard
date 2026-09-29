# Execution steps — `pyrdp-rdp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `pyrdp-rdp`
- benchmark: `pyrdp` · protocol: `rdp` · class: `Low-Interaction`
- upstream: `https://github.com/GoSecure/pyrdp.git`
- branch/commit: `main` / `b610809260778cf1bfb15ad3c6493bd318dbb508`
- latest path: `docs/conformance/latest/results-5.0.1/pyrdp/rdp`
- strategy: `upstream-dockerfile` · base: `ubuntu:22.04`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/pyrdp/rdp/Dockerfile.pin -t pyrdp:uhbs-lab docs/conformance/latest/results-5.0.1/pyrdp/rdp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/pyrdp/rdp/Dockerfile -t pyrdp:uhbs-lab .local/labs/pyrdp
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/pyrdp/Dockerfile.lab -t pyrdp:uhbs-lab .local/labs/pyrdp
docker build -f .local/labs/pyrdp/Dockerfile.lab -t pyrdp:uhbs-lab .local/labs/pyrdp
docker rm -f pyrdp-lab 2>/dev/null || true
docker run -d --name pyrdp-lab --network uhbs-lab --network-alias pyrdp-lab pyrdp:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

