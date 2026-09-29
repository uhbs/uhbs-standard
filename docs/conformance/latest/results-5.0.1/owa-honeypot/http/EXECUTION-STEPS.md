# Execution steps — `owa-honeypot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `owa-honeypot-http`
- benchmark: `owa-honeypot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/joda32/owa-honeypot.git`
- branch/commit: `master` / `17d7166c3dc319e6acd9eb7343e9fa9eef225562`
- latest path: `docs/conformance/latest/results-5.0.1/owa-honeypot/http`
- strategy: `lab-dockerfile` · base: `python:3.11-slim-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/owa-honeypot/http/Dockerfile.pin -t owa-honeypot:uhbs-lab docs/conformance/latest/results-5.0.1/owa-honeypot/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/owa-honeypot/http/Dockerfile -t owa-honeypot:uhbs-lab .local/labs/owa-honeypot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/owa-honeypot/Dockerfile.lab -t owa-honeypot:uhbs-lab .local/labs/owa-honeypot
docker build -f .local/labs/owa-honeypot/Dockerfile.lab -t owa-honeypot:uhbs-lab .local/labs/owa-honeypot
docker rm -f owa-honeypot-lab 2>/dev/null || true
docker run -d --name owa-honeypot-lab --network uhbs-lab --network-alias owa-honeypot-lab owa-honeypot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

