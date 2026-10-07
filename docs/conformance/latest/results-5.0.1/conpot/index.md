# Conpot — published UHBS lab reports

**Status:** Informative · evaluation proof  
**UHBS:** 5.0.1 · **Class:** ICS-SCADA · **Protocol:** `modbus`  
**Target id:** `conpot-modbus` · **Evaluated:** 2026-09-28

| Run | UHQS | Grade | δ_C | Verdict | Artifacts |
| --- | ---: | --- | --- | --- | --- |
| [Quick](quick/SCORECARD.txt) | **59.46** | D | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](quick/report.json) |
| [Full](full/SCORECARD.txt) (authoritative) | **61.94** | D | 1 | INCOMPLETE / GATE_PASSED | [`report.json`](full/report.json) |

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 79.0 | 0.35 | PASSED | resp=000100000003018302 |
| Module B: Behavioral Realism | 5.0 | 0.20 | PARTIAL | write step (FC 0x06) failed/unacknowledged: resp=000200000003018602 |
| Module C: Telemetry Assurance | 0.0 | 0.15 | INCOMPLETE | UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4 |
| Module D: Safety & Containment (C) | 83.3 | GATE | PASSED | Memory=0 NanoCpus=0 PidsLimit=0 |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | service alive after load (connect 0.6ms) |
| Module F: Static Code Audit | 70.0 | 0.20 | PASSED | 2 static private keys: conpot/templates/default/ssl/ssl.key, conpot/templates/kamstrup_382/ssl/ssl.key |
| Safety Gate δ_C | 1 | GATE | — | Gate GATE_PASSED; δ_C=1 applied to composite |

## Full scorecard (verbatim)

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : conpot
System Profile Class  : ICS-SCADA
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_PASSED
Protocols             : modbus
Evaluation Date       : 2026-09-28
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  79.0/100       0.35     PASSED (resp=000100000003018302)
Module B: Behavioral Realism        :   5.0/100       0.20     PARTIAL (write step (FC 0x06) failed/unacknowledged: resp=000200000003018602)
Module C: Telemetry Assurance       :   0.0/100       0.15     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  83.3/100       GATE     PASSED (Memory=0 NanoCpus=0 PidsLimit=0)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (service alive after load (connect 0.6ms))
Module F: Static Code Audit         :  70.0/100       0.20     PASSED (2 static private keys: conpot/templates/default/ssl/ssl.key, conpot/templates/kamstrup_382/ssl/ssl.key)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=1.0; defense-in-depth C=83.33; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 61.94 / 100
OVERALL EVALUATION GRADE              : GRADE D (Needs Remediation)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```

## Replication

- Execution steps: [EXECUTION-STEPS.md](EXECUTION-STEPS.md)
- How to read UHQS: [CTI / blue-team guide](../../../reports/READING-UHQS.md)
- Tutorial & methodology: see the product hub for this decoy

> Named product is evaluation proof only — not a UHBS endorsement.
