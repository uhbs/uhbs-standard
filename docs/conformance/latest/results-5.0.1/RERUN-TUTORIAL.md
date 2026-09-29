# RERUN-TUTORIAL — fixing and re-grading the unreachable-target units (results-5.0.1)

**Status:** Operative runbook · **Audience:** operators re-running the 63 broken units
**Related:** [`rerun-runbook.yaml`](rerun-runbook.yaml) · [`scripts/preflight_unit.py`](../../../scripts/preflight_unit.py) · [`scripts/rerun_unit.py`](../../../scripts/rerun_unit.py)

## What broke (30-second version)

The Sep-27 wave graded 135 units, but the wave scripts invoked **only the
grader** — target containers had to be started separately, and for 63 units
they weren't started, had died, or weren't configured for the unit's protocol.
Module A (weight 0.30) scored 0.0 against dead targets, dragging those units
to junk grades (median 8.12, clustered at 1.38–8.12) that measure Docker
plumbing, not the products.

Failure classes across the 63:

| Class | Signature in old `REPORT.txt` | Count | Real cause |
| --- | --- | --- | --- |
| **D** | `[Errno -2] Name or service not known` | 16 | target container absent / wrong `--network-alias` at grade time |
| **P** | `ssh port 2222 closed`, `[Errno 111] refused` | 29 | container up, service not listening (protocol not enabled in product config, broken image, or port mismatch) |
| **U** | `plugins=['snmp'/'sip'/'ntp'/'dns'/'dhcp'/'tftp'/'bacnet']` + FAILED | 15 | UDP datagram service gave no reply (target down **or** probe gets no answer) |
| **C** | `no port mapped for protocol` | 1 | inventory/TPS port wiring (echidra-class) |
| (misc) | `http port 2222 closed` on espot (a 9200 service) | — | grader fell back to default port 2222 — site/port resolution mismatch |

## The two tools (read this once)

