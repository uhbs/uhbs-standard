# Execution steps — `mailoney-smtp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `mailoney-smtp`
- benchmark: `mailoney` · protocol: `smtp` · class: `Low-Interaction`
- upstream: `https://github.com/phin3has/mailoney.git`
- branch/commit: `main` / `b8310a7019dd0ba00c666e5185bee3c1dd851e19`
- latest path: `docs/conformance/latest/results-5.0.1/mailoney/smtp`
- strategy: `upstream-docker` · base: `mailoney:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/mailoney/smtp/Dockerfile.pin -t mailoney:uhbs-lab docs/conformance/latest/results-5.0.1/mailoney/smtp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/mailoney/smtp/Dockerfile -t mailoney:uhbs-lab .local/labs/mailoney
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t mailoney:uhbs-lab .local/labs/mailoney
docker rm -f uhbs-target-mailoney-smtp 2>/dev/null || true
mkdir -p .local/labs/mailoney-telemetry && touch .local/labs/mailoney-telemetry/egress-gateway.log
docker run -d --name uhbs-target-mailoney-smtp --label uhbs.unit=mailoney-smtp --network uhbs-lab --network-alias mailoney-lab -p 0.0.0.0:25:25 -v "$PWD/.local/labs/mailoney-telemetry:/telemetry:rw" mailoney:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

