# Scorecard: heralding — smtp (results-5.0.0)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.0** · **Class:** Low-Interaction · **Protocol:** `smtp`  
**Target id (lab):** `heralding-smtp` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.0/heralding/smtp/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below |

**Report hub:** [heralding / smtp](../conformance/latest/results-5.0.0/heralding/smtp/index.md) · [Tutorial](../conformance/latest/results-5.0.0/heralding/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.0/heralding/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.0/heralding/smtp/EXECUTION-STEPS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.4 | 0.30 | PASSED | median=0.527ms pstdev=60.221ms (target jitter often <2ms vs native) |
| Module B: Behavioral Realism | 37.0 | 0.15 | PARTIAL | no codes |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate. |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 6.2ms) |
| Module F: Static Code Audit | 66.9 | 0.20 | PARTIAL | bandit HIGH=11 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded when INCOMPLETE/GATE_FAILED |

Archived 4.x letter grades are **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : heralding-smtp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : smtp
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  86.4/100       0.30     PASSED (median=0.527ms pstdev=60.221ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  37.0/100       0.15     PARTIAL (no codes)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 6.2ms))
Module F: Static Code Audit         :  66.9/100       0.20     PARTIAL (bandit HIGH=11)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
