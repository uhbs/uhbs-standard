# Beelzebub (UHBS multi-protocol proof) (mcp)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Web-API · **Protocol:** `mcp`  
**Target id:** `beelzebub-mcp` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **30.55** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **31.44** | F | 0.5 | COMPLETE / GATE_FAILED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 60.1 | 0.25 | PARTIAL | allowed tools/list before notifications/initialized |
| Module B: Behavioral Realism | 94.3 | 0.20 | PASSED | survived binary blast |
| Module C: Telemetry Assurance | 0.0 | 0.20 | PARTIAL | http_inject markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 100.0 | 0.15 | PASSED | service alive after load (connect 0.2ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | semgrep error/critical=7 total=41 |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

## Full scorecard (verbatim)

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

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
