# Execution steps — `opencanary-mysql`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `opencanary-mysql`
- benchmark: `opencanary` · protocol: `mysql` · class: `Low-Interaction`
- upstream: `https://github.com/thinkst/opencanary.git`
- branch/commit: `master` / `fb12e4fefbdb1b9acd1e5561a2614f827ab639ff`
- latest path: `docs/conformance/latest/results-5.0.1/opencanary/mysql`
- strategy: `upstream-docker` · base: `thinkst/opencanary:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/opencanary/mysql/Dockerfile.pin -t thinkst/opencanary:latest docs/conformance/latest/results-5.0.1/opencanary/mysql

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/opencanary/mysql/Dockerfile -t thinkst/opencanary:latest .local/labs/opencanary
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull thinkst/opencanary:latest
docker rm -f uhbs-target-opencanary-mysql 2>/dev/null || true
mkdir -p .local/labs/opencanary-telemetry && touch .local/labs/opencanary-telemetry/egress-gateway.log
docker run -d --name uhbs-target-opencanary-mysql --label uhbs.unit=opencanary-mysql --network uhbs-lab --network-alias opencanary-lab -p 0.0.0.0:3306:3306 -v "$PWD/.local/labs/opencanary-telemetry:/telemetry:rw" thinkst/opencanary:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

