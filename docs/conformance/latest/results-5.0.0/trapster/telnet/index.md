# trapster — Telnet (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Low-Interaction · **Protocol:** `telnet`  
**Target id:** `trapster-telnet` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`  
**Verdict:** INCOMPLETE / ungraded

| Run | UHQS | Grade | Artifacts |
| --- | ---: | --- | --- |
| [Quick](quick/README.md) | ungraded | — | [`SCORECARD.txt`](quick/SCORECARD.txt) |
| [Full](full/README.md) | ungraded | — | [`SCORECARD.txt`](full/SCORECARD.txt) · [`full-run.cast`](full/proof/full-run.cast) |

Fixture: [`../../../../fixtures/trapster-telnet.scorecard.json`](../../../../fixtures/trapster-telnet.scorecard.json)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

Do not cite archived 4.x 64.9 / D.

## Full SCORECARD (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : trapster-telnet
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : telnet
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         : 100.0/100       0.30     PASSED (fsm=100 nego=100 timing=100)
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 1.0ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: trapster/modules/http.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```
