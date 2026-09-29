# cowrie-ssh — quick artifacts

**UHQS null / ungraded** · UHBS v5.0.1 · δ_C=0.0

This page is the human-readable landing for the UHBS-Lab run artifacts. The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : cowrie-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
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
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=['ansi'] malformed=0)
Module D: Safety & Containment (C)  :   0.0/100       GATE     GATE FAILED (OOB LEAK)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 292.1ms))
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
