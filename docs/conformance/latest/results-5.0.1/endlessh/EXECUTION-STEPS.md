# Execution steps — `endlessh-ssh_tarpit`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `endlessh-ssh_tarpit`
- benchmark: `endlessh` · protocol: `ssh_tarpit` · class: `Low-Interaction`
- upstream: `https://github.com/skeeto/endlessh.git`
- branch/commit: `master` / `dfe44eb2c5b6fc3c48a39ed826fe0e4459cdf6ef`
- latest path: `docs/conformance/latest/results-5.0.1/endlessh`
- strategy: `upstream-docker` · base: `endlessh:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/endlessh/Dockerfile.pin -t endlessh:uhbs-lab docs/conformance/latest/results-5.0.1/endlessh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/endlessh/Dockerfile -t endlessh:uhbs-lab .local/labs/endlessh
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t endlessh:uhbs-lab .local/labs/endlessh
docker rm -f uhbs-target-endlessh-ssh_tarpit 2>/dev/null || true
mkdir -p .local/labs/endlessh-telemetry && touch .local/labs/endlessh-telemetry/egress-gateway.log
docker run -d --name uhbs-target-endlessh-ssh_tarpit --label uhbs.unit=endlessh-ssh_tarpit --network uhbs-lab --network-alias endlessh-lab -p 0.0.0.0:2222:2222 -v "$PWD/.local/labs/endlessh-telemetry:/telemetry:rw" endlessh:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

