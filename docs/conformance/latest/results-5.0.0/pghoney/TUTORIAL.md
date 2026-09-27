# Tutorial: grade pghoney with UHBS (results-5.0.0)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/betheroot/pghoney](https://github.com/betheroot/pghoney) · `master` @ `f5d367f749f7e9353421aaf44dad856df490c441`  
**Refreshed:** postgres

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.0 .
docker build -f Dockerfile.full -t uhbs:5.0.0-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/betheroot/pghoney.git .local/labs/pghoney
```

## 2. Start the lab container

See [`postgres/EXECUTION-STEPS.md`](postgres/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`postgres/EXECUTION-STEPS.md`](postgres/EXECUTION-STEPS.md).

**Published (results-5.0.0):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
