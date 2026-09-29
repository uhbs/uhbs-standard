# Tutorial: grade Beelzebub with UHBS (results-5.0.1)

**Status:** Informative · evaluation proof  
**Target:** [https://github.com/beelzebub-labs/beelzebub](https://github.com/beelzebub-labs/beelzebub) · `main` @ `67d5632a754f39f7b14c703d3009193150440116`  
**Refreshed so far:** SSH, TELNET, HTTP, MCP, REDIS (INCOMPLETE / ungraded under UHBS 5.0.1). All five listeners share `uhbs-target-beelzebub`.

## 0. Prerequisites

```bash
docker build -t uhbs:5.0.1 .
docker build -f Dockerfile.full -t uhbs:5.0.1-full .
docker network create uhbs-lab 2>/dev/null || true
```

## 1. Clone source (Module F)

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 \
  https://github.com/beelzebub-labs/beelzebub.git .local/labs/beelzebub
```

Reviewed: `README.md`, `Dockerfile`, `docker-compose.yml`, lab overlay under `docs/conformance/labs/beelzebub/configurations/`.

## 2. Start the lab container

Upstream Dockerfile (`golang:alpine` → `scratch`) is the documented path. Mount the UHBS static service overlay (no LLM keys). `logsPath` is a file.

```bash
docker build -t beelzebub:uhbs-lab .local/labs/beelzebub
docker run -d \
  --name uhbs-target-beelzebub \
  --network uhbs-lab \
  --network-alias beelzebub-lab \
  -v "$PWD/docs/conformance/labs/beelzebub/configurations:/configurations:ro" \
  -v "$PWD/.local/labs/beelzebub-telemetry/beelzebub.log:/logs:rw" \
  -v "$PWD/.local/labs/beelzebub-telemetry:/telemetry:rw" \
  beelzebub:uhbs-lab
```

## 3. Per-protocol quick + full

See each protocol `EXECUTION-STEPS.md`. **Published (results-5.0.1):** completed units **ungraded / INCOMPLETE**. Archived 4.x letter grades are not current.