| Tool | What it does | When you use it |
| --- | --- | --- |
| `scripts/preflight_unit.py` | Resolves the inventory site **exactly like the grader** (`load_inventory` + `resolve_target` + TPS `apply_tps`), then probes every protocol: TCP connect (the same `_port_open` check Module A's RFC probes use) or a real UDP PDU (DNS query, NTP, SNMP GET, SIP OPTIONS, TFTP RRQ, DHCPDISCOVER, BACnet Who-Is). Classifies failures: `site_missing` / `no_port_mapped` / `dns_error` / `port_closed` / `timeout` / `udp_no_reply`. | Triage — before spending any grade compute |
| `scripts/rerun_unit.py` | Full unit lifecycle: ensure `uhbs-lab` network → verify target image → start target (alias + telemetry mount + config mounts from runbook) → capture `container-inspect` + egress-gateway evidence with sha256 pins → **preflight with retry loop until `--wait` expires** (dead target ⇒ nothing graded, `docker logs` dumped, exit 1) → grade quick + full (asciinema cast) → tear down → `validate_unit.py` → print UHQS. | The actual re-run — always, for every unit |

Unit coordinates (inventory, TPS, alias, port, output paths) come from the
SQLite ledger (`.local/benchmark-refresh/results-5.0.1.sqlite3`,
`benchmark_units` table). The **target launcher** (image + env + mounts +
cmd) comes from [`rerun-runbook.yaml`](rerun-runbook.yaml) — that file is the
fix table: one entry per broken unit with a `status` field.

Runbook `status` values:

| Status | Meaning |
| --- | --- |
| `verified` | Launcher confirmed against a live container (green preflight) |
| `needs-launcher` | Image known/likely; confirm env/mounts before trusting the grade |
| `needs-config` | Product config must enable the protocol (§6 per-product recipes) |
| `needs-investigation` | No known launcher or UDP probe unanswered; triage with `--preflight-only` |

---

## Step-by-step

### Step 0 — Prerequisites (once)

```bash
cd /Users/mz/Projects/uhbs-standard
docker network create uhbs-lab 2>/dev/null || true

# grader images (used by both tools)
docker image inspect uhbs:5.0.1 >/dev/null      && echo quick-grader ok
docker image inspect uhbs:5.0.1-full >/dev/null && echo full-grader ok
# missing? build them: see repo root Dockerfile + AGENTS.md verify block

# per-unit target image (example kippo):
docker image inspect kippo:uhbs-lab >/dev/null || \
  docker build -f .local/labs/kippo/Dockerfile.lab -t kippo:uhbs-lab .local/labs/kippo
```

Run everything with the project venv: `.venv/bin/python`.

### Step 1 — Triage a unit (no grading, seconds)

```bash
# site resolution + full probe, from inside the Docker network:
.venv/bin/python scripts/rerun_unit.py \
  --unit <unit-id> \
  --runbook docs/conformance/latest/results-5.0.1/rerun-runbook.yaml \
  --preflight-only
```

Or probe a target that is already running (e.g. live dionaea):

```bash
docker run --rm --network uhbs-lab -v "$PWD:/work" -w /work \
  --entrypoint python3 uhbs:5.0.1 \
  scripts/preflight_unit.py \
    --inventory docs/conformance/labs/dionaea/inventory.yaml \
    --site dionaea-smb --protocol smb
```

Read the failure **class** and apply the matching fix:

| Preflight class | Fix |
| --- | --- |
| `site_missing` | inventory site id ≠ unit id — the driver resolves protocol/port matches automatically; if it still fails, fix the site key in the inventory or pass `--site` |
| `no_port_mapped` | add `ports: {<proto>: <port>}` under the site in the inventory |
| `dns_error` | target not running / wrong alias → fix the runbook `alias:` (must equal the DB `target_host`) or the `docker run` alias in the driver |
| `port_closed` | service not listening → product config (§6) or image is broken (rebuild) |
| `timeout` | service wedged → `docker logs <container>`, usually a config crash loop |
| `udp_no_reply` | datagram sent, nothing back → verify the protocol is actually enabled; honest predictor that Module A will also get zero |

### Step 2 — Fix the launcher, record it in the runbook

Edit `rerun-runbook.yaml` for the unit: set `image`, `env`, `mounts`, `cmd`
so the target starts **with the unit's protocol enabled and listening on the
inventory port**. Worked example — kippo (verified 2026-09-28):

```yaml
  kippo-ssh:
    benchmark: kippo
    protocol: ssh
    alias: kippo-lab
    port: 2222
    status: verified
    image: kippo:uhbs-lab
    mounts:
      - .local/labs/kippo/kippo.cfg.dist:/app/kippo.cfg:ro  # image's /app/kippo.cfg is a broken dir
      - .local/labs/kippo-data:/app/data:rw                 # image dir not writable by app user
      - .local/labs/kippo-dl:/app/dl:rw
      - .local/labs/kippo-log:/app/log:rw
```

How that fix was found (the general recipe):

1. First run crashed: `NoSectionError: 'honeypot'` → preflight dumped
   `docker logs` → config missing ⇒ mount `kippo.cfg.dist` as `/app/kippo.cfg`.
2. Second run crashed: `Permission denied: data/ssh_host_rsa_key.pub` ⇒ mount
   writable host dirs over `/app/data`, `/app/dl`, `/app/log`.
3. Third run: preflight `port_closed` on attempt 1 (kippo generates RSA keys
   at boot), **PASS on attempt 2** — the retry loop exists exactly for this.
4. Flip `status: verified` only after a green preflight **and** a completed grade.

### Step 3 — Re-run one unit (full lifecycle)

```bash
.venv/bin/python scripts/rerun_unit.py \
  --unit kippo-ssh \
  --runbook docs/conformance/latest/results-5.0.1/rerun-runbook.yaml \
  --modes both            # or quick | full
```

What happens (in order): network → image check → target start → evidence
capture → preflight retries (up to `--wait 60`) → quick grade → full grade
(+ `proof/full-run.cast` if asciinema installed) → teardown →
`validate_unit.py` → UHQS summary. A preflight failure aborts **before any
grading** and prints `docker logs` — that is the feature, not a bug.

Useful flags: `--preflight-only`, `--reuse-target` (target already running),
`--keep-target`, `--publish <host-port>` (debug from localhost), `--no-cast`,
`--concurrency/--requests`, `--no-validate`, `--track` (record the run in the
benchmark SQLite ledger — see Step 7).

### Step 4 — Batch re-run (the 63, in dependency order)

```bash
RUNBOOK=docs/conformance/latest/results-5.0.1/rerun-runbook.yaml
for U in $(grep -E '^  [a-zA-Z0-9_-]+:' "$RUNBOOK" | sed -E 's/^  ([^:]+):.*/\1/'); do
  echo "=== $U"
  .venv/bin/python scripts/rerun_unit.py --unit "$U" --runbook "$RUNBOOK" --modes quick \
    || { echo "PREFLIGHT FAILED: $U — fix launcher, rerun"; continue; }
done
# after the quick smoke pass is green, run full mode for the same units
```

Rules of thumb: run units of one product **sequentially** (they share an
alias), different products may run in parallel (≤4 graders); always smoke
(`--modes quick`) before `full` — quick costs ~1 min, full ~3–5.

### Step 5 — Acceptance gate (per unit, before it counts)

```bash
.venv/bin/python scripts/validate_unit.py --unit-id <unit-id>   # exit 0 = ACCEPT
```

Plus the review-level gates:

- [ ] Module A > 0 in `full/report.json` (no unreachable-target artifacts)
- [ ] Module F > 0 and `static/` present (full runs must ship SAST)
- [ ] Module C either measured or explicitly `INCOMPLETE` with reason
- [ ] `uhbs validate-scorecard <fixture> --strict` on any regenerated fixture

### Step 6 — Per-product launcher recipes (class P/C fixes)

#### 6a. Wire telemetry FIRST — every honeypot logs somewhere (do this for every unit)

Module C is unmeasured for most of the field **only because the labs never
routed the product's logs into the graded sink** — not because products lack
telemetry. Module C needs records in `telemetry_dir` to run its three checks:
C1 parse + declared-format validation, C2 log-injection resilience (marker
payloads sent at the service must appear in the sink), C4 ground-truth
correlation (sent observables must be findable).

The wiring rule — put the runbook's `log_path:` on the product's **native log
directory inside the container**; the driver mounts the telemetry sink there:

```yaml
  cowrie-ssh:
    log_path: /cowrie/cowrie-git/var/log/cowrie   # cowrie.json lands in the sink
```

or ad hoc: `--wire-log /opt/dionaea/var/log/dionaea`.

**Grader-side rule (automatic in `rerun_unit.py` since 2026-09-28):** Module C
reads the inventory's `telemetry_dir` field — 143 sites declare `/telemetry`,
but three declare the product's native path (kippo `/app/log`, artillery
`/var/artillery/logs`, pyrdp `/home/pyrdp/pyrdp_output`). The driver now mounts
the sink into BOTH the target (rw) and the grader (ro) at that declared path.
Before this fix, such units graded Module C as "telemetry_dir missing"
(unmeasured) even with a perfectly wired sink — kippo demonstrated the
transition: `INCOMPLETE (dir missing)` → `FAILED complete=True (0 records —
no JSONL sink)` — an honest measured-zero instead of a harness gap.

