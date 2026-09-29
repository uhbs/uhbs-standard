# Execution steps — `pghoney-postgres`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `pghoney-postgres`
- benchmark: `pghoney` · protocol: `postgres` · class: `Low-Interaction`
- upstream: `https://github.com/betheroot/pghoney.git`
- branch/commit: `master` / `f5d367f749f7e9353421aaf44dad856df490c441`
- latest path: `docs/conformance/latest/results-5.0.1/pghoney/postgres`
- strategy: `upstream-docker` · base: `pghoney:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/pghoney/postgres/Dockerfile.pin -t pghoney:uhbs-lab docs/conformance/latest/results-5.0.1/pghoney/postgres

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/pghoney/postgres/Dockerfile -t pghoney:uhbs-lab .local/labs/pghoney
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/pghoney/Dockerfile.lab .local/labs/pghoney/Dockerfile.lab
docker build -f .local/labs/pghoney/Dockerfile.lab -t pghoney:uhbs-lab .local/labs/pghoney
docker rm -f uhbs-target-pghoney-postgres 2>/dev/null || true
mkdir -p .local/labs/pghoney-telemetry && touch .local/labs/pghoney-telemetry/egress-gateway.log
docker run -d --name uhbs-target-pghoney-postgres --label uhbs.unit=pghoney-postgres --network uhbs-lab --network-alias pghoney-lab -p 0.0.0.0:5432:5432 -v "$PWD/.local/labs/pghoney-telemetry:/telemetry:rw" pghoney:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

