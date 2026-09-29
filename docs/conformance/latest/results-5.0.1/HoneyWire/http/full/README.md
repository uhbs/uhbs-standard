# HoneyWire-http — full artifacts

**UHQS 57.15 / GRADE D (Needs Remediation)** · UHBS v5.0.1 · assessment `COMPLETE` · δ_C=1.0

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : HoneyWire-http
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_PASSED
Protocols             : http
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  60.6/100       0.25     PARTIAL (status=200)
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     FAILED (declared native_json but no matching records)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.4ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=4 total=28)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_PASSED (δ_C=1.0; defense-in-depth C=83.33)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 57.15 / 100
OVERALL EVALUATION GRADE              : GRADE D (Needs Remediation)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

