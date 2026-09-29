# Execution steps — `heralding-pop3`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `heralding-pop3`
- benchmark: `heralding` · protocol: `pop3` · class: `Low-Interaction`
- upstream: `https://github.com/johnnykv/heralding.git`
- branch/commit: `master` / `ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0`
- latest path: `docs/conformance/latest/results-5.0.1/heralding/pop3`
- strategy: `upstream-docker` · base: `heralding:uhbs-lab`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/heralding/pop3/Dockerfile.pin -t heralding:uhbs-lab docs/conformance/latest/results-5.0.1/heralding/pop3

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/heralding/pop3/Dockerfile -t heralding:uhbs-lab .local/labs/heralding
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
cp -f docs/conformance/labs/heralding/Dockerfile.lab .local/labs/heralding/Dockerfile.lab
docker build -f .local/labs/heralding/Dockerfile.lab -t heralding:uhbs-lab .local/labs/heralding
docker rm -f uhbs-target-heralding-pop3 2>/dev/null || true
mkdir -p .local/labs/heralding-telemetry && touch .local/labs/heralding-telemetry/egress-gateway.log
docker run -d --name uhbs-target-heralding-pop3 --label uhbs.unit=heralding-pop3 --network uhbs-lab --network-alias heralding-lab -p 0.0.0.0:110:110 -v "$PWD/.local/labs/heralding-telemetry:/telemetry:rw" heralding:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

