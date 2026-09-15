# EchidraOSS methodology & trust notes

**Status:** Informative · evaluation proof  
**Related:** [TUTORIAL.md](TUTORIAL.md) · [full/run-meta.json](full/run-meta.json) · [quick/run-meta.json](quick/run-meta.json)

---

## 1. Claims / non-claims

| We claim | We do **not** claim |
| --- | --- |
| Artifacts come from UHBS-Lab v4.0.0 against a live Echidra Compose honeypot SSH `:2222` | That Echidra is UHBS-certified |
| Full run used 1000-sample timing, source audit, SAST, and real log directory | That HTTP/FTP/Telnet were graded in this report |
| Manifests include SHA-256 digests | That Docker Desktop equals a production air-gap |
| Grades follow normative UHQS / δ_C math | That UHBS is an industry consortium standard |
| Module D exercised SSH shell containment probes | That accepting any password is “correct” auth policy |

---

## 2. Software under test

| Field | Value |
| --- | --- |
| Project | [Qyleron/EchidraOSS](https://github.com/Qyleron/EchidraOSS) |
| Description | Multi-protocol honeypot + ATT&CK classifier + dashboard |
| Git commit (source mount) | `c16548ba4eb54af0cf9efa2c545d83039b2c1ece` |
| Image | `echidraoss-honeypot` (Compose build) |
| Image id | `sha256:2d48d2a38ed71d19d99c966f624870310b50c3e31f10ffd73bab37f31780e5ec` |
| Graded listen | TCP **2222** SSH (asyncssh) |
| Other listeners (not graded) | HTTP `:8080`, FTP `:2121`, Telnet `:2323` |
| Lab auth | `root` / `admin` (any credentials accepted) |

---

## 3. Grader

| Field | Full | Quick |
| --- | --- | --- |
| Image | `uhbs:4.0.0-full` | `uhbs:4.0.0` |
| Image id | `sha256:e1d1ee47bb9ef17201de1d2bf5ca6709fbc28a8cd5383ec2d86d60a49e850695` | `sha256:792a7201a691232a33f7c3782e3371dbcef3b71f4578163a123a23b4d3ec73f7` |
| TPS | [`labs/echidra/low_interaction_ssh_full.yaml`](../../labs/echidra/low_interaction_ssh_full.yaml) | [`labs/echidra/low_interaction_ssh_quick.yaml`](../../labs/echidra/low_interaction_ssh_quick.yaml) |
| Inventory | [`labs/echidra/inventory.yaml`](../../labs/echidra/inventory.yaml) | same inventory + quick TPS |
| Protocol plugin | **ssh** | same |
| Profile class | `Low-Interaction` | same |
| Module E | concurrency **10**, requests **50** | `UHBS_QUICK` caps |

---

## 4. Topology

```text
┌──────────────────────┐   network uhbs-lab    ┌──────────────────────────┐
│ uhbs:4.0.0[-full]    │ ───────────────────── │ echidra-lab (Compose)    │
│ mounts /honeypot     │ ← source tree         │ SSH :2222 (graded)       │
│ mounts /telemetry    │ ← sessions.jsonl      │ HTTP/FTP/Telnet (idle)   │
└──────────────────────┘                       └──────────────────────────┘
         ▲                                              │
         │                                              ▼
         │                                     postgres + api (Compose)
```

Start method: Echidra’s own `docker compose up` plus a UHBS overlay that sets
`container_name: echidra-lab` and attaches to `uhbs-lab`.

---

## 5. Module notes (full)

| Module | What ran | Outcome driver |
| --- | --- | --- |
| A | SSH RFC4253 + 1000× timing | Null ID accepted → low fidelity score |
| B | Cross-session marker + shell probes | Marker missing → **25** |
| C | `/telemetry` with `sessions.jsonl` | JSONL without STIX/OTel/ECS → capped **55** |
| D | SSH shell egress / LPE probes | Blocked → **C=100**, **δ_C=1.0** |
| E | 10×50 SSH load | P95 ~1.8 s ≫ 100 ms TPS limit |
| F | bandit + semgrep on source | SAST gate → F capped at **70** |

---

## 6. Lab quirks recorded

1. Fresh `echidra_ssh_host_key` volume may be root-owned; `chown 1000:1000` before
   the honeypot can write the host key.  
2. macOS hosts often lack `/etc/timezone`; the UHBS compose overlay drops those binds.  
3. Postgres may log `persona_configs` missing until schema init — honeypot falls
   back to the `generic_linux` preset and still serves SSH.  
4. Trivy was unavailable in this `uhbs:4.0.0-full` build (download 404); Module F
   used bandit + semgrep only.

---

## 7. Integrity

```bash
python - <<'PY'
import hashlib, json
from pathlib import Path
for mode in ("quick", "full"):
    root = Path(f"docs/conformance/reports/echidra/{mode}")
    man = json.loads((root / "MANIFEST.json").read_text())
    for art in man["artifacts"]:
        p = root / art["path"]
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(("OK" if h == art["sha256"] else "MISMATCH"), mode, art["path"])
PY

uhbs validate-scorecard docs/conformance/fixtures/echidra-low-interaction.scorecard.json --strict
```

---

## 8. Non-endorsement

Named product appears only under `docs/conformance/` as evaluation proof.
A UHQS grade is not a certification, badge, or consortium verdict.
