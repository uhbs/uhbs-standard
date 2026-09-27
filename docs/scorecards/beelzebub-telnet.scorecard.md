# Scorecard: beelzebub — telnet (results-5.0.0)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.0** · **Class:** Low-Interaction · **Protocol / surface:** `telnet`  
**Target id (lab):** `beelzebub-telnet` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.0/beelzebub/telnet/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.0/beelzebub/telnet/full/proof/full-run.cast) |

**Report hub:** [beelzebub / telnet](../conformance/latest/results-5.0.0/beelzebub/telnet/index.md) · [Tutorial](../conformance/latest/results-5.0.0/beelzebub/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.0/beelzebub/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.0/beelzebub/telnet/EXECUTION-STEPS.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 30.0 | 0.30 | PARTIAL | no IAC (0xFF) byte in response — not real Telnet: recv=b'\r\nlogin: ' |
| Module B: Behavioral Realism | 65.0 | 0.15 | PARTIAL | no payload probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress an |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 1.0ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded (INCOMPLETE) |

Archived 4.x 47.89 / F is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.0
====================================================================================
Target System         : beelzebub-telnet
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : telnet
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  30.0/100       0.30     PARTIAL (no IAC (0xFF) byte in response — not real Telnet: recv=b'\r\nlogin: ')
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 1.0ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.0)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

## Replication

Re-run commands are in the [execution steps](../conformance/latest/results-5.0.0/beelzebub/telnet/EXECUTION-STEPS.md).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
