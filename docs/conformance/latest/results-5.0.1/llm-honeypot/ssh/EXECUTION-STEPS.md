# Execution steps — `llm-honeypot-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `llm-honeypot-ssh`
- benchmark: `llm-honeypot` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/PalisadeResearch/llm-honeypot.git`
- branch/commit: `main` / `156004a1b122f201448635417ee47bd44d7f28ca`
- latest path: `docs/conformance/latest/results-5.0.1/llm-honeypot/ssh`
- strategy: `upstream-image` · base: `cowrie/cowrie:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/llm-honeypot/ssh/Dockerfile.pin -t cowrie/cowrie:latest docs/conformance/latest/results-5.0.1/llm-honeypot/ssh

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/llm-honeypot/ssh/Dockerfile -t cowrie/cowrie:latest .local/labs/llm-honeypot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull cowrie/cowrie:latest
docker pull cowrie/cowrie:latest
docker rm -f llm-honeypot-lab 2>/dev/null || true
docker run -d --name llm-honeypot-lab --network uhbs-lab --network-alias llm-honeypot-lab cowrie/cowrie:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

