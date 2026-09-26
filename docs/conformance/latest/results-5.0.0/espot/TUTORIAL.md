# Tutorial: grade ESPot with UHBS (quick + full)

**Status:** Informative · evaluation proof  
**Audience:** Researchers reproducing the results-5.0.0 ESPot pack  
**Outputs:** [`quick/`](quick/README.md) · [`full/`](full/README.md) · [METHODOLOGY.md](METHODOLOGY.md) · [EXECUTION-STEPS.md](EXECUTION-STEPS.md)

Product name = proof label only. Exact command sequence: [EXECUTION-STEPS.md](EXECUTION-STEPS.md).

---

## 0. Prerequisites

Docker, git, `asciinema`, grader images `uhbs:5.0.0` and `uhbs:5.0.0-full`, network `uhbs-lab`.

## 1. Clone HEAD

```bash
GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/mycert/ESPot.git .local/labs/espot
git -C .local/labs/espot rev-parse HEAD
# results-5.0.0 used: 0b126a7783da69d543239606df59211c5d21f1db (master)
```

Reviewed: `README.md` (Node v0.10.x), `package.json`, `config.js-sample`. No upstream Dockerfile.

## 2. Runtime (custom-base, not Ubuntu latest)

Upstream requires Node 0.10 / Express 3. `ubuntu:latest` cannot provide that toolchain; `sqlite3@2` fails on modern Node. Lab wrapper uses `node:10-buster-slim` and disables SQLite in `config.js`.

```bash
docker build -t espot:lab .local/labs/espot
docker network create uhbs-lab 2>/dev/null || true
docker run -d --name uhbs-target-espot-http --network uhbs-lab \
  --network-alias espot-lab -p 127.0.0.1:9200:9200 espot:lab
curl -sS http://127.0.0.1:9200/
```

## 3. Quick (`uhbs:5.0.0`)

```bash
UHBS_QUICK=1 UHBS_AIRGAP_ATTESTED=1 docker run --rm --network uhbs-lab \
  -v "$PWD:/work" -v "$PWD/.local/labs/espot:/honeypot:ro" -w /work \
  -e UHBS_QUICK=1 -e UHBS_AIRGAP_ATTESTED=1 \
  uhbs:5.0.0 lab \
    --inventory /work/docs/conformance/labs/espot/inventory.yaml \
    --target espot --tps /work/docs/conformance/labs/espot/web_api_quick.yaml \
    --quick --skip-sast-tools \
    --out /work/docs/conformance/latest/results-5.0.0/espot/quick
```

**Published quick result (UHBS 5.0.0):** INCOMPLETE / ungraded — see [`quick/SCORECARD.txt`](quick/SCORECARD.txt).

## 4–5. Telemetry + full (`uhbs:5.0.0-full`)

Seed Express `access.log`, write `egress-gateway.log`, then:

```bash
asciinema rec --overwrite docs/conformance/latest/results-5.0.0/espot/full/proof/full-run.cast \
  -c .local/benchmark-refresh/espot-full.sh
```

**Published full result (UHBS 5.0.0):** INCOMPLETE / ungraded — see [`full/SCORECARD.txt`](full/SCORECARD.txt). Module A still flags illegal `HTTP/9.9` → 200. Modules C and D stay incomplete under v5 declared-format / non-SSH gateway evidence rules. Archived 4.x letter grades are **not** reused.

## 6. Verify

```bash
uhbs validate-scorecard docs/conformance/fixtures/espot-web-api.scorecard.json --strict
python scripts/validate_unit.py --unit-id espot-http
```

Back to [ESPot hub](index.md).
