# heralding — ssh (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id:** `heralding-ssh` · **Evaluated:** 2026-09-26  
**Upstream:** `master` @ `ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0`  
**Verdict:** INCOMPLETE / INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | ungraded | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | ungraded | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/heralding-ssh.scorecard.json`](../../../../fixtures/heralding-ssh.scorecard.json)  
Archive: [`../../../../archive/v5.0.0/heralding/ssh/`](../../../../archive/v5.0.0/heralding/ssh/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

INCOMPLETE / ungraded (Module D critical controls). Do not cite archived 4.x letter grades.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 44.4 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 6.2 | 0.15 | PARTIAL | Authentication failed. |
| Module C: Telemetry Assurance | 0.0 | 0.25 | PARTIAL | markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | UHBS v5: containment verdict from critical controls; defense-in-depth score is diagnostic only; no 95-point floor |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh |
| Module F: Static Code Audit | 66.9 | 0.20 | PARTIAL | bandit HIGH=11 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded when INCOMPLETE/GATE_FAILED |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : heralding-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
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
Module B: Behavioral Realism        :   6.2/100       0.15     PARTIAL (Authentication failed.)
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=[] malformed=0)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (UHBS v5: containment verdict from critical controls; defense-in-depth score is diagnostic only; no 95-point floor)
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh)
Module F: Static Code Audit         :  66.9/100       0.20     PARTIAL (bandit HIGH=11)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/heralding-ssh.md`](../../../../../scorecards/heralding-ssh.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
