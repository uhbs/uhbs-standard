# Tutorial: grade heralding with UHBS (results-5.0.1)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/johnnykv/heralding](https://github.com/johnnykv/heralding) · `master` @ `ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0`  
**Refreshed:** ftp, smtp, ssh

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.1 .
docker build -f Dockerfile.full -t uhbs:5.0.1-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/johnnykv/heralding.git .local/labs/heralding
```

## 2. Start the lab container

See [`ftp/EXECUTION-STEPS.md`](ftp/EXECUTION-STEPS.md), [`smtp/EXECUTION-STEPS.md`](smtp/EXECUTION-STEPS.md), [`ssh/EXECUTION-STEPS.md`](ssh/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`ftp/EXECUTION-STEPS.md`](ftp/EXECUTION-STEPS.md), [`smtp/EXECUTION-STEPS.md`](smtp/EXECUTION-STEPS.md), [`ssh/EXECUTION-STEPS.md`](ssh/EXECUTION-STEPS.md).

**Published (results-5.0.1):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
