# trapster — SSH (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id:** `trapster-ssh` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7`  
**Verdict:** INCOMPLETE / UHQS=22.7 grade=F (`uhqs-v5.1-always-grade`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | UHQS=22.7 grade=F | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | UHQS=22.7 grade=F | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/trapster-ssh.scorecard.json`](../../../../fixtures/trapster-ssh.scorecard.json)  
Archive: [`../../../../archive/v5.0.0/trapster/ssh/`](../../../../archive/v5.0.0/trapster/ssh/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

v5 Safety Gate leaves this SSH unit **UHQS=22.7 grade=F**. Do not cite archived 4.x 44.38 / F as the current result.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 44.4 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 6.2 | 0.15 | PARTIAL | known_hosts miss for `[trapster-lab]:2222` |
| Module C: Telemetry Assurance | 0.0 | 0.25 | FAILED | declared native_json but no matching records |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | critical controls not fully measured |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50/P95/P99 = 0.0 ms |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | predictable PRNG in `trapster/modules/http.py` |
| Safety Gate δ_C | 0.0 | GATE | — | UHQS=22.7 grade=F (INCOMPLETE) |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : trapster-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.1-always-grade
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : ssh
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  44.4/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :   6.2/100       0.15     PARTIAL (Server '[trapster-lab]:2222' not found in known_hosts)
Module C: Telemetry Assurance       :   0.0/100       0.25     FAILED (declared native_json but no matching records)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (UHBS v5: containment verdict from critical controls; defense-in-depth score is diagnostic only; no 95-point floor)
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: trapster/modules/http.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : UHQS=22.7 grade=F — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (UHQS=22.7 grade=F — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.1-always-grade
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/trapster-ssh.md`](../../../../../scorecards/trapster-ssh.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
