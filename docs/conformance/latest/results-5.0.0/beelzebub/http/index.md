# beelzebub — HTTP (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Web-API · **Protocol:** `http`  
**Target id:** `beelzebub-http` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `67d5632a754f39f7b14c703d3009193150440116`  
**Verdict:** INCOMPLETE / UHQS=50.25 grade=D (`uhqs-v5.1-always-grade`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | UHQS=50.25 grade=D | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | UHQS=50.25 grade=D | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/beelzebub-http.scorecard.json`](../../../../fixtures/beelzebub-http.scorecard.json)  
Archive: [`../../../../archive/v5.0.0/beelzebub/http/`](../../../../archive/v5.0.0/beelzebub/http/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

v5 Safety Gate leaves this unit **UHQS=50.25 grade=D**. Do not cite archived 4.x 66.02 / D.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 100.0 | 0.25 | PASSED | fsm=100 nego=100 timing=100 |
| Module B: Behavioral Realism | 65.0 | 0.20 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.20 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress an |
| Module E: Scalability & Latency | 100.0 | 0.15 | PASSED | service alive after load (connect 0.7ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.0 | GATE | — | UHQS=50.25 grade=D (INCOMPLETE) |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : beelzebub-http
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.1-always-grade
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
Module A: Protocol Fidelity         : 100.0/100       0.25     PASSED (fsm=100 nego=100 timing=100)
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.7ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : UHQS=50.25 grade=D — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (UHQS=50.25 grade=D — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.1-always-grade
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/beelzebub-http.scorecard.md`](../../../../../scorecards/beelzebub-http.scorecard.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
