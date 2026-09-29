# Execution steps — `ssh-honeypotd-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `ssh-honeypotd-ssh`
- benchmark: `ssh-honeypotd` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/sjinks/ssh-honeypotd.git`
- branch/commit: `master` / `080d43e81f152e26f8e441741e34b36df505c1e7`
- latest path: `docs/conformance/latest/results-5.0.1/ssh-honeypotd/ssh`
- strategy: `upstream-image` · base: `wildwildangel/ssh-honeypotd:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/ssh-honeypotd/ssh/Dockerfile.pin -t wildwildangel/ssh-honeypotd:latest docs/conformance/latest/results-5.0.1/ssh-honeypotd/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/ssh-honeypotd/ssh/Dockerfile -t wildwildangel/ssh-honeypotd:latest .local/labs/ssh-honeypotd
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull wildwildangel/ssh-honeypotd:latest
docker pull wildwildangel/ssh-honeypotd:latest
docker rm -f ssh-honeypotd-lab 2>/dev/null || true
docker run -d --name ssh-honeypotd-lab --network uhbs-lab --network-alias ssh-honeypotd-lab -e ADDRESS=0.0.0.0 -e PORT=22 wildwildangel/ssh-honeypotd:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

