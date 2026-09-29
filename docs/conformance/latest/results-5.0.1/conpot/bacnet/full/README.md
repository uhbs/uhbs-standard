# conpot-bacnet — full artifacts

**UHQS 30.5 / GRADE F (Fail)** · UHBS v5.0.1 · assessment `INCOMPLETE` · δ_C=1.0

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : conpot-bacnet
System Profile Class  : ICS-SCADA
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_PASSED
Protocols             : bacnet
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :   0.0/100       0.35     INCOMPLETE (UHBS Module A — plugins=['bacnet'])
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.15     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     :  35.0/100       0.10     PARTIAL (P50=1502.9ms P95=1508.4ms P99=1509.5ms TPS_limit=150.0ms proto=bacnet)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (2 static private keys: conpot/templates/default/ssl/ssl.key, conpot/templates/kamstrup_382/ssl/ssl.key)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=1.0; defense-in-depth C=83.33; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 30.5 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

