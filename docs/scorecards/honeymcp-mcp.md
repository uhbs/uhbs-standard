# Scorecard: honeymcp — mcp (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Web-API · **Protocol:** `mcp`  
**Target id (lab):** `honeymcp-mcp` · **Evaluation date:** 2026-09-26  
**Verdict:** INCOMPLETE / INCOMPLETE / ungraded (`uhqs-v5.0-critical-gate-diagnostic`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | ungraded | — | 0.0 | [quick SCORECARD](../conformance/latest/results-5.0.1/honeymcp/mcp/quick/SCORECARD.txt) |
| **Full (authoritative)** | **ungraded** | **—** | **0.0** | Verbatim SCORECARD below |

**Report hub:** [honeymcp / mcp](../conformance/latest/results-5.0.1/honeymcp/mcp/index.md) · [Tutorial](../conformance/latest/results-5.0.1/honeymcp/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/honeymcp/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/honeymcp/mcp/EXECUTION-STEPS.md)

## Proof: module scores (full run)

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 46.5 | 0.25 | PARTIAL | allowed tools/list before notifications/initialized |
| Module B: Behavioral Realism | 94.3 | 0.20 | PASSED | survived binary blast |
| Module C: Telemetry Assurance | 0.0 | 0.20 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 0.0 | GATE | INCOMPLETE | Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate. |
| Module E: Scalability & Latency | 75.0 | 0.15 | PASSED | P50=927.0ms P95=3928.8ms P99=4238.0ms TPS_limit=3000.0ms proto=mcp |
| Module F: Static Code Audit | 65.5 | 0.20 | PARTIAL | 3 static private keys: personas/filesystem-admin.yaml, src/detect/secret_exfil.rs, src/bin/probes.rs |
| Safety Gate δ_C | 0.0 | GATE | — | Ungraded when INCOMPLETE/GATE_FAILED |

Archived 4.x letter grades are **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : honeymcp-mcp
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.0-critical-gate-diagnostic
Assessment Status     : INCOMPLETE
Critical Controls     : INCOMPLETE
Protocols             : mcp
Evaluation Date       : 2026-09-26
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : interactive
MCP Surface Reason    : exercised allowlisted tool get_caller_identity
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  46.5/100       0.25     PARTIAL (allowed tools/list before notifications/initialized)
Module B: Behavioral Realism        :  94.3/100       0.20     PASSED (survived binary blast)
Module C: Telemetry Assurance       :   0.0/100       0.20     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :   0.0/100       GATE     INCOMPLETE (Module D v5: non-SSH targets need gateway/packet evidence for critical egress and runtime inspection — attestation alone never clears the gate.)
Module E: Scalability & Latency     :  75.0/100       0.15     PASSED (P50=927.0ms P95=3928.8ms P99=4238.0ms TPS_limit=3000.0ms proto=mcp)
Module F: Static Code Audit         :  65.5/100       0.20     PARTIAL (3 static private keys: personas/filesystem-admin.yaml, src/detect/secret_exfil.rs, src/bin/probes.rs)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : Ungraded — assessment incomplete (mandatory checks NOT_TESTED/ERROR)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : null (Ungraded — no composite UHQS)
OVERALL EVALUATION GRADE              : — (no letter grade)
scoring_model_id                      : uhqs-v5.0-critical-gate-diagnostic
====================================================================================
```

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
