# Execution steps — `owasp-python-honeypot-http`

Replication log for the UHBS 5.0.1 results-5.0.1 Spot dual-vantage refresh.

## Identity

- unit_id: `owasp-python-honeypot-http`
- benchmark: `owasp-python-honeypot` · protocol: `http` · class: `Web-API`
- upstream: `https://github.com/OWASP/Python-Honeypot.git`
- branch/commit: `master` / `5482fdcc0b828a5d3acf354910843b907e92032a`
- latest path: `docs/conformance/latest/results-5.0.1/owasp-python-honeypot/http`
- strategy: `lab-dockerfile` · base: `python:3.11-slim-bookworm`
- vantage: on-box Module C/D (Spot A) + remote Module A/B (Spot B)

## Exact image (score Dockerfile)

The graded target image is pinned by [`Dockerfile`](Dockerfile) (build recipe) and
[`Dockerfile.pin`](Dockerfile.pin) (`FROM sha256:…` exact digest) in this unit directory
(plus any companions under `image/` / `docker_config.toml`).

```bash
# Exact graded image (no rebuild):
docker build -f docs/conformance/latest/results-5.0.1/owasp-python-honeypot/http/Dockerfile.pin -t owasp-python-honeypot:uhbs-lab docs/conformance/latest/results-5.0.1/owasp-python-honeypot/http

# Or rebuild from the lab recipe + cloned upstream:
docker build -f docs/conformance/latest/results-5.0.1/owasp-python-honeypot/http/Dockerfile -t owasp-python-honeypot:uhbs-lab .local/labs/owasp-python-honeypot
```

## Build and start (Spot A)

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -f .local/labs/owasp-python-honeypot/Dockerfile.lab -t owasp-python-honeypot:uhbs-lab .local/labs/owasp-python-honeypot
docker build -f .local/labs/owasp-python-honeypot/Dockerfile.lab -t owasp-python-honeypot:uhbs-lab .local/labs/owasp-python-honeypot
docker rm -f owasp-python-honeypot-lab 2>/dev/null || true
docker run -d --name owasp-python-honeypot-lab --network uhbs-lab --network-alias owasp-python-honeypot-lab owasp-python-honeypot:uhbs-lab
```

## Grade

See `quick/uhbs-run.log` and `full/uhbs-run.log`. Full cast: `full/proof/full-run.cast`.

