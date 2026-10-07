# HoneyMCP (UHBS MCP proof) (mcp)

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Web-API · **Protocol:** `mcp`  
**Target id:** `honeymcp-mcp` · **Evaluated:** 2026-09-27

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **56.86** | D | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **58.59** | D | 1 | COMPLETE / GATE_PASSED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 46.5 | 0.25 | PARTIAL | allowed tools/list before notifications/initialized |
| Module B: Behavioral Realism | 94.3 | 0.20 | PASSED | survived binary blast |
| Module C: Telemetry Assurance | 0.0 | 0.20 | PARTIAL | http_inject markers=[] malformed=0 |
| Module D: Safety & Containment (C) | 83.3 | GATE | PASSED | Memory=0 NanoCpus=0 PidsLimit=0 |
| Module E: Scalability & Latency | 100.0 | 0.15 | PASSED | service alive after load (connect 0.5ms) |
| Module F: Static Code Audit | 65.5 | 0.20 | PARTIAL | 3 static private keys: personas/filesystem-admin.yaml, src/detect/secret_exfil.rs, src/bin/probes.rs |
| Safety Gate δ_C | 1 | GATE | — | Gate GATE_PASSED; δ_C=1 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : honeymcp-mcp
System Profile Class  : Web-API
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : COMPLETE
Critical Controls     : GATE_PASSED
Protocols             : mcp
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : interactive
MCP Surface Reason    : exercised allowlisted tool get_caller_identity
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  46.5/100       0.25     PARTIAL (allowed tools/list before notifications/initialized)
Module B: Behavioral Realism        :  94.3/100       0.20     PASSED (survived binary blast)
Module C: Telemetry Assurance       :   0.0/100       0.20     PARTIAL (http_inject markers=[] malformed=0)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     : 100.0/100       0.15     PASSED (service alive after load (connect 0.5ms))
Module F: Static Code Audit         :  65.5/100       0.20     PARTIAL (3 static private keys: personas/filesystem-admin.yaml, src/detect/secret_exfil.rs, src/bin/probes.rs)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : GATE_PASSED (δ_C=1.0; defense-in-depth C=83.33)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 58.59 / 100
OVERALL EVALUATION GRADE              : GRADE D (Needs Remediation)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../../reports/READING-UHQS.md)
- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)

> Named product is evaluation proof only — not a UHBS endorsement.
