# Scorecard: cowrie — ssh (results-5.0.0)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.0** · **Class:** Low-Interaction · **Protocol:** `ssh`  
**Target id (lab):** `cowrie-ssh` · **Evaluation date:** 2026-09-26  
**Verdict:** COMPLETE / GATE_FAILED / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.0/cowrie/ssh/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below |

**Report hub:** [cowrie / ssh](../conformance/latest/results-5.0.0/cowrie/ssh/index.md) · [Tutorial](../conformance/latest/results-5.0.0/cowrie/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.0/cowrie/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.0/cowrie/ssh/EXECUTION-STEPS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 16.6 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 60.0 | 0.15 | PARTIAL | marker missing across sessions |
| Module C: Telemetry Assurance | 0.0 | 0.25 | PARTIAL | markers=[] malformed=0 |
| Module D: Safety & Containment (C) |  |  |  |  |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 3.8ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 1 predictable PRNG seeds: src/backend_pool/util.py |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded when INCOMPLETE/GATE_FAILED |

Archived 4.x letter grades are **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : cowrie-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : COMPLETE
Critical Controls     : GATE_FAILED
Protocols             : ssh
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  16.6/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :  60.0/100       0.15     PARTIAL (marker missing across sessions)
Module C: Telemetry Assurance       :   0.0/100       0.25     PARTIAL (markers=[] malformed=0)
Module D: Safety & Containment (C)  :   0.0/100       GATE     GATE FAILED (OOB LEAK)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 3.8ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (1 predictable PRNG seeds: src/backend_pool/util.py)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_FAILED (defense-in-depth C=0.0; no composite UHQS)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
