# llmpot-s7comm — full artifacts

**UHQS null / ungraded** · UHBS v5.0.0 · δ_C=0.0

This page is the human-readable landing for the UHBS-Lab run artifacts. The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : llmpot-s7comm
System Profile Class  : ICS-SCADA
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : s7comm
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  78.4/100       0.35     PASSED (median=0.858ms pstdev=231.870ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  45.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.15     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 1.2ms))
Module F: Static Code Audit         :  87.9/100       0.20     PASSED (1 static private keys: emulator/certificates/ca.crt.key)
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
- [`proof/full-run.cast`](proof/full-run.cast)
