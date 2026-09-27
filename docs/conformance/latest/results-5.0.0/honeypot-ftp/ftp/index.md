# honeypot-ftp — ftp (results-5.0.0)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.0 · **Class:** Low-Interaction · **Protocol:** `ftp`  
**Target id:** `honeypot-ftp-ftp` · **Evaluated:** 2026-09-26  
**Upstream:** `master` @ `c7b7cbed4c52d3d84b62676dd1a359c6d9da2696`  
**Verdict:** INCOMPLETE / INCOMPLETE / UHQS=39.61 grade=F (`uhqs-v5.1-always-grade`)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Quick](quick/README.md) | UHQS=39.61 grade=F | — | 0.0 | [`SCORECARD.txt`](quick/SCORECARD.txt) · [`report.json`](quick/report.json) |
| [Full](full/README.md) | UHQS=39.61 grade=F | — | 0.0 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) · [`proof/full-run.cast`](full/proof/full-run.cast) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../../fixtures/honeypot-ftp-ftp.scorecard.json`](../../../../fixtures/honeypot-ftp-ftp.scorecard.json)  
Archive: [`../../../../archive/v5.0.0/honeypot-ftp/ftp/`](../../../../archive/v5.0.0/honeypot-ftp/ftp/)  
Replication: [`EXECUTION-STEPS.md`](EXECUTION-STEPS.md)

INCOMPLETE / UHQS=39.61 grade=F (non-SSH Module D). Do not cite archived 4.x letter grades.

## Full run — module breakdown (analyst view)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.4 | 0.30 | PASSED | median=1.627ms pstdev=6.519ms (target jitter often <2ms vs native) |
| Module B: Behavioral Realism |  |  |  |  |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate. |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 0.3ms) |
| Module F: Static Code Audit | 56.6 | 0.20 | PARTIAL | 2 static private keys: keys/smtp.private.key, keys/ca.private.key |
| Safety Gate δ_C | 0.0 | GATE | — | UHQS=39.61 grade=F when INCOMPLETE/GATE_FAILED |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : honeypot-ftp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.1-always-grade
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : ftp
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  86.4/100       0.30     PASSED (median=1.627ms pstdev=6.519ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  37.0/100       0.15     PARTIAL (PASS step failed: 530 Sorry, Authentication failed.
)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 0.3ms))
Module F: Static Code Audit         :  56.6/100       0.20     PARTIAL (2 static private keys: keys/smtp.private.key, keys/ca.private.key)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : UHQS=39.61 grade=F — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (UHQS=39.61 grade=F — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.1-always-grade
====================================================================================
```

## Guides

- Product hub: [`../`](../index.md)
- [Tutorial](../TUTORIAL.md)
- [Methodology](../METHODOLOGY.md)
- [Execution steps](EXECUTION-STEPS.md)
- Published scorecard page: [`../../../../../scorecards/honeypot-ftp.md`](../../../../../scorecards/honeypot-ftp.md)

> Named products appear only under conformance as evaluation proof — not UHBS requirements or endorsements.
