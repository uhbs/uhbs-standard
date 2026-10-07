# Endlessh — published UHBS lab reports

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** Low-Interaction · **Protocol:** `ssh_tarpit`  
**Target id:** `endlessh-ssh_tarpit` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **34.05** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **33.95** | F | 0.5 | INCOMPLETE / GATE_FAILED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 79.0 | 0.30 | PASSED | fsm=70 nego=70 timing=100 |
| Module B: Behavioral Realism | 25.0 | 0.15 | PARTIAL | no state probe implemented |
| Module C: Telemetry Assurance | 0.0 | 0.25 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 75.0 | GATE | PASSED | User=(empty→root) UsernsMode=(empty) |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 1.0ms) |
| Module F: Static Code Audit | 67.4 | 0.20 | PARTIAL | semgrep error/critical=2 total=2 |
| Safety Gate δ_C | 0.5 | GATE | — | Gate GATE_FAILED; δ_C=0.5 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : endlessh
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : ssh_tarpit
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  79.0/100       0.30     PASSED (fsm=70 nego=70 timing=100)
Module B: Behavioral Realism        :  25.0/100       0.15     PARTIAL (no state probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 1.0ms))
Module F: Static Code Audit         :  67.4/100       0.20     PARTIAL (semgrep error/critical=2 total=2)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 33.95 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../reports/READING-UHQS.md)
- Tutorial & methodology: see the product hub for this decoy

> Named product is evaluation proof only — not a UHBS endorsement.
