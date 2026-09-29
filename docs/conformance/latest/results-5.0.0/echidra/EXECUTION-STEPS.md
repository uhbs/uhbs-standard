# Execution steps — `echidra-ssh`

Replication log for the UHBS 5.0.1 results-5.0.1 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `echidra-ssh`
- benchmark: `echidra` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/Qyleron/EchidraOSS.git`
- default branch: `main`
- commit: `50305356ffe49a20459b89b071dc30bb2598e88b`
- latest path: `docs/conformance/latest/results-5.0.1/echidra`
- lab credentials: `root` / `admin` (inventory)

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/Qyleron/EchidraOSS.git .local/labs/echidra
git -C .local/labs/echidra rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/echidra rev-parse HEAD                # 50305356ffe49a20459b89b071dc30bb2598e88b
```

Docs reviewed: `README.md` (native `echidra start` and Docker Compose), `Dockerfile` (`FROM python:3.11-slim`), `docker-compose.yml`, `SECURITY.md`.

## 2. Runtime

Strategy `upstream-docker`. Upstream documents Docker Compose as Method B. Base image is `python:3.11-slim`, not `ubuntu:latest`. Lab overlay joins `uhbs-lab`, names the honeypot `echidra-lab`, and drops `/etc/localtime` + `/etc/timezone` binds that fail on macOS.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
cat > .local/labs/echidra/.env <<'EOF'
ECHIDRA_DB_PASSWORD=uhbs_lab_db_pass
ECHIDRA_INGEST_API_KEY=uhbs_lab_ingest_key_not_for_prod
ECHIDRA_SESSION_SECRET=uhbs_lab_session_secret_not_for_prod
ECHIDRA_ALERT_SECRET=uhbs_lab_alert_secret_not_for_prod
ECHIDRA_ALLOW_SIGNUPS=false
ECHIDRA_COOKIE_SECURE=false
ECHIDRA_PERSONA=generic_linux
EOF
cat > .local/labs/echidra/docker-compose.uhbs-lab.yml <<'EOF'
services:
  honeypot:
    container_name: echidra-lab
    volumes: !override
      - echidra_logs:/app/logs
      - echidra_ssh_host_key:/app/data
    networks:
      - default
      - uhbs-lab
  api:
    volumes: !override
      - echidra_logs:/app/logs
networks:
  uhbs-lab:
    external: true
    name: uhbs-lab
EOF
docker volume create echidra-uhbs_echidra_ssh_host_key
docker run --rm -v echidra-uhbs_echidra_ssh_host_key:/data alpine chown -R 1000:1000 /data
docker compose -p echidra-uhbs \
  -f .local/labs/echidra/docker-compose.yml \
  -f .local/labs/echidra/docker-compose.uhbs-lab.yml \
  --project-directory .local/labs/echidra \
  up -d --build
# wait until logs contain: SSH server listening on 0.0.0.0:2222
```

SSH `known_hosts` (RejectPolicy — required for Module B/D sessions):

```bash
mkdir -p .local/labs/echidra-telemetry
docker run --rm --network uhbs-lab alpine:3.20 sh -c \
  'apk add --no-cache openssh-client >/dev/null && ssh-keyscan -T 8 -p 2222 echidra-lab' \
  > .local/labs/echidra-telemetry/known_hosts
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/echidra-telemetry/egress-gateway.log
```

## 4. Quick (`uhbs:5.0.1`)

```bash
UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/echidra:/honeypot:ro" \
  -v "$PWD/.local/labs/echidra-telemetry:/telemetry:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_SSH_KNOWN_HOSTS=/work/.local/labs/echidra-telemetry/known_hosts \
  uhbs:5.0.1 lab \
    --inventory /work/docs/conformance/labs/echidra/inventory.yaml \
    --target echidra \
    --tps /work/docs/conformance/labs/echidra/low_interaction_ssh_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.1/echidra/quick
```

Quick is **INCOMPLETE** (SAST skipped → Module F). Do not treat it as the published grade.

## 5. Full + asciinema (`uhbs:5.0.1-full`)

Copy compose logs / `sessions.jsonl` into `.local/labs/echidra-telemetry/` then:

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.1/echidra/full/proof/full-run.cast \
  -c .local/benchmark-refresh/echidra-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/echidra-low-interaction.scorecard.json --strict
python scripts/validate_unit.py --unit-id echidra-ssh
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.1 full outcome: **COMPLETE / GATE_PASSED / UHQS 36.58 / F**. Do not copy archived 4.x 43.45 as the current result.
