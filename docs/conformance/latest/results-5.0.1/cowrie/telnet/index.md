# Cowrie (UHBS multi-protocol proof) (telnet)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `telnet`  
**Target id:** `cowrie-telnet` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **89.06** | B | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **77.98** | C | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 97.4 | 0.30 | PASSED | fsm=100 nego=91 timing=100 |
| Module B: Behavioral Realism | 65.0 | 0.15 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 83.3 | GATE | PASSED | Memory=0 NanoCpus=0 PidsLimit=0 |
| Module E: Scalability & Latency | 55.0 | 0.10 | PARTIAL | P50=1.9ms P95=1004.0ms P99=1006.6ms TPS_limit=500.0ms proto=telnet |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 1 predictable PRNG seeds: src/backend_pool/util.py |
| Safety Gate δ_C | 1 | GATE | — | Gate GATE_PASSED; δ_C=1 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : cowrie-telnet
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_PASSED
Protocols             : telnet
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  97.4/100       0.30     PASSED (fsm=100 nego=91 timing=100)
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1.9ms P95=1004.0ms P99=1006.6ms TPS_limit=500.0ms proto=telnet)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: src/backend_pool/util.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=1.0; defense-in-depth C=83.33; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 77.98 / 100
OVERALL EVALUATION GRADE              : GRADE C (Conditional — not approved for production)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
