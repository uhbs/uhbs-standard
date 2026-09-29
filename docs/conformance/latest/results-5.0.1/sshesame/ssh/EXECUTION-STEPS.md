# Execution steps — `sshesame-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `sshesame-ssh`
- benchmark: `sshesame` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/jaksi/sshesame.git`
- branch/commit: `master` / `062795684a859d36a06979e39498c476dcd66970`
- latest path: `docs/conformance/latest/results-5.0.1/sshesame/ssh`
- strategy: `upstream-image` · base: `ghcr.io/jaksi/sshesame:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/sshesame/ssh/Dockerfile.pin -t ghcr.io/jaksi/sshesame:latest docs/conformance/latest/results-5.0.1/sshesame/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/sshesame/ssh/Dockerfile -t ghcr.io/jaksi/sshesame:latest .local/labs/sshesame
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull ghcr.io/jaksi/sshesame:latest
docker pull ghcr.io/jaksi/sshesame:latest
mkdir -p .local/labs/sshesame-telemetry
docker rm -f sshesame-lab 2>/dev/null || true
docker run -d --name sshesame-lab --network uhbs-lab --network-alias sshesame-lab -v "$PWD/.local/labs/sshesame-telemetry:/data" ghcr.io/jaksi/sshesame:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

