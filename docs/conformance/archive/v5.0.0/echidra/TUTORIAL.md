# Tutorial: grade EchidraOSS with UHBS (quick + full)

**Status:** Informative · evaluation proof  
**Target:** [Qyleron/EchidraOSS](https://github.com/Qyleron/EchidraOSS) — multi-protocol honeypot; graded on SSH `:2222`  
**Published artifacts:** [`quick/`](quick/) · [`full/`](full/) · trust notes: [METHODOLOGY.md](METHODOLOGY.md)

This is the workflow used to produce the artifacts under
`docs/conformance/reports/echidra/`. Product name = proof label only.

---

## 0. Prerequisites

- Docker Engine or Docker Desktop  
- `git`, Python 3.11+ (optional local `uhbs validate-scorecard`)  

```bash
git clone https://github.com/mziqudhd92/uhbs-standard.git
cd uhbs-standard

docker build -t uhbs:4.0.0 .
docker build -f Dockerfile.full -t uhbs:4.0.0-full .
docker network create uhbs-lab 2>/dev/null || true
```

Confirm:

```bash
docker run --rm uhbs:4.0.0 --version
docker run --rm uhbs:4.0.0 lab --list-protocols
```

---

## 1. Clone EchidraOSS

```bash
mkdir -p .local/labs
git clone --depth 1 https://github.com/Qyleron/EchidraOSS.git .local/labs/EchidraOSS
cd .local/labs/EchidraOSS
git rev-parse HEAD   # published proof used: c16548ba4eb54af0cf9efa2c545d83039b2c1ece
```

---

## 2. Start Echidra with Docker Compose (project instructions)

Create a local `.env` (Compose requires these; lab-only placeholders are fine):

```bash
cat > .env <<'EOF'
ECHIDRA_DB_PASSWORD=uhbs_lab_db_pass
ECHIDRA_INGEST_API_KEY=uhbs_lab_ingest_key_not_for_prod
ECHIDRA_SESSION_SECRET=uhbs_lab_session_secret_not_for_prod
ECHIDRA_ALERT_SECRET=uhbs_lab_alert_secret_not_for_prod
ECHIDRA_ALLOW_SIGNUPS=false
ECHIDRA_COOKIE_SECURE=false
ECHIDRA_PERSONA=generic_linux
EOF
```

UHBS lab overlay (stable hostname `echidra-lab`, join `uhbs-lab`, drop host
timezone binds that break on macOS without `/etc/timezone`):

```bash
cat > docker-compose.uhbs-lab.yml <<'EOF'
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

docker compose -f docker-compose.yml -f docker-compose.uhbs-lab.yml up -d --build
```

If SSH fails with `PermissionError` writing `data/ssh_host_key`, fix volume
ownership once and restart:

```bash
docker run --rm -v echidraoss_echidra_ssh_host_key:/data alpine chown -R 1000:1000 /data
docker restart echidra-lab
```

Smoke-test banner (from the grader network):

```bash
until docker logs echidra-lab 2>&1 | grep -q 'SSH server listening'; do sleep 1; done
docker run --rm --network uhbs-lab python:3.12-slim python3 -c "
import socket
s=socket.create_connection(('echidra-lab',2222),timeout=5)
s.settimeout(3); print(s.recv(128)); s.close()
"
# expect: b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\\r\\n'
```

Return to the UHBS repo root:

```bash
cd /path/to/uhbs-standard
```

---

## 3. Quick run (smoke grade)

Lab assets:

- [`../../labs/echidra/inventory.yaml`](../../labs/echidra/inventory.yaml)  
- [`../../labs/echidra/low_interaction_ssh_quick.yaml`](../../labs/echidra/low_interaction_ssh_quick.yaml)

```bash
mkdir -p docs/conformance/reports/echidra/quick

docker run --rm \
  --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/EchidraOSS:/honeypot:ro" \
  -w /work \
  -e UHBS_QUICK=1 \
  -e UHBS_AIRGAP_ATTESTED=1 \
  -e PYTHONUNBUFFERED=1 \
  uhbs:4.0.0 \
  lab \
    --inventory /work/docs/conformance/labs/echidra/inventory.yaml \
    --target echidra \
    --tps /work/docs/conformance/labs/echidra/low_interaction_ssh_quick.yaml \
    --phases profile,static,sandbox,dynamic,score \
    --modules A,B,C,D,E,F \
    --quick \
    --skip-sast-tools \
    --out /work/docs/conformance/reports/echidra/quick \
    --environment "Quick Docker lab: EchidraOSS SSH :2222 root/admin, UHBS_QUICK=1, SAST skipped"
```

**Published quick result:** UHQS **57.33** · Grade **D** · δ_C **1.0**  
See [`quick/SCORECARD.txt`](quick/SCORECARD.txt).

---

## 4. Seed telemetry for the full run

```bash
mkdir -p .local/labs/EchidraOSS-telemetry

docker run --rm --network uhbs-lab python:3.12-slim bash -c '
pip install -q paramiko >/dev/null
python3 - <<'"'"'PY'"'"'
import paramiko, time
for i in range(15):
    c = paramiko.SSHClient()
    # Seed script only — UHBS harness uses RejectPolicy + UHBS_SSH_KNOWN_HOSTS.
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # noqa: B507 lab seed
    c.connect("echidra-lab", 2222, username="root", password=f"admin{i}",
              timeout=10, allow_agent=False, look_for_keys=False, banner_timeout=10)
    for cmd in ("whoami", "uname -a", "ls /", "id"):
        stdin, stdout, stderr = c.exec_command(cmd, timeout=8)
        stdout.read(); stderr.read()
    c.close()
    time.sleep(0.2)
print("seeded")
PY
'

docker run --rm \
  -v echidraoss_echidra_logs:/logs \
  -v "$PWD/.local/labs/EchidraOSS-telemetry:/out" \
  alpine sh -c 'cp -a /logs/. /out/'
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/EchidraOSS-telemetry/egress-gateway.log
```

---

## 5. Full run (claim-grade Docker lab)

Assets:

- [`../../labs/echidra/low_interaction_ssh_full.yaml`](../../labs/echidra/low_interaction_ssh_full.yaml) — 1000-sample TPS  
- [`../../labs/echidra/inventory.yaml`](../../labs/echidra/inventory.yaml)

```bash
mkdir -p docs/conformance/reports/echidra/full

docker run --rm \
  --network uhbs-lab \
  -v "$PWD:/work" \
  -v "$PWD/.local/labs/EchidraOSS:/honeypot:ro" \
  -v "$PWD/.local/labs/EchidraOSS-telemetry:/telemetry:ro" \
  -w /work \
  -e PYTHONUNBUFFERED=1 \
  -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_EGRESS_GATEWAY_LOG=/telemetry/egress-gateway.log \
  uhbs:4.0.0-full \
  lab \
    --inventory /work/docs/conformance/labs/echidra/inventory.yaml \
    --target echidra \
    --phases profile,static,sandbox,dynamic,score \
    --modules A,B,C,D,E,F \
    --concurrency 10 \
    --requests 50 \
    --out /work/docs/conformance/reports/echidra/full \
    --environment "Full Docker lab: EchidraOSS SSH :2222 + 1000-sample A3 + SAST + telemetry"
```

**Published full result:** UHQS **43.45** · Grade **F** · δ_C **1.0**  
See [`full/SCORECARD.txt`](full/SCORECARD.txt).

After the run, refresh provenance + manifests (see [METHODOLOGY.md](METHODOLOGY.md)).

---

## 6. Verify

```bash
cat docs/conformance/reports/echidra/quick/SCORECARD.txt
cat docs/conformance/reports/echidra/full/SCORECARD.txt
uhbs validate-scorecard docs/conformance/fixtures/echidra-low-interaction.scorecard.json --strict
ls docs/conformance/reports/echidra/full/static/
```

---

## 7. How to read the grade

| Signal | Meaning |
| --- | --- |
| Banner `SSH-2.0-OpenSSH_8.9p1…` | Real asyncssh handshake (not plaintext fake) |
| Module A ≈ 21–23 | Null ID / fidelity gaps dominate |
| Module B = 25 | Cross-session behavioral marker missing |
| Full C = 55 | JSONL logs without STIX/OTel/ECS |
| D = 100 / δ_C = 1.0 | Containment gate cleared |
| Full UHQS 43.45 / F | Below beta Production Baseline (UHQS > 80 + gate) |

For trust-facing narrative, cite **full/** and [METHODOLOGY.md](METHODOLOGY.md).

---

## 8. Cleanup

```bash
cd .local/labs/EchidraOSS
docker compose -f docker-compose.yml -f docker-compose.uhbs-lab.yml down
# optional: docker network rm uhbs-lab
```

Back to [Echidra report hub](index.md) · [all reports](../index.md).
