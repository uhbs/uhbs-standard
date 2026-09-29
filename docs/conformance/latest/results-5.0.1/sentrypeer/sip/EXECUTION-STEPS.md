# Execution steps — `sentrypeer-sip`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `sentrypeer-sip`
- benchmark: `sentrypeer` · protocol: `sip` · class: `Low-Interaction`
- upstream: `https://github.com/SentryPeer/SentryPeer.git`
- branch/commit: `main` / `0340440ef96767cf7ad0f43cf972b2162c327de3`
- latest path: `docs/conformance/latest/results-5.0.1/sentrypeer/sip`
- strategy: `upstream-image` · base: `sentrypeer/sentrypeer:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/sentrypeer/sip/Dockerfile.pin -t sentrypeer/sentrypeer:latest docs/conformance/latest/results-5.0.1/sentrypeer/sip

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/sentrypeer/sip/Dockerfile -t sentrypeer/sentrypeer:latest .local/labs/sentrypeer
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull sentrypeer/sentrypeer:latest
docker pull sentrypeer/sentrypeer:latest
docker rm -f sentrypeer-lab 2>/dev/null || true
docker run -d --name sentrypeer-lab --network uhbs-lab --network-alias sentrypeer-lab sentrypeer/sentrypeer:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

