# Cowrie (UHBS multi-protocol proof) (ssh)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id:** `cowrie-ssh` · **Evaluated:** 2026-09-27

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **17.25** | F | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **23.73** | F | 1 | COMPLETE / GATE_PASSED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 22.6 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 6.2 | 0.15 | PARTIAL | Host key for server 'cowrie-lab' does not match: got 'AAAAC3NzaC1lZDI1NTE5AAAAIMBuaXnvSsORPVMSFY6UZAtRICRRlJFKx1GxoqSCBd7m', expected 'AAAAC3NzaC1lZDI1NTE5AAAAILQg1t9/eK4ktUlv3vLEDyDBVkmaGcJw/gsEvet6gU0Y' |
| Module C: Telemetry Assurance | 0.0 | 0.25 | PARTIAL | markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 83.3 | GATE | PASSED | Memory=0 NanoCpus=0 PidsLimit=0 |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 1 predictable PRNG seeds: src/backend_pool/util.py |
| Safety Gate δ_C | 1 | GATE | — | Gate GATE_PASSED; δ_C=1 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : cowrie-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_PASSED
Protocols             : ssh
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  22.6/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :   6.2/100       0.15     PARTIAL (Host key for server 'cowrie-lab' does not match: got 'AAAAC3NzaC1lZDI1NTE5AAAAIMBuaXnvSsORPVMSFY6UZAtRICRRlJFKx1GxoqSCBd7m', expected 'AAAAC3NzaC1lZDI1NTE5AAAAILQg1t9/eK4ktUlv3vLEDyDBVkmaGcJw/gsEvet6gU0Y')
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=[] malformed=0)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: src/backend_pool/util.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_PASSED (δ_C=1.0; defense-in-depth C=83.33)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 23.73 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
