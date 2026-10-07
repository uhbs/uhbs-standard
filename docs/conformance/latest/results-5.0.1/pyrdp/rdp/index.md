# pyrdp (GoSecure) (rdp)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `rdp`  
**Target id:** `pyrdp-rdp` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **54.45** | D | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **36.14** | F | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 36.4 | 0.30 | PARTIAL | no reply |
| Module B: Behavioral Realism | 33.0 | 0.15 | PARTIAL | r1= r2= e=- |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 83.3 | GATE | PASSED | Memory=0 NanoCpus=0 PidsLimit=0 |
| Module E: Scalability & Latency | 40.0 | 0.10 | PARTIAL | P50=1024.0ms P95=2053.5ms P99=2058.9ms TPS_limit=150.0ms proto=rdp |
| Module F: Static Code Audit | 0.0 | 0.20 | FAILED |  |
| Safety Gate δ_C | 1 | GATE | — | Gate GATE_PASSED; δ_C=1 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : pyrdp-rdp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_PASSED
Protocols             : rdp
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  36.4/100       0.30     PARTIAL (no reply)
Module B: Behavioral Realism        :  33.0/100       0.15     PARTIAL (r1= r2= e=-)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     :  40.0/100       0.10     PARTIAL (P50=1024.0ms P95=2053.5ms P99=2058.9ms TPS_limit=150.0ms proto=rdp)
Module F: Static Code Audit         :   0.0/100       0.20     FAILED
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=1.0; defense-in-depth C=83.33; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 36.14 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
