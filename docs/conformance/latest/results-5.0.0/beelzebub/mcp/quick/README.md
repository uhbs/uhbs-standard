# beelzebub-mcp — quick artifacts

**UHQS ungraded / —** · UHBS v5.0.1 · assessment `INCOMPLETE` · critical controls `INCOMPLETE` · δ_C=0.0

This page is the human-readable landing for the UHBS-Lab run artifacts. The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Module scores

| Module | Score | Status |
| --- | ---: | --- |
| A Protocol Fidelity | 60.07 | PARTIAL |
| B Behavioral Realism | 94.28 | PASSED |
| C Telemetry Assurance | 0.0 | INCOMPLETE |
| D Safety & Containment | 0.0 | INCOMPLETE |
| E Scalability & Latency | 100.0 | PASSED |
| F Static Code Audit | 0.0 | INCOMPLETE |

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : beelzebub-mcp
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : mcp
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : interactive
MCP Surface Reason    : exercised allowlisted tool tool:system-log
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  60.1/100       0.25     PARTIAL (allowed tools/list before notifications/initialized)
Module B: Behavioral Realism        :  94.3/100       0.20     PASSED (survived binary blast)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.1ms))
Module F: Static Code Audit         :   0.0/100       0.20     INCOMPLETE (Module F white-box audit (keys/prompts/SAST/VFS))
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
