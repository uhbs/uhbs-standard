# OpenCanary (UHBS multi-protocol proof) (snmp)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `snmp`  
**Target id:** `opencanary-snmp` · **Evaluated:** 2026-09-27

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **5.5** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **18.05** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 0.0 | 0.30 | INCOMPLETE | UHBS Module A — plugins=['snmp'] |
| Module B: Behavioral Realism | 5.0 | 0.15 | PARTIAL | no state probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=150.0ms proto=snmp |
| Module F: Static Code Audit | 67.5 | 0.20 | PARTIAL | bandit HIGH=21 |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : opencanary-snmp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : snmp
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :   0.0/100       0.30     INCOMPLETE (UHBS Module A — plugins=['snmp'])
Module B: Behavioral Realism        :   5.0/100       0.15     PARTIAL (no state probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=150.0ms proto=snmp)
Module F: Static Code Audit         :  67.5/100       0.20     PARTIAL (bandit HIGH=21)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 18.05 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
