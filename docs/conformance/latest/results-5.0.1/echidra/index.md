# EchidraOSS — published UHBS lab reports

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id:** `echidra-ssh` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **30.12** | F | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **38.09** | F | 1 | COMPLETE / GATE_PASSED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 70.5 | 0.30 | PASSED | accepted null ID |
| Module B: Behavioral Realism | 6.2 | 0.15 | PARTIAL | Server '[echidra-lab]:2222' not found in known_hosts |
| Module C: Telemetry Assurance | 0.0 | 0.25 | PARTIAL | markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 83.3 | GATE | PASSED | Memory=0 NanoCpus=0 PidsLimit=0 |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=100.0ms proto=ssh |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 1 hardcoded SSH banners: honeypot/core/persona.py |
| Safety Gate δ_C | 1 | GATE | — | Gate GATE_PASSED; δ_C=1 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : echidra
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_PASSED
Protocols             : ssh
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  70.5/100       0.30     PASSED (accepted null ID)
Module B: Behavioral Realism        :   6.2/100       0.15     PARTIAL (Server '[echidra-lab]:2222' not found in known_hosts)
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=[] malformed=0)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=100.0ms proto=ssh)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 hardcoded SSH banners: honeypot/core/persona.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_PASSED (δ_C=1.0; defense-in-depth C=83.33)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 38.09 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../reports/READING-UHQS.md)
- Tutorial & methodology: see the product hub for this decoy

> Named product is evaluation proof only — not a UHBS endorsement.
