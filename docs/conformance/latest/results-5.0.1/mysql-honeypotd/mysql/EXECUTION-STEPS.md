# Execution steps — `mysql-honeypotd-mysql`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `mysql-honeypotd-mysql`
- benchmark: `mysql-honeypotd` · protocol: `mysql` · class: `Low-Interaction`
- upstream: `https://github.com/sjinks/mysql-honeypotd.git`
- branch/commit: `master` / `955ecce4ce22c8588da1f023dfd790099755d575`
- latest path: `docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql`
- strategy: `upstream-docker` · base: `mysql-honeypotd:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/Dockerfile.pin -t mysql-honeypotd:uhbs-lab docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/mysql-honeypotd/mysql/Dockerfile -t mysql-honeypotd:uhbs-lab .local/labs/mysql-honeypotd
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t mysql-honeypotd:uhbs-lab .local/labs/mysql-honeypotd
docker rm -f uhbs-target-mysql-honeypotd-mysql 2>/dev/null || true
mkdir -p .local/labs/mysql-honeypotd-telemetry && touch .local/labs/mysql-honeypotd-telemetry/egress-gateway.log
docker run -d --name uhbs-target-mysql-honeypotd-mysql --label uhbs.unit=mysql-honeypotd-mysql --network uhbs-lab --network-alias mysql-honeypotd-lab -p 0.0.0.0:3306:3306 -v "$PWD/.local/labs/mysql-honeypotd-telemetry:/telemetry:rw" mysql-honeypotd:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

