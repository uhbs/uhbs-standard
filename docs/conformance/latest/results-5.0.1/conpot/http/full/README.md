# conpot-http — full artifacts

**UHQS 16.11 / GRADE F (Fail)** · UHBS v5.0.1 · assessment `COMPLETE` · δ_C=1.0

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : conpot-http
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
Module A: Protocol Fidelity         :   0.0/100       0.25     FAILED (http port 80 closed)
Module B: Behavioral Realism        :  13.0/100       0.20     PARTIAL (inconsistent/no HTTP)
Module C: Telemetry Assurance       :   0.0/100       0.20     FAILED (declared native_json but no matching records)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     :  20.0/100       0.15     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=150.0ms proto=http)
Module F: Static Code Audit         :  52.5/100       0.20     PARTIAL (2 static private keys: conpot/templates/default/ssl/ssl.key, conpot/templates/kamstrup_382/ssl/ssl.key)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_PASSED (δ_C=1.0; defense-in-depth C=83.33)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 16.11 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

