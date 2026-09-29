# Execution steps — `fortigate-vpn-ssl-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `fortigate-vpn-ssl-http`
- benchmark: `fortigate-vpn-ssl` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/PeterGabaldon/Fortigate.VPN-SSL.Honeypot.git`
- branch/commit: `main` / `1fea6014337eff79a684877644ff625782f2315d`
- latest path: `docs/conformance/latest/results-5.0.1/fortigate-vpn-ssl/http`
- strategy: `lab-dockerfile` · base: `python:3.12-slim-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/fortigate-vpn-ssl/http/Dockerfile.pin -t fortigate-vpn-ssl:uhbs-lab docs/conformance/latest/results-5.0.1/fortigate-vpn-ssl/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/fortigate-vpn-ssl/http/Dockerfile -t fortigate-vpn-ssl:uhbs-lab .local/labs/fortigate-vpn-ssl
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/fortigate-vpn-ssl/Dockerfile.lab -t fortigate-vpn-ssl:uhbs-lab .local/labs/fortigate-vpn-ssl
docker build -f .local/labs/fortigate-vpn-ssl/Dockerfile.lab -t fortigate-vpn-ssl:uhbs-lab .local/labs/fortigate-vpn-ssl
docker rm -f fortigate-vpn-ssl-lab 2>/dev/null || true
docker run -d --name fortigate-vpn-ssl-lab --network uhbs-lab --network-alias fortigate-vpn-ssl-lab fortigate-vpn-ssl:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

