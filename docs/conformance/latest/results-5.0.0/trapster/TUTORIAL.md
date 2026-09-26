# Tutorial: grade Trapster Community with UHBS (results-5.0.0)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/0xBallpoint/trapster-community](https://github.com/0xBallpoint/trapster-community) · `main` @ `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`  
**Refreshed so far:** SSH `:2222`, HTTP `:8080`, FTP `:2121`, Telnet `:2323` (all INCOMPLETE / ungraded under UHBS 5.0.0)

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.0 .
docker build -f Dockerfile.full -t uhbs:5.0.0-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 \
  https://github.com/0xBallpoint/trapster-community.git .local/labs/trapster
```

Reviewed: `README.md`, `Dockerfile`, `docker-compose.yml`.

## 2. Start the lab container

Upstream Dockerfile (`FROM python:3.11-slim`) is the documented path.

```bash
docker build -t trapster:uhbs-lab .local/labs/trapster
docker run -d \
  --name uhbs-target-trapster \
  --network uhbs-lab \
  --network-alias trapster-lab \
  -v "$PWD/docs/conformance/labs/trapster/trapster.conf:/etc/trapster/trapster.conf:ro" \
  -v "$PWD/.local/labs/trapster-telemetry:/telemetry:rw" \
  trapster:uhbs-lab
```

Wait for SSH `:2222` after first-boot host-key generation.

## 3. Per-protocol quick + full

Exact commands for SSH: [`ssh/EXECUTION-STEPS.md`](ssh/EXECUTION-STEPS.md). HTTP: [`http/EXECUTION-STEPS.md`](http/EXECUTION-STEPS.md). FTP: [`ftp/EXECUTION-STEPS.md`](ftp/EXECUTION-STEPS.md). Telnet: [`telnet/EXECUTION-STEPS.md`](telnet/EXECUTION-STEPS.md).

**Published (results-5.0.0):** all four protocols **ungraded / INCOMPLETE**. Archived 4.x letter grades are not current.
