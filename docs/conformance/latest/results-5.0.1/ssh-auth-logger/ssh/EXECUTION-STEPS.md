# Execution steps — `ssh-auth-logger-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `ssh-auth-logger-ssh`
- benchmark: `ssh-auth-logger` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/JustinAzoff/ssh-auth-logger.git`
- branch/commit: `master` / `f53dddcb78d9ce46ecd9eada499435ccce2bfc2f`
- latest path: `docs/conformance/latest/results-5.0.1/ssh-auth-logger/ssh`
- strategy: `upstream-image` · base: `justinazoff/ssh-auth-logger:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/ssh-auth-logger/ssh/Dockerfile.pin -t justinazoff/ssh-auth-logger:latest docs/conformance/latest/results-5.0.1/ssh-auth-logger/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/ssh-auth-logger/ssh/Dockerfile -t justinazoff/ssh-auth-logger:latest .local/labs/ssh-auth-logger
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull justinazoff/ssh-auth-logger:latest
docker pull justinazoff/ssh-auth-logger:latest
docker rm -f ssh-auth-logger-lab 2>/dev/null || true
docker run -d --name ssh-auth-logger-lab --network uhbs-lab --network-alias ssh-auth-logger-lab -e SSHD_BIND=:2222 -e SSHD_RATE=5000000 -e SSHD_RSA_BITS=2048 justinazoff/ssh-auth-logger:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

