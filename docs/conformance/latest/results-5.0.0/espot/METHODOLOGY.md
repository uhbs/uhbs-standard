# ESPot methodology & trust notes (results-5.0.0)

**Status:** Informative · evaluation proof  
**Related:** [TUTORIAL.md](TUTORIAL.md) · [EXECUTION-STEPS.md](EXECUTION-STEPS.md) · [full/run-meta.json](full/run-meta.json)

## 1. Claims

| We claim | We do **not** claim |
| --- | --- |
| These artifacts were produced by UHBS-Lab **5.0.0** against ESPot HEAD `0b126a7783da69d543239606df59211c5d21f1db` | That ESPot is certified or UHBS-approved |
| Quick + full Docker grades, with a full-run `.cast` | That Module D fully proved host containment |
| Honest v5 Safety Gate: this run is **INCOMPLETE / ungraded** | That archived 4.x UHQS 63.33 / D still applies |

## 2. Software under test

| Field | Value |
| --- | --- |
| Project | [mycert/ESPot](https://github.com/mycert/ESPot) |
| Branch / commit | `master` / `0b126a7783da69d543239606df59211c5d21f1db` |
| Runtime strategy | `custom-base` |
| Base image | `node:10-buster-slim` |
| Why not Ubuntu latest | Upstream README requires NodeJS v0.10.x; sqlite3@2 fails on modern Node |
| Target image | `espot:lab` (`sha256:353e164df44fef98a94ebd3da59b01bc0b576e757c1b425d954b871f9422b955`) |
| Listen | TCP `9200` / HTTP · alias `espot-lab` on `uhbs-lab` |
| Shim | SQLite logger disabled |

## 3. Grader

| Field | Quick | Full |
| --- | --- | --- |
| Image | `uhbs:5.0.0` | `uhbs:5.0.0-full` |
| TPS | `docs/conformance/labs/espot/web_api_quick.yaml` | `docs/conformance/labs/espot/web_api_full.yaml` |
| Inventory | `docs/conformance/labs/espot/inventory.yaml` | same |

## 4. Topology

```text
uhbs:5.0.0[-full]  --uhbs-lab-->  uhbs-target-espot-http (alias espot-lab:9200)
  /honeypot = .local/labs/espot
  /telemetry = .local/labs/espot-telemetry (full only)
```

## 5. What changed vs archive/v5.0.0

- Grader stamps **UHBS 5.0.0** (`uhqs-v5.0-critical-gate-diagnostic`), not leftover 4.0.1.
- Module C v5 requires declared-format / sink-side evidence; Express `access.log` is not enough → C INCOMPLETE.
- Module D v5: non-SSH targets need gateway/packet evidence; attestation + canary file does not clear the gate → D INCOMPLETE.
- Composite UHQS/grade are **null** (ungraded). Archived 63.33 / D is historical only.

## 6. Limitations

- Operator attested air-gap (`UHBS_AIRGAP_ATTESTED=1`) is not a physical air-gap.
- HTTP-only decoy: no SSH exec surface for shell probes.
- Trivy may be absent in the grader image; bandit + semgrep ran on the full pack.
