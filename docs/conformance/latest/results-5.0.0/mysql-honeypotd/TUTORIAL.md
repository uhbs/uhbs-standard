# Tutorial: grade mysql-honeypotd with UHBS (results-5.0.0)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/sjinks/mysql-honeypotd](https://github.com/sjinks/mysql-honeypotd) · `master` @ `955ecce4ce22c8588da1f023dfd790099755d575`  
**Refreshed:** mysql

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.0 .
docker build -f Dockerfile.full -t uhbs:5.0.0-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/sjinks/mysql-honeypotd.git .local/labs/mysql-honeypotd
```

## 2. Start the lab container

See [`mysql/EXECUTION-STEPS.md`](mysql/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`mysql/EXECUTION-STEPS.md`](mysql/EXECUTION-STEPS.md).

**Published (results-5.0.0):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
