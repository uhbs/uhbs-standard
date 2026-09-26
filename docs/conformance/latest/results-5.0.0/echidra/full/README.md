# Lab artifacts — echidra/full

**UHQS 36.58 / F** · UHBS v5.0.0 · δ_C=1.0

This page is the human-readable landing for the UHBS-Lab run artifacts.
The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : echidra
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : COMPLETE
Critical Controls     : GATE_PASSED
Protocols             : ssh
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  44.4/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :  25.0/100       0.15     PARTIAL (marker missing across sessions)
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=[] malformed=0)
Module D: Safety & Containment (C)  :   0.0/100       GATE     GATE PASSED (stable)
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1350.5ms P95=1812.5ms P99=1882.2ms TPS_limit=100.0ms proto=ssh)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 hardcoded SSH banners: honeypot/core/persona.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_PASSED (δ_C=1.0; defense-in-depth C=0.0)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : 36.58 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
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

Parent hub: [`../index.md`](../index.md)
