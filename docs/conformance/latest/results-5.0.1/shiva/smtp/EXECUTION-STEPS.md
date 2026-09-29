# Execution steps — `shiva-smtp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `shiva-smtp`
- benchmark: `shiva` · protocol: `smtp` · class: `Low-Interaction`
- upstream: `https://github.com/shiva-spampot/shiva.git`
- branch/commit: `main` / `6197cd3f7751688a29ec44e6dcef9ff8647e9e15`
- latest path: `docs/conformance/latest/results-5.0.1/shiva/smtp`
- strategy: `upstream-dockerfile` · base: `ubuntu:20.04`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/shiva/smtp/Dockerfile.pin -t shiva-receiver:uhbs-lab docs/conformance/latest/results-5.0.1/shiva/smtp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/shiva/smtp/Dockerfile -t shiva-receiver:uhbs-lab .local/labs/shiva
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t shiva-receiver:uhbs-lab -f .local/labs/shiva/receiver/src/Dockerfile .local/labs/shiva/receiver/src
docker build -t shiva-receiver:uhbs-lab -f .local/labs/shiva/receiver/src/Dockerfile .local/labs/shiva/receiver/src
mkdir -p .local/labs/shiva/data/mails
docker rm -f shiva-lab 2>/dev/null || true
docker run -d --name shiva-lab --network uhbs-lab --network-alias shiva-lab -v "$PWD/.local/labs/shiva/data/mails:/tmp/spam_queue" -e QUEUE_DIR=/tmp/spam_queue/ -e SHIVA_HOST=0.0.0.0 -e SHIVA_PORT=2525 shiva-receiver:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

