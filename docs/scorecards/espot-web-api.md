# Scorecard: espot — lab (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Web-API · **Protocol:** `http`  
**Target id (lab):** `espot` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.1/espot/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below |

**Report hub:** [espot](../conformance/latest/results-5.0.1/espot/index.md) · [Tutorial](../conformance/latest/results-5.0.1/espot/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/espot/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/espot/EXECUTION-STEPS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.8 | 0.25 | PASSED | HTTP/9.9 still returns 200 |
| Module B: Behavioral Realism | 65.0 | 0.20 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Quality | 0.0 | 0.20 | INCOMPLETE | declared-format validation |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | non-SSH gateway/packet evidence |
| Module E: Scalability & Latency | 100.0 | 0.15 | PASSED | service alive after load |
| Module F: Static Code Audit | 66.6 | 0.20 | PARTIAL | semgrep error/critical=2 total=6 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded (INCOMPLETE) |

Archived 4.x 63.33 / D is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : espot
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
Module A: Protocol Fidelity         :  86.8/100       0.25     PASSED (status=200 (want 400/505 or close))
Module B: Behavioral Realism        :  65.0/100       0.20     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 1.0ms))
Module F: Static Code Audit         :  66.6/100       0.20     PARTIAL (semgrep error/critical=2 total=6)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
