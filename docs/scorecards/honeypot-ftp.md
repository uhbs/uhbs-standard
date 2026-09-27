# Scorecard: honeypot-ftp — ftp (results-5.0.0)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.0** · **Class:** Low-Interaction · **Protocol:** `ftp`  
**Target id (lab):** `honeypot-ftp-ftp` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.0/honeypot-ftp/ftp/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below |

**Report hub:** [honeypot-ftp / ftp](../conformance/latest/results-5.0.0/honeypot-ftp/ftp/index.md) · [Tutorial](../conformance/latest/results-5.0.0/honeypot-ftp/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.0/honeypot-ftp/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.0/honeypot-ftp/ftp/EXECUTION-STEPS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.4 | 0.30 | PASSED | median=1.627ms pstdev=6.519ms (target jitter often <2ms vs native) |
| Module B: Behavioral Realism |  |  |  |  |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate. |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 0.3ms) |
| Module F: Static Code Audit | 56.6 | 0.20 | PARTIAL | 2 static private keys: keys/smtp.private.key, keys/ca.private.key |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded when INCOMPLETE/GATE_FAILED |

Archived 4.x letter grades are **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : honeypot-ftp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : ftp
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  86.4/100       0.30     PASSED (median=1.627ms pstdev=6.519ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  37.0/100       0.15     PARTIAL (PASS step failed: 530 Sorry, Authentication failed.
)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 0.3ms))
Module F: Static Code Audit         :  56.6/100       0.20     PARTIAL (2 static private keys: keys/smtp.private.key, keys/ca.private.key)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
