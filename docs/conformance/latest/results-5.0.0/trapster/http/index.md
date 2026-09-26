# trapster — HTTP (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Web-API · **Protocol:** `http`  
**Target id:** `trapster-http` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`  
**Verdict:** INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | ungraded | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) |
| [Full](full/README.md) | ungraded | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Fixture: [`../../../../fixtures/trapster-http.scorecard.json`](../../../../fixtures/trapster-http.scorecard.json)  
Archive: [`../../../../archive/v5.0.0/trapster/http/`](../../../../archive/v5.0.0/trapster/http/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

Do not cite archived 4.x 63.33 / D as the current result.

## Full module snapshot

| Module | Score | Weight | Status |
| --- | ---: | --- | --- |
| A Protocol Fidelity | 73.2 | 0.25 | PASSED |
| B Behavioral Realism | 65.0 | 0.20 | PARTIAL |
| C Telemetry Assurance | 0.0 | 0.20 | INCOMPLETE |
| D Safety & Containment | 0.0 | GATE | INCOMPLETE |
| E Scalability & Latency | 100.0 | 0.15 | PASSED |
| F Static Code Audit | 70.0 | 0.20 | PASSED |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : trapster-http
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : http
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  73.2/100       0.25     PASSED (status=200 (want 400/505 or close))
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 1.2ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: trapster/modules/http.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md) · [Methodology](../METHODOLOGY.md)
- Scorecard: [`../../../../../scorecards/trapster-http.md`](../../../../../scorecards/trapster-http.md)
