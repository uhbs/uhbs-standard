# beelzebub — SSH (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id:** `beelzebub-ssh` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `67d5632a754f39f7b14c703d3009193150440116`  
**Verdict:** INCOMPLETE / UHQS=25.15 grade=F (`uhqs-v5.1-always-grade`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | UHQS=25.15 grade=F | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | UHQS=25.15 grade=F | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/beelzebub-ssh.scorecard.json`](../../../../fixtures/beelzebub-ssh.scorecard.json)  
Archive: [`../../../../archive/v5.0.0/beelzebub/ssh/`](../../../../archive/v5.0.0/beelzebub/ssh/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

v5 Safety Gate leaves this unit **UHQS=25.15 grade=F**. Do not cite archived 4.x 59.88 / D.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 55.3 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 6.2 | 0.15 | PARTIAL | Server '[beelzebub-lab]:2222' not found in known_hosts |
| Module C: Telemetry Assurance | 0.0 | 0.25 | FAILED | declared native_json but no matching records |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | UHBS v5: containment verdict from critical controls; defense-in-depth score is d |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.0 | GATE | — | UHQS=25.15 grade=F (INCOMPLETE) |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : beelzebub-ssh
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
Module A: Protocol Fidelity         :  55.3/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :   6.2/100       0.15     PARTIAL (Server '[beelzebub-lab]:2222' not found in known_hosts)
Module C: Telemetry Assurance       :   0.0/100       0.25     FAILED (declared native_json but no matching records)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (UHBS v5: containment verdict from critical controls; defense-in-depth score is diagnostic only; no 95-point floor)
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : UHQS=25.15 grade=F — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (UHQS=25.15 grade=F — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.1-always-grade
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/beelzebub-ssh.scorecard.md`](../../../../../scorecards/beelzebub-ssh.scorecard.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
