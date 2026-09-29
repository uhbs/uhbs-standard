# genaipot — pop3 (results-5.0.1)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `pop3`  
**Target id:** `genaipot-pop3` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `205ffe40008f2e76e0decdb01bc19bf8e00acd8a`  
**Verdict:** INCOMPLETE / INCOMPLETE / UHQS=40.28 grade=F (`uhqs-v5.1-always-grade`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | UHQS=40.28 grade=F | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | UHQS=40.28 grade=F | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/genaipot-pop3.scorecard.json`](../../../../fixtures/genaipot-pop3.scorecard.json)  
Archive: [`../../../../archive/v5.0.1/genaipot/pop3/`](../../../../archive/v5.0.1/genaipot/pop3/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

INCOMPLETE / UHQS=40.28 grade=F (non-SSH Module D). Do not cite archived 4.x letter grades.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 81.5 | 0.30 | PASSED | median=0.936ms pstdev=372.489ms (target jitter often <2ms vs native) |
| Module B: Behavioral Realism | 65.0 | 0.15 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate. |
| Module E: Scalability & Latency | 55.0 | 0.10 | PARTIAL | P50=62.6ms P95=2084.1ms P99=2113.6ms TPS_limit=300.0ms proto=pop3 |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | bandit HIGH=1 |
| Safety Gate δ_C | 0.0 | GATE | — | UHQS=40.28 grade=F when INCOMPLETE/GATE_FAILED |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : genaipot-pop3
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.1-always-grade
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : pop3
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  81.5/100       0.30     PASSED (median=0.936ms pstdev=372.489ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=62.6ms P95=2084.1ms P99=2113.6ms TPS_limit=300.0ms proto=pop3)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (bandit HIGH=1)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : UHQS=40.28 grade=F — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : null (UHQS=40.28 grade=F — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.1-always-grade
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/genaipot-pop3.md`](../../../../../scorecards/genaipot-pop3.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
