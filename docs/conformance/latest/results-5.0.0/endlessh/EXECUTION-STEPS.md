# Execution steps — `endlessh-ssh_tarpit`

Replication log for the UHBS 5.0.0 results-5.0.0 refresh. Commands ran from the UHBS repo root.

## Identity

- unit_id: `endlessh-ssh_tarpit`
- benchmark: `endlessh` · protocol: `ssh_tarpit` · class: `Low-Interaction`
- upstream: `https://github.com/skeeto/endlessh.git`
- default branch: `master`
- commit: `dfe44eb2c5b6fc3c48a39ed826fe0e4459cdf6ef`
- latest path: `docs/conformance/latest/results-5.0.0/endlessh`

## 1. Clone

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/skeeto/endlessh.git .local/labs/endlessh
git -C .local/labs/endlessh rev-parse --abbrev-ref HEAD
git -C .local/labs/endlessh rev-parse HEAD
```

Docs reviewed: README.md, Dockerfile, Makefile.

## 2. Runtime

Strategy `upstream-docker` · base `alpine:3.9`. Upstream Dockerfile pins alpine:3.9 for the C builder/runtime; Ubuntu latest is not the documented image.

## 3. Build and start

```bash
docker network create uhbs-lab 2>/dev/null || true
docker build -t endlessh:lab .local/labs/endlessh
docker run -d --name uhbs-target-endlessh-ssh_tarpit --network uhbs-lab --network-alias endlessh-lab endlessh:lab -v -d 200 -p 2222 -l 32 -m 4096
```

## 4. Quick (`uhbs:5.0.0`)

```bash
UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/endlessh:/honeypot:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/endlessh/inventory.yaml \
    --target endlessh \
    --tps /work/docs/conformance/labs/endlessh/low_interaction_quick.yaml \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.0/endlessh/quick
```

Inventory target id may differ from hostname; this refresh used inventory `--target` as recorded in `run-meta.json`.

## 5. Full + asciinema (`uhbs:5.0.0-full`)

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.0/endlessh/full/proof/full-run.cast \
  -c .local/benchmark-refresh/endlessh-full.sh
```

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/endlessh-low-interaction.scorecard.json --strict
python scripts/validate_unit.py --unit-id endlessh-ssh_tarpit
python scripts/rebuild_mkdocs_nav.py
```

Honest UHBS 5.0.0 outcome: **INCOMPLETE / INCOMPLETE** (ungraded unless GATE_PASSED). Do not copy archived 4.x letter grades.