Evidence it works: cowrie (wired) measured **800/800 valid native_json
records** for C1; honeymcp 594 records; HellPot 77 records + C2 markers
captured → 78.5. Unwired (shiva, sentrypeer, heralding…) = `0 records`,
`complete=False`, excluded from the composite.

Three honest outcomes once wired:

| Outcome | Meaning | Action |
| --- | --- | --- |
| records + format match + markers/ground-truth | measured, scored | none — that's the goal |
| records exist, format mismatch or markers `[]` | **measured zero** — a real telemetry finding | fix the declared `native_event_format` or the sink's capture fidelity |
| text-only logger, nothing parses | measured zero — telemetry not machine-consumable | enable JSONL output where the product supports it; else accept the honest zero |

Per-product native log paths (verify with `docker logs` / `docker exec ls`):

| Product | Native log path (container) | Structured? |
| --- | --- | --- |
| cowrie | `/cowrie/cowrie-git/var/log/cowrie` (cowrie.json) | ✅ JSONL |
| dionaea | `/opt/dionaea/var/log/dionaea` (enable `json` logging handler in dionaea.conf for log.json) | config-dependent |
| heralding | its configured session log (heralding writes JSONL natively — point its `log_path` config at `/telemetry`) | ✅ JSONL |
| kippo | `/app/log` (kippo.log) | ❌ text → measured-zero |
| opencanary | its configured log file (opencanary.conf `logger` section; JSON if file backend) | config-dependent |
| beelzebub | its configured log sink (per-protocol yaml) | config-dependent |

Also declare the format so C1 validates the right thing:
`native_event_format: native_json` in the inventory/TPS when the product
emits JSONL.

#### 6b. Launcher recipes

| Product (units) | Recipe |
| --- | --- |
| **kippo-ssh** | verified — see §2 worked example |
| **cowrie-ssh / cowrie-telnet** | `cowrie/cowrie:latest`; mount `docs/conformance/labs/cowrie/cowrie.cfg` to the container's etc path (`cowrie-git/etc/cowrie.cfg`), env `COWRIE_TELNET_ENABLED=yes` for telnet, telemetry rw mount to `var/log/cowrie`; grader env needs `UHBS_SSH_KNOWN_HOSTS=docs/conformance/labs/cowrie/known_hosts` |
| **dionaea-*** | stock `dinotools/dionaea:latest` + telemetry rw mount (`/telemetry`); protocol set is baked in the image config — for non-default protocols mount a custom dionaea config enabling them (sip, tftp, mqtt, …). `pptp`/`upnp` currently verified live |
| **opencanary-*** (14) | `opencanary:uhbs-lab`; mount `docs/conformance/labs/opencanary/opencanary.conf` at the container's config path; every unit protocol must be `enabled: true` with the **inventory port** in that conf (ssh 2222, telnet 23, ftp 21, http 80, git 9418, …) — one conf per run; restart target between units |
| **beelzebub-*** (8) | `beelzebub:uhbs-lab`; beelzebub enables protocols via its yaml config — mount a per-protocol config that declares only the unit's protocol handler on the inventory port |
| **qeeqbox-honeypots-*** (19) | `qeeqbox-honeypots:uhbs-lab`; one process per protocol (`cmd: honeypots -p <proto> …`) listening on the inventory's 19xxx port — check the site's `port:` in the inventory and match the container's listen port exactly |
| **trapster-*** (7) | `trapster:uhbs-lab`; per-protocol service config like beelzebub |
| **datatrap-*** (4) | image exists; `.local/labs/datatrap-runtime/<proto>/` holds per-protocol runtime — mount the matching dir |
| **conpot-*** | image exists; conpot selects protocol template via config/mount (`bacnet.json`, `s7comm.json`, `http.json` …) — s7comm also showed `connection refused`: check `docker logs` for a crash |
| **espot** | inventory is correct (`http: 9200`); old failure was the port-2222 fallback — keep site id `espot`, verify preflight resolves `9200` |
| **echidra** | inventory has `ports: {ssh: 2222}`; old `no port mapped` was a run-time wiring bug — preflight with `--resolve-site-only` first; if mapping still fails, align the TPS `protocols` list |
| **endlessh / honeypot-ftp / mysql-honeypotd / Krawl / owa-honeypot / pyrdp** | images exist — `--preflight-only` first; most just need the right startup cmd/env from the upstream README in `.local/labs/<product>/` |

