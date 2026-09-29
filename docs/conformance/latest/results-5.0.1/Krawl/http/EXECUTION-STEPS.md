# Execution steps — `Krawl-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `Krawl-http`
- benchmark: `Krawl` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/BlessedRebuS/Krawl.git`
- branch/commit: `main` / `ee5080f05832249342758e3b14273c56e8b72ad7`
- latest path: `docs/conformance/latest/results-5.0.1/Krawl/http`
- strategy: `upstream-image` · base: `ghcr.io/blessedrebus/krawl:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/Krawl/http/Dockerfile.pin -t ghcr.io/blessedrebus/krawl:latest docs/conformance/latest/results-5.0.1/Krawl/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/Krawl/http/Dockerfile -t ghcr.io/blessedrebus/krawl:latest .local/labs/Krawl
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull ghcr.io/blessedrebus/krawl:latest
docker pull ghcr.io/blessedrebus/krawl:latest
docker rm -f Krawl-lab 2>/dev/null || true
docker run -d --name Krawl-lab --network uhbs-lab --network-alias Krawl-lab -v "$PWD/.local/labs/Krawl/config.yaml:/app/config.yaml:ro" -v "$PWD/.local/labs/Krawl/wordlists.json:/app/wordlists.json:ro" ghcr.io/blessedrebus/krawl:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

