# Execution steps — `modpot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `modpot-http`
- benchmark: `modpot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/referefref/modpot.git`
- branch/commit: `main` / `3722ce126b74e7bf9897f49fdde610c96eb8103f`
- latest path: `docs/conformance/latest/results-5.0.1/modpot/http`
- strategy: `lab-dockerfile` · base: `golang:1.22-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/modpot/http/Dockerfile.pin -t modpot:uhbs-lab docs/conformance/latest/results-5.0.1/modpot/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/modpot/http/Dockerfile -t modpot:uhbs-lab .local/labs/modpot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/modpot/Dockerfile.lab -t modpot:uhbs-lab .local/labs/modpot
cp docs/conformance/labs/modpot/config.uhbs.yaml .local/labs/modpot/config.uhbs.yaml
docker build -f .local/labs/modpot/Dockerfile.lab -t modpot:uhbs-lab .local/labs/modpot
docker rm -f modpot-lab 2>/dev/null || true
docker run -d --name modpot-lab --network uhbs-lab --network-alias modpot-lab modpot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

