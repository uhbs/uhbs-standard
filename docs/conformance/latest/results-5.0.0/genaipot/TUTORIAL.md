# Tutorial: grade GenAIPot with UHBS (results-5.0.1)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/eduardobsg/GenAIPot](https://github.com/eduardobsg/GenAIPot) · `main` @ `205ffe40008f2e76e0decdb01bc19bf8e00acd8a`  
**Refreshed:** smtp, pop3

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.1 .
docker build -f Dockerfile.full -t uhbs:5.0.1-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/eduardobsg/GenAIPot.git .local/labs/genaipot
```

## 2. Start the lab container

See [`smtp/EXECUTION-STEPS.md`](smtp/EXECUTION-STEPS.md), [`pop3/EXECUTION-STEPS.md`](pop3/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`smtp/EXECUTION-STEPS.md`](smtp/EXECUTION-STEPS.md), [`pop3/EXECUTION-STEPS.md`](pop3/EXECUTION-STEPS.md).

**Published (results-5.0.1):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
