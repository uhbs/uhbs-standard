# dionaea-memcache — full artifacts

**UHQS 20.56 / GRADE F (Fail)** · UHBS v5.0.1 · assessment `INCOMPLETE` · δ_C=0.5

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : dionaea-memcache
System Profile Class  : Database
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : memcache
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  56.4/100       0.25     PARTIAL (ERROR
)
Module B: Behavioral Realism        :  33.0/100       0.25     PARTIAL (STORED
)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1023.3ms P95=1038.7ms P99=1064.4ms TPS_limit=150.0ms proto=memcache)
Module F: Static Code Audit         :  66.3/100       0.20     PARTIAL (bandit HIGH=9)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 20.56 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

