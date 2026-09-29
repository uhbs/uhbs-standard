# Tutorial: grade HoneyMCP with UHBS (results-5.0.1)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/kosiorkosa47/honeymcp](https://github.com/kosiorkosa47/honeymcp) · `main` @ `966bb908d140809957ba01e05132631c514ade5d`  
**Refreshed:** mcp

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.1 .
docker build -f Dockerfile.full -t uhbs:5.0.1-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/kosiorkosa47/honeymcp.git .local/labs/honeymcp
```

## 2. Start the lab container

See [`mcp/EXECUTION-STEPS.md`](mcp/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`mcp/EXECUTION-STEPS.md`](mcp/EXECUTION-STEPS.md).

**Published (results-5.0.1):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
