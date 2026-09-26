# Tutorial: grade honeypot-ftp with UHBS (results-5.0.0)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/alexbredo/honeypot-ftp](https://github.com/alexbredo/honeypot-ftp) · `master` @ `c7b7cbed4c52d3d84b62676dd1a359c6d9da2696`  
**Refreshed:** ftp

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.0 .
docker build -f Dockerfile.full -t uhbs:5.0.0-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/alexbredo/honeypot-ftp.git .local/labs/honeypot-ftp
```

## 2. Start the lab container

See [`ftp/EXECUTION-STEPS.md`](ftp/EXECUTION-STEPS.md) for the exact `docker run` used (unique `uhbs-target-<unit_id>` names, inventory DNS aliases, no host `-p`).

## 3. Per-protocol quick + full

Exact commands: [`ftp/EXECUTION-STEPS.md`](ftp/EXECUTION-STEPS.md).

**Published (results-5.0.0):** UHQS null / ungraded under `uhqs-v5.0-critical-gate-diagnostic`.
