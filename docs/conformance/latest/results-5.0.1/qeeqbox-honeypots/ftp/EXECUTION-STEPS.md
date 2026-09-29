# Execution steps — `qeeqbox-honeypots-ftp`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `qeeqbox-honeypots-ftp`
- benchmark: `qeeqbox-honeypots` · protocol: `ftp` · class: `Low-Interaction`
- upstream: `https://github.com/qeeqbox/honeypots.git`
- branch/commit: `main` / `f337a32e3351e2add3a455a3bcaf1f02ded5744b`
- latest path: `docs/conformance/latest/results-5.0.1/qeeqbox-honeypots/ftp`
- strategy: `upstream-docker` · base: `qeeqbox-honeypots:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/qeeqbox-honeypots/ftp/Dockerfile.pin -t qeeqbox-honeypots:uhbs-lab docs/conformance/latest/results-5.0.1/qeeqbox-honeypots/ftp

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/qeeqbox-honeypots/ftp/Dockerfile -t qeeqbox-honeypots:uhbs-lab .local/labs/qeeqbox-honeypots
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t qeeqbox-honeypots:uhbs-lab .local/labs/qeeqbox-honeypots
docker rm -f uhbs-target-qeeqbox-honeypots-ftp 2>/dev/null || true
mkdir -p .local/labs/qeeqbox-honeypots-telemetry && touch .local/labs/qeeqbox-honeypots-telemetry/egress-gateway.log
docker run -d --name uhbs-target-qeeqbox-honeypots-ftp --label uhbs.unit=qeeqbox-honeypots-ftp --network uhbs-lab --network-alias qeeqbox-lab -p 0.0.0.0:19021:19021 -v "$PWD/.local/labs/qeeqbox-honeypots-telemetry:/telemetry:rw" qeeqbox-honeypots:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

