# beelzebub-mcp — full artifacts

**UHQS 13.5 / GRADE F (Fail)** · UHBS v5.0.1 · assessment `COMPLETE` · δ_C=0.5

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : beelzebub-mcp
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_FAILED
Protocols             : mcp
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : metadata_only
MCP Surface Reason    : <urlopen error [Errno -2] Name or service not known>
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :   0.0/100       0.25     FAILED (<urlopen error [Errno -2] Name or service not known>)
Module B: Behavioral Realism        :   5.0/100       0.20     PARTIAL (<urlopen error [Errno -2] Name or service not known>)
Module C: Telemetry Assurance       :   0.0/100       0.20     PARTIAL (http_inject markers=[] malformed=0)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  80.0/100       0.15     PASSED (service alive after load (connect 3.4ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_FAILED (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 13.5 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

