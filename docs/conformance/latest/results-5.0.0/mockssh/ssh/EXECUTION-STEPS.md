# Execution steps — `mockssh-ssh`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `mockssh-ssh`
- benchmark: `mockssh` · protocol: `ssh` · class: `Low-Interaction`
- upstream: `https://github.com/ncouture/MockSSH.git`
- default branch: `main`
- commit: `d2d49b6121544818560ce8e56f306ccf75f961b3`
- latest path: `docs/conformance/latest/results-5.0.0/mockssh/ssh`
- lab credentials: `testadmin` / `x`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/ncouture/MockSSH.git .local/labs/mockssh
git -C .local/labs/mockssh rev-parse --abbrev-ref HEAD   # main
git -C .local/labs/mockssh rev-parse HEAD                # d2d49b6121544818560ce8e56f306ccf75f961b3
```

Docs reviewed: `README.md` (Python 3.12+, no Docker), `examples/mock_cisco.py` (binds `127.0.0.1:9999`), `pyproject.toml`.

## 2. Runtime

Strategy `ubuntu-wrapper`. No upstream Dockerfile. Ubuntu 24.04 + `pip install -e .`. Lab entry `docs/conformance/labs/mockssh/lab_cisco.py` listens on `0.0.0.0:2222`.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
cp docs/conformance/labs/mockssh/lab_cisco.py .local/labs/mockssh/lab_cisco.py
docker build -f docs/conformance/labs/mockssh/Dockerfile.lab -t mockssh:uhbs-lab .local/labs/mockssh
docker run -d --name uhbs-target-mockssh-ssh --network uhbs-lab --network-alias mockssh-lab mockssh:uhbs-lab
mkdir -p .local/labs/mockssh-telemetry
docker run --rm --network uhbs-lab alpine:3.20 sh -c \
  'apk add --no-cache openssh-client >/dev/null && ssh-keyscan -T 8 -p 2222 mockssh-lab' \
  > .local/labs/mockssh-telemetry/known_hosts
printf '%s\n' '# UHBS egress gateway canary — no HIT lines means clean' \
  > .local/labs/mockssh-telemetry/egress-gateway.log
```

## 4. Quick (`uhbs:5.0.0`)

```bash
UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/mockssh:/honeypot:ro" \
  -v "$PWD/.local/labs/mockssh-telemetry:/telemetry:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  -e UHBS_SSH_KNOWN_HOSTS=/work/.local/labs/mockssh-telemetry/known_hosts \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/mockssh/inventory.yaml \
    --target mockssh-ssh \
    --tps /work/docs/conformance/labs/mockssh/low_interaction_ssh_quick.yaml \
    --phases profile,static,sandbox,dynamic,score --modules A,B,C,D,E,F \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.0/mockssh/ssh/quick
```

## 5. Full + asciinema (`uhbs:5.0.0-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.0/mockssh/ssh/full/proof/full-run.cast \
  -c .local/benchmark-refresh/mockssh-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/mockssh-low-interaction.scorecard.json --strict
python scripts/validate_unit.py --unit-id mockssh-ssh
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.0 full outcome: **COMPLETE / GATE_PASSED / UHQS 41.75 / F**. Do not copy archived 4.x 59.0 / D.
