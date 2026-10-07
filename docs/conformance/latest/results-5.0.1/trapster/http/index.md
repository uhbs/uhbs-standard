# Trapster Community (UHBS multi-protocol proof) (http)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Web-API · **Protocol:** `http`  
**Target id:** `trapster-http` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **31.66** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **28.95** | F | 0.5 | COMPLETE / GATE_FAILED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 90.6 | 0.25 | PASSED | status=200 (want 400/505 or close) |
| Module B: Behavioral Realism | 65.0 | 0.20 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.20 | PARTIAL | http_inject markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 55.0 | 0.15 | PARTIAL | P50=2.1ms P95=1063.4ms P99=1064.6ms TPS_limit=150.0ms proto=http |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 1 predictable PRNG seeds: trapster/modules/http.py |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : trapster-http
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_FAILED
Protocols             : http
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  90.6/100       0.25     PASSED (status=200 (want 400/505 or close))
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     PARTIAL (http_inject markers=[] malformed=0)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  55.0/100       0.15     PARTIAL (P50=2.1ms P95=1063.4ms P99=1064.6ms TPS_limit=150.0ms proto=http)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: trapster/modules/http.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_FAILED (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 28.95 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
