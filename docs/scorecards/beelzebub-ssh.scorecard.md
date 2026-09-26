# Scorecard: beelzebub — ssh (results-5.0.0)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.0** · **Class:** Low-Interaction · **Protocol / surface:** `ssh`  
**Target id (lab):** `beelzebub-ssh` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.0/beelzebub/ssh/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.0/beelzebub/ssh/full/proof/full-run.cast) |

**Report hub:** [beelzebub / ssh](../conformance/latest/results-5.0.0/beelzebub/ssh/index.md) · [Tutorial](../conformance/latest/results-5.0.0/beelzebub/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.0/beelzebub/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.0/beelzebub/ssh/EXECUTION-STEPS.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 55.3 | 0.30 | PARTIAL | accepted null ID |
| Module B: Behavioral Realism | 6.2 | 0.15 | PARTIAL | Server '[beelzebub-lab]:2222' not found in known_hosts |
| Module C: Telemetry Assurance | 0.0 | 0.25 | FAILED | declared native_json but no matching records |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | UHBS v5: containment verdict from critical controls; defense-in-depth score is d |
| Module E: Scalability & Latency | 20.0 | 0.10 | PARTIAL | P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded (INCOMPLETE) |

Archived 4.x 59.88 / D is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : beelzebub-ssh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : ssh
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  55.3/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :   6.2/100       0.15     PARTIAL (Server '[beelzebub-lab]:2222' not found in known_hosts)
Module C: Telemetry Assurance       :   0.0/100       0.25     FAILED (declared native_json but no matching records)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (UHBS v5: containment verdict from critical controls; defense-in-depth score is diagnostic only; no 95-point floor)
Module E: Scalability & Latency     :  20.0/100       0.10     PARTIAL (P50=0.0ms P95=0.0ms P99=0.0ms TPS_limit=3000.0ms proto=ssh)
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

## Replication

Re-run commands are in the [execution steps](../conformance/latest/results-5.0.0/beelzebub/ssh/EXECUTION-STEPS.md).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
