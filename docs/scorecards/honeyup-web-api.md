# Scorecard: honeyup — http (results-5.0.0)

**UHBS:** **5.0.0** · **Class:** Web-API · **Protocol:** `http`  
**Verdict:** INCOMPLETE / INCOMPLETE (ungraded unless GATE_PASSED)

| Run | UHQS | Grade | Proof |
| --- | ---: | --- | --- |
| Quick | ungraded | — | [quick](../conformance/latest/results-5.0.0/honeyup/http/quick/SCORECARD.txt) |
| **Full** | **ungraded** | **—** | Verbatim SCORECARD below |

**Hub:** [honeyup](../conformance/latest/results-5.0.0/honeyup/http/index.md) · [Tutorial](../conformance/latest/results-5.0.0/honeyup/http/../TUTORIAL.md) · [Execution steps](../conformance/latest/results-5.0.0/honeyup/http/EXECUTION-STEPS.md)

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : honeyup-http
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : http
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  86.4/100       0.25     PASSED (median=0.519ms pstdev=4.131ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 19.7ms))
Module F: Static Code Audit         :  71.3/100       0.20     PASSED (trivy not installed — not tested (zero credit))
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```
