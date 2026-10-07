# Log4Pot (thomaspatzke) (http)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Web-API · **Protocol:** `http`  
**Target id:** `Log4Pot-http` · **Evaluated:** 2026-09-27

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **35.54** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **33.94** | F | 0.5 | COMPLETE / GATE_FAILED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 46.4 | 0.25 | PARTIAL | status=200 |
| Module B: Behavioral Realism | 65.0 | 0.20 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 69.3 | 0.20 | PARTIAL | 1/3 observables present missing=['source_endpoint', 'protocol_action'] |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 100.0 | 0.15 | PASSED | service alive after load (connect 0.6ms) |
| Module F: Static Code Audit | 72.0 | 0.20 | PASSED | trivy not installed — not tested (zero credit) |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : Log4Pot-http
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_FAILED
Protocols             : http
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  46.4/100       0.25     PARTIAL (status=200)
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :  69.3/100       0.20     PARTIAL (1/3 observables present missing=['source_endpoint', 'protocol_action'])
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.6ms))
Module F: Static Code Audit         :  72.0/100       0.20     PASSED (trivy not installed — not tested (zero credit))
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_FAILED (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 33.94 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
