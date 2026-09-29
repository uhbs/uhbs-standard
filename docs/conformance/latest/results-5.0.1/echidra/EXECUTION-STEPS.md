# Execution steps — `echidra-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `echidra-ssh`
- benchmark: `echidra` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/Qyleron/EchidraOSS.git`
- branch/commit: `main` / `50305356ffe49a20459b89b071dc30bb2598e88b`
- latest path: `docs/conformance/latest/results-5.0.1/echidra`
- strategy: `upstream-docker` · base: `echidra:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/echidra/Dockerfile.pin -t echidra:uhbs-lab docs/conformance/latest/results-5.0.1/echidra

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/echidra/Dockerfile -t echidra:uhbs-lab .local/labs/echidra
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t echidra:uhbs-lab .local/labs/echidra
docker rm -f uhbs-target-echidra-ssh 2>/dev/null || true
mkdir -p .local/labs/echidra-telemetry && touch .local/labs/echidra-telemetry/egress-gateway.log
docker run -d --name uhbs-target-echidra-ssh --label uhbs.unit=echidra-ssh --network uhbs-lab --network-alias echidra-lab -p 0.0.0.0:2222:2222 -v "$PWD/.local/labs/echidra-telemetry:/telemetry:rw" echidra:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

