# Tutorial: grade Cowrie with UHBS (results-5.0.1)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/cowrie/cowrie](https://github.com/cowrie/cowrie) · `main` @ `fef0d620962e23194a9d34a048488f9c76c85835`  
**Refreshed:** ssh, telnet

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.1 .
docker build -f Dockerfile.full -t uhbs:5.0.1-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/cowrie/cowrie.git .local/labs/cowrie
```

## 2. Start the lab container

See [`ssh/EXECUTION-STEPS.md`](ssh/EXECUTION-STEPS.md), [`telnet/EXECUTION-STEPS.md`](telnet/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`ssh/EXECUTION-STEPS.md`](ssh/EXECUTION-STEPS.md), [`telnet/EXECUTION-STEPS.md`](telnet/EXECUTION-STEPS.md).

**Published (results-5.0.1):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
