# Scorecard: echidra — ssh (results-5.0.1)

**UHBS:** **5.0.1** · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Verdict:** COMPLETE / GATE_PASSED · **UHQS 36.58 / F**

| Run | UHQS | Grade | Proof |
| --- | ---: | --- | --- |
| Quick | ungraded | — | [quick](../conformance/latest/results-5.0.1/echidra/quick/SCORECARD.txt) |
| **Full** | **36.58** | **F** | Verbatim SCORECARD below |

**Hub:** [echidra](../conformance/latest/results-5.0.1/echidra/index.md) · [Tutorial](../conformance/latest/results-5.0.1/echidra/TUTORIAL.md) · [Execution steps](../conformance/latest/results-5.0.1/echidra/EXECUTION-STEPS.md)

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
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
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 36.58 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```
