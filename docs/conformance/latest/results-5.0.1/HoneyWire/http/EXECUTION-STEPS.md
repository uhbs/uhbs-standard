# Execution steps — `HoneyWire-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `HoneyWire-http`
- benchmark: `HoneyWire` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/andreicscs/HoneyWire.git`
- branch/commit: `main` / `53f2a4946740170ddecfe90ae31f3ac24e83efb4`
- latest path: `docs/conformance/latest/results-5.0.1/HoneyWire/http`
- strategy: `upstream-image` · base: `ghcr.io/andreicscs/honeywire-webrouterdecoy:latest`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/HoneyWire/http/Dockerfile.pin -t ghcr.io/andreicscs/honeywire-webrouterdecoy:latest docs/conformance/latest/results-5.0.1/HoneyWire/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/HoneyWire/http/Dockerfile -t ghcr.io/andreicscs/honeywire-webrouterdecoy:latest .local/labs/HoneyWire
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker pull ghcr.io/andreicscs/honeywire-webrouterdecoy:latest
docker pull ghcr.io/andreicscs/honeywire-webrouterdecoy:latest
docker rm -f honeywire-webdecoy 2>/dev/null || true
docker run -d --name honeywire-webdecoy --network uhbs-lab --network-alias honeywire-webdecoy -e HW_BIND_PORT=8081 -e HW_ROUTER_BRAND=Netgear -e HW_HUB_ENDPOINT=http://127.0.0.1:9 -e HW_HUB_KEY=lab -e HW_SENSOR_ID=hw-sensor-web-router-decoy ghcr.io/andreicscs/honeywire-webrouterdecoy:latest
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