For every **UDP** unit (snmp/sip/ntp/dns/dhcp/tftp/bacnet): after the target
starts, confirm the preflight's protocol PDU actually gets a reply. If the
product legitimately silent-drops the PDU, Module A will also score 0 — file
that as a harness/plugin gap (see `src/uhbs_core/protocols/`), not a target bug.

### Step 7 — After the batch: ledger + docs regeneration

The SQLite ledger and generated docs must reflect the re-run (they currently
don't — the DB holds only bootstrap rows). Easiest: pass `--track` to the
driver and every graded mode is recorded automatically
(`log-run-start` + `log-run-finish`; the latter extracts UHQS/grade/hashes
from the out-dir itself).

Manual equivalents (same CLI the wave used):

```bash
DB=.local/benchmark-refresh/results-5.0.1.sqlite3
.venv/bin/python scripts/tracker.py --db "$DB" log-run-start \
  --unit-id <unit> --mode full --uhbs-version 5.0.1 \
  --grader-image uhbs:5.0.1-full --target-image <image> \
  --telemetry-mode mounted --airgap-attested
.venv/bin/python scripts/tracker.py --db "$DB" log-run-finish \
  --unit-id <unit> --mode full --out-dir docs/conformance/latest/results-5.0.1/<product>/<proto>/full \
  [--cast-path .../proof/full-run.cast]

# then regenerate the ledger + generated docs (do not hand-edit):
.venv/bin/python scripts/tracker.py --db "$DB" sync-ledger     # rewrites RUN-LEDGER.md
# HONEYPOT-SCORE-LIST.md / benchmark-manifest.yaml via generate-manifest +
# the wave generators in .local/benchmark-refresh/ (wave2_publish.py / write_hub_docs.py)

# tests (repo rule: pytest -q + ruff check on touched Python):
ruff check scripts/preflight_unit.py scripts/rerun_unit.py
.venv/bin/python -m pytest -q
```

### Step 8 — Guardrails for future waves

1. **Never grade without preflight.** Use `scripts/rerun_unit.py` for every
   unit — grader-only scripts are how the Sep-27 wave broke.
2. **Preflight is the contract**: it uses the grader's own inventory/TPS
   resolution and port check, so green preflight ⇒ Module A can reach the
   target. A red preflight means fix the launcher, not "run it anyway".
3. One target container per unit (unique alias), started and torn down by the
   driver. No shared "already-running" hub targets.
4. Flip runbook `status:` to `verified` only after green preflight **and** a
   completed grade; the file is the audit trail of what was fixed.
5. UDP units additionally need a PDU reply — silent ≠ reachable for datagram
   services.
6. **Wire telemetry on every launcher** (`log_path:` in the runbook) — an
   unwired sink grades Module C as unmeasured; the product's logs exist by
   design and belong in the graded sink.

## Quick reference

```bash
# triage everything still broken:
for U in $(grep -E '^  [a-zA-Z0-9_-]+:' docs/conformance/latest/results-5.0.1/rerun-runbook.yaml | sed -E 's/^  ([^:]+):.*/\1/'); do
  .venv/bin/python scripts/rerun_unit.py --unit "$U" \
    --runbook docs/conformance/latest/results-5.0.1/rerun-runbook.yaml --preflight-only \
    && echo "READY: $U" || echo "FIX:   $U"
done

# re-run a ready unit end-to-end:
.venv/bin/python scripts/rerun_unit.py --unit <unit-id> \
  --runbook docs/conformance/latest/results-5.0.1/rerun-runbook.yaml --modes both
```
