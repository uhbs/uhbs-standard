# Execution steps — `mockssh-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `mockssh-ssh`
- benchmark: `mockssh` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/ncouture/MockSSH.git`
- branch/commit: `main` / `d2d49b6121544818560ce8e56f306ccf75f961b3`
- latest path: `docs/conformance/latest/results-5.0.1/mockssh/ssh`
- strategy: `upstream-docker` · base: `mockssh:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/mockssh/ssh/Dockerfile.pin -t mockssh:uhbs-lab docs/conformance/latest/results-5.0.1/mockssh/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/mockssh/ssh/Dockerfile -t mockssh:uhbs-lab .local/labs/mockssh
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/mockssh/Dockerfile.lab .local/labs/mockssh/Dockerfile.lab
docker build -f .local/labs/mockssh/Dockerfile.lab -t mockssh:uhbs-lab .local/labs/mockssh
docker rm -f uhbs-target-mockssh-ssh 2>/dev/null || true
mkdir -p .local/labs/mockssh-telemetry && touch .local/labs/mockssh-telemetry/egress-gateway.log
docker run -d --name uhbs-target-mockssh-ssh --label uhbs.unit=mockssh-ssh --network uhbs-lab --network-alias mockssh-lab -p 0.0.0.0:2222:2222 -v "$PWD/.local/labs/mockssh-telemetry:/telemetry:rw" mockssh:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

