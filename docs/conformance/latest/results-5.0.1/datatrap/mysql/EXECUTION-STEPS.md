# Execution steps — `datatrap-mysql`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `datatrap-mysql`
- benchmark: `datatrap` · protocol: `mysql` · class: `Low-Interaction`
- upstream: `https://github.com/ThalesGroup/dd-honeypot.git`
- branch/commit: `main` / `c692e8c697647122821f635be2ce362555ce768b`
- latest path: `docs/conformance/latest/results-5.0.1/datatrap/mysql`
- strategy: `upstream-docker` · base: `datatrap:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/datatrap/mysql/Dockerfile.pin -t datatrap:uhbs-lab docs/conformance/latest/results-5.0.1/datatrap/mysql

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/datatrap/mysql/Dockerfile -t datatrap:uhbs-lab .local/labs/datatrap
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t datatrap:uhbs-lab .local/labs/datatrap
docker rm -f uhbs-target-datatrap-mysql 2>/dev/null || true
mkdir -p .local/labs/datatrap-telemetry && touch .local/labs/datatrap-telemetry/egress-gateway.log
docker run -d --name uhbs-target-datatrap-mysql --label uhbs.unit=datatrap-mysql --network uhbs-lab --network-alias datatrap-lab -p 0.0.0.0:3306:3306 -v "$PWD/.local/labs/datatrap-telemetry:/telemetry:rw" datatrap:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

