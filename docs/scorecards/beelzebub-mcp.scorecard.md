# Scorecard: beelzebub — mcp (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Web-API · **Protocol / surface:** `mcp`  
**Target id (lab):** `beelzebub-mcp` · **Evaluation date:** 2026-09-28  
**Verdict:** COMPLETE / GATE_FAILED (`uhqs-v5.2-measured-renorm`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | 30.55| F| 0.5| [quick SCORECARD](../conformance/latest/results-5.0.1/beelzebub/mcp/quick/SCORECARD.txt) |
| **Full (authoritative)** | **31.44** | **F** | **0.5** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.1/beelzebub/mcp/full/proof/full-run.cast) |

**Report hub:** [beelzebub / mcp](../conformance/latest/results-5.0.1/beelzebub/mcp/index.md) · [Tutorial](../conformance/latest/results-5.0.1/beelzebub/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/beelzebub/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/beelzebub/mcp/EXECUTION-STEPS.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 60.1 | 0.25 | PARTIAL | allowed tools/list before notifications/initialized |
| Module B: Behavioral Realism | 94.3 | 0.20 | PASSED | survived binary blast |
| Module C: Telemetry Assurance | 0.0 | 0.20 | PARTIAL | http_inject markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 100.0 | 0.15 | PASSED | service alive after load (connect 0.2ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

Archived 4.x 42.93 / F is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : beelzebub-mcp
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_FAILED
Protocols             : mcp
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : interactive
MCP Surface Reason    : exercised allowlisted tool tool:system-log
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  60.1/100       0.25     PARTIAL (allowed tools/list before notifications/initialized)
Module B: Behavioral Realism        :  94.3/100       0.20     PASSED (survived binary blast)
Module C: Telemetry Assurance       :   0.0/100       0.20     PARTIAL (http_inject markers=[] malformed=0)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.2ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (semgrep error/critical=7 total=41)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_FAILED (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 31.44 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

Re-run commands are in the [execution steps](../conformance/latest/results-5.0.1/beelzebub/mcp/EXECUTION-STEPS.md).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
