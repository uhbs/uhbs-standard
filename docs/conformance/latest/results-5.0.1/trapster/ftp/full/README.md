# trapster-ftp — full artifacts

**UHQS 8.38 / GRADE F (Fail)** · UHBS v5.0.1 · assessment `INCOMPLETE` · δ_C=0.5

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : trapster-ftp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : ftp
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :   0.0/100       0.30     FAILED (ftp port 2121 closed)
Module B: Behavioral Realism        :   5.0/100       0.15     PARTIAL ([Errno 111] Connection refused)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=150.0ms proto=ftp)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: trapster/modules/http.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 8.38 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

