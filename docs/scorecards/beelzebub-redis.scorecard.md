# Scorecard: beelzebub — redis (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Low-Interaction · **Protocol / surface:** `redis`  
**Target id (lab):** `beelzebub-redis` · **Evaluation date:** 2026-09-27  
**Verdict:** INCOMPLETE / GATE_FAILED (`uhqs-v5.2-measured-renorm`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | 9.72| F| 0.5| [quick SCORECARD](../conformance/latest/results-5.0.1/beelzebub/redis/quick/SCORECARD.txt) |
| **Full (authoritative)** | **16.46** | **F** | **0.5** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.1/beelzebub/redis/full/proof/full-run.cast) |

**Report hub:** [beelzebub / redis](../conformance/latest/results-5.0.1/beelzebub/redis/index.md) · [Tutorial](../conformance/latest/results-5.0.1/beelzebub/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/beelzebub/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/beelzebub/redis/EXECUTION-STEPS.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 26.5 | 0.30 | PARTIAL | [Errno -2] Name or service not known |
| Module B: Behavioral Realism | 5.0 | 0.15 | PARTIAL | [Errno -2] Name or service not known |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=150.0ms proto=redis |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

Archived 4.x 61.01 / D is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : beelzebub-redis
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : redis
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  26.5/100       0.30     PARTIAL ([Errno -2] Name or service not known)
Module B: Behavioral Realism        :   5.0/100       0.15     PARTIAL ([Errno -2] Name or service not known)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=150.0ms proto=redis)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 16.46 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

Re-run commands are in the [execution steps](../conformance/latest/results-5.0.1/beelzebub/redis/EXECUTION-STEPS.md).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
