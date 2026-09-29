# Execution steps — `cowrie-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `cowrie-ssh`
- benchmark: `cowrie` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/cowrie/cowrie.git`
- branch/commit: `main` / `fef0d620962e23194a9d34a048488f9c76c85835`
- latest path: `docs/conformance/latest/results-5.0.1/cowrie/ssh`
- strategy: `upstream-docker` · base: `gcr.io/distroless/python3-debian13`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/cowrie/ssh/Dockerfile.pin -t cowrie/cowrie:latest docs/conformance/latest/results-5.0.1/cowrie/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/cowrie/ssh/Dockerfile -t cowrie/cowrie:latest .local/labs/cowrie
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull cowrie/cowrie:latest
docker rm -f uhbs-target-cowrie-ssh 2>/dev/null || true
mkdir -p .local/labs/cowrie-telemetry && touch .local/labs/cowrie-telemetry/egress-gateway.log
docker run -d --name uhbs-target-cowrie-ssh --label uhbs.unit=cowrie-ssh --network uhbs-lab --network-alias cowrie-lab -p 0.0.0.0:2222:2222 -p 0.0.0.0:2223:2223 -e COWRIE_TELNET_ENABLED=yes -v "$PWD/docs/conformance/labs/cowrie/cowrie.cfg:/cowrie/cowrie-git/etc/cowrie.cfg:ro" -v "$PWD/.local/labs/cowrie-telemetry:/cowrie/cowrie-git/var/log/cowrie" -v "$PWD/.local/labs/cowrie-telemetry:/telemetry:rw" cowrie/cowrie:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

