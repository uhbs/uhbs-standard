# reports / echidra — quick artifacts

**UHQS 57.33 / D** · UHBS lab harness v4.0.0 · δ_C=1.0

This page is the human-readable landing for the UHBS-Lab run artifacts. The authoritative proof is the verbatim scorecard below (same bytes as `SCORECARD.txt`).

## Verbatim SCORECARD.txt

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v4.0
====================================================================================
Target System         : echidra
System Profile Class  : Low-Interaction
Protocols             : ssh
Evaluation Date       : 2026-09-15
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  23.5/100       0.30     PARTIAL (accepted null ID)
Module B: Behavioral Realism        :  25.0/100       0.15     PARTIAL (marker missing across sessions)
Module C: Telemetry Quality         : 100.0/100       0.25     PASSED (telemetry_dir missing — set TPS/inventory telemetry_dir for C1 schema gates)
Module D: Safety & Containment (C)  : 100.0/100       GATE     PASSED (stable)
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1114.3ms P95=1736.3ms P99=1809.1ms TPS_limit=100.0ms proto=ssh)
Module F: Static Code Audit         :  80.1/100       0.20     PASSED (1 hardcoded SSH banners: honeypot/core/persona.py)
------------------------------------------------------------------------------------
SAFETY GATE MULTIPLIER                : δ_C = 1.0 (Containment Score C = 100.0 >= 95)
FINAL COMPOSITE SCORE (UHQS 4.0)      : 57.33 / 100
OVERALL EVALUATION GRADE              : GRADE D (Needs Remediation)
====================================================================================
```

## Other artifacts

- [`report.json`](report.json) — per-check machine evidence
- [`MANIFEST.json`](MANIFEST.json) — SHA-256 digests
- [`run-meta.json`](run-meta.json) — provenance
- [`uhbs-run.log`](uhbs-run.log) — console transcript

