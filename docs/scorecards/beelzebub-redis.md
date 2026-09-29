# Scorecard: beelzebub — redis (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Low-Interaction · **Protocol / surface:** `redis`  
**Target id (lab):** `beelzebub-redis` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.1/beelzebub/redis/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.1/beelzebub/redis/full/proof/full-run.cast) |

**Report hub:** [beelzebub / redis](../conformance/latest/results-5.0.1/beelzebub/redis/index.md) · [Tutorial](../conformance/latest/results-5.0.1/beelzebub/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/beelzebub/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/beelzebub/redis/EXECUTION-STEPS.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 49.2 | 0.30 | PARTIAL | closed on wrong-arity GET |
| Module B: Behavioral Realism | 25.0 | 0.15 | PARTIAL | SET/GET failed |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | declared-format / sink-side C2 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | non-SSH needs gateway/packet evidence |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=40 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded (INCOMPLETE) |

Archived 4.x 61.01 / D is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : beelzebub-redis
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : redis
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  49.2/100       0.30     PARTIAL (closed on wrong-arity GET)
Module B: Behavioral Realism        :  25.0/100       0.15     PARTIAL (SET/GET failed)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 1.9ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=40)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

## Replication

Re-run commands are in the [execution steps](../conformance/latest/results-5.0.1/beelzebub/redis/EXECUTION-STEPS.md). Environment and limitations are in the [methodology](../conformance/latest/results-5.0.1/beelzebub/METHODOLOGY.md).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
