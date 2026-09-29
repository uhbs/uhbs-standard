# Execution steps — `honeypot-ftp-ftp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `honeypot-ftp-ftp`
- benchmark: `honeypot-ftp` · protocol: `ftp` · class: `Low-Interaction`
- upstream: `https://github.com/alexbredo/honeypot-ftp.git`
- branch/commit: `master` / `c7b7cbed4c52d3d84b62676dd1a359c6d9da2696`
- latest path: `docs/conformance/latest/results-5.0.1/honeypot-ftp/ftp`
- strategy: `upstream-docker` · base: `honeypot-ftp:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/honeypot-ftp/ftp/Dockerfile.pin -t honeypot-ftp:uhbs-lab docs/conformance/latest/results-5.0.1/honeypot-ftp/ftp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/honeypot-ftp/ftp/Dockerfile -t honeypot-ftp:uhbs-lab .local/labs/honeypot-ftp
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/honeypot-ftp/Dockerfile.lab .local/labs/honeypot-ftp/Dockerfile.lab
docker build -f .local/labs/honeypot-ftp/Dockerfile.lab -t honeypot-ftp:uhbs-lab .local/labs/honeypot-ftp
docker rm -f uhbs-target-honeypot-ftp-ftp 2>/dev/null || true
mkdir -p .local/labs/honeypot-ftp-telemetry && touch .local/labs/honeypot-ftp-telemetry/egress-gateway.log
docker run -d --name uhbs-target-honeypot-ftp-ftp --label uhbs.unit=honeypot-ftp-ftp --network uhbs-lab --network-alias honeypot-ftp-lab -p 0.0.0.0:21:21 -v "$PWD/.local/labs/honeypot-ftp-telemetry:/telemetry:rw" honeypot-ftp:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

