# dionaea-smb — full artifacts

**UHQS ungraded / —** · UHBS v5.0.0 · assessment `INCOMPLETE` · critical controls `INCOMPLETE` · δ_C=0.0

This page is the human-readable landing for the UHBS-Lab run artifacts. The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Module scores

| Module | Score | Status |
| --- | ---: | --- |
| A Protocol Fidelity | 70.43 | PASSED |
| B Behavioral Realism | 65.0 | PARTIAL |
| C Telemetry Assurance | 0.0 | INCOMPLETE |
| D Safety & Containment | 0.0 | INCOMPLETE |
| E Scalability & Latency | 55.0 | PARTIAL |
| F Static Code Audit | 66.35 | PARTIAL |

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : dionaea-smb
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : smb
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  70.4/100       0.30     PASSED (median=1.258ms pstdev=191.691ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1024.7ms P95=1057.0ms P99=1062.9ms TPS_limit=150.0ms proto=smb)
Module F: Static Code Audit         :  66.3/100       0.20     PARTIAL (bandit HIGH=9)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
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
