# Scorecard: genaipot — pop3 (results-5.0.0)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.0** · **Class:** Low-Interaction · **Protocol:** `pop3`  
**Target id (lab):** `genaipot-pop3` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.0/genaipot/pop3/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below |

**Report hub:** [genaipot / pop3](../conformance/latest/results-5.0.0/genaipot/pop3/index.md) · [Tutorial](../conformance/latest/results-5.0.0/genaipot/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.0/genaipot/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.0/genaipot/pop3/EXECUTION-STEPS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 81.5 | 0.30 | PASSED | median=0.936ms pstdev=372.489ms (target jitter often <2ms vs native) |
| Module B: Behavioral Realism | 65.0 | 0.15 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate. |
| Module E: Scalability & Latency | 55.0 | 0.10 | PARTIAL | P50=62.6ms P95=2084.1ms P99=2113.6ms TPS_limit=300.0ms proto=pop3 |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | bandit HIGH=1 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded when INCOMPLETE/GATE_FAILED |

Archived 4.x letter grades are **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : genaipot-pop3
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : pop3
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  81.5/100       0.30     PASSED (median=0.936ms pstdev=372.489ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=62.6ms P95=2084.1ms P99=2113.6ms TPS_limit=300.0ms proto=pop3)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (bandit HIGH=1)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
