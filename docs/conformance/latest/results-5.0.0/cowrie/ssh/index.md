# cowrie — ssh (results-5.0.1)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id:** `cowrie-ssh` · **Evaluated:** 2026-09-26  
**Upstream:** `main` @ `fef0d620962e23194a9d34a048488f9c76c85835`  
**Verdict:** COMPLETE / GATE_FAILED / UHQS=18.98 grade=F (`uhqs-v5.1-always-grade`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | UHQS=18.98 grade=F | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | UHQS=18.98 grade=F | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/cowrie-ssh.scorecard.json`](../../../../fixtures/cowrie-ssh.scorecard.json)  
Archive: [`../../../../archive/v5.0.1/cowrie/ssh/`](../../../../archive/v5.0.1/cowrie/ssh/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

COMPLETE / GATE_FAILED (OOB LEAK) / UHQS=18.98 grade=F. Do not cite archived 4.x letter grades.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 16.6 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 60.0 | 0.15 | PARTIAL | marker missing across sessions |
| Module C: Telemetry Assurance | 0.0 | 0.25 | PARTIAL | markers=[] malformed=0 |
| Module D: Safety & Containment (C) |  |  |  |  |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 3.8ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 1 predictable PRNG seeds: src/backend_pool/util.py |
| Safety Gate δ_C | 0.0 | GATE | — | UHQS=18.98 grade=F when INCOMPLETE/GATE_FAILED |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : cowrie-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.1-always-grade
Assessment Status     : COMPLETE
Critical Controls     : GATE_FAILED
Protocols             : ssh
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  16.6/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :  60.0/100       0.15     PARTIAL (marker missing across sessions)
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=[] malformed=0)
Module D: Safety & Containment (C)  :   0.0/100       GATE     GATE FAILED (OOB LEAK)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 3.8ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: src/backend_pool/util.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_FAILED (defense-in-depth C=0.0; no composite UHQS)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : null (UHQS=18.98 grade=F — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.1-always-grade
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/cowrie-ssh.md`](../../../../../scorecards/cowrie-ssh.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
