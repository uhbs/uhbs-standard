# beelzebub-http — full artifacts

**UHQS ungraded / —** · UHBS v5.0.1 · assessment `INCOMPLETE` · critical controls `INCOMPLETE` · δ_C=0.0

This page is the human-readable landing for the UHBS-Lab run artifacts. The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Module scores

| Module | Score | Status |
| --- | ---: | --- |
| A Protocol Fidelity | 100.0 | PASSED |
| B Behavioral Realism | 65.0 | PARTIAL |
| C Telemetry Assurance | 0.0 | INCOMPLETE |
| D Safety & Containment | 0.0 | INCOMPLETE |
| E Scalability & Latency | 100.0 | PASSED |
| F Static Code Audit | 70.0 | PASSED |

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : beelzebub-http
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
Module A: Protocol Fidelity         : 100.0/100       0.25     PASSED (fsm=100 nego=100 timing=100)
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.7ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

## Files in this directory

- [`SCORECARD.txt`](SCORECARD.txt)
- [`report.json`](report.json)
- [`MANIFEST.json`](MANIFEST.json)
- [`REPORT.txt`](REPORT.txt)
- [`run-meta.json`](run-meta.json)
- [`uhbs-run.log`](uhbs-run.log)
