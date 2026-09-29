# Execution steps — `dionaea-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `dionaea-http`
- benchmark: `dionaea` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/dinotools/dionaea.git`
- branch/commit: `master` / `4e459f1b672a5b4c1e8335c0bff1b93738019215`
- latest path: `docs/conformance/latest/results-5.0.1/dionaea/http`
- strategy: `upstream-docker` · base: `dinotools/dionaea:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/dionaea/http/Dockerfile.pin -t dinotools/dionaea:latest docs/conformance/latest/results-5.0.1/dionaea/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/dionaea/http/Dockerfile -t dinotools/dionaea:latest .local/labs/dionaea
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull dinotools/dionaea:latest
docker rm -f uhbs-target-dionaea-http 2>/dev/null || true
mkdir -p .local/labs/dionaea-telemetry && touch .local/labs/dionaea-telemetry/egress-gateway.log
docker run -d --name uhbs-target-dionaea-http --label uhbs.unit=dionaea-http --network uhbs-lab --network-alias dionaea-lab -p 0.0.0.0:80:80 -v "$PWD/.local/labs/dionaea-telemetry:/telemetry:rw" dinotools/dionaea:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

