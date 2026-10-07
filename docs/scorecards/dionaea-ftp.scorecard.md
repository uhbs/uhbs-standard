# Scorecard: dionaea — ftp (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Low-Interaction · **Protocol / surface:** `ftp`  
**Target id (lab):** `dionaea-ftp` · **Evaluation date:** 2026-09-27  
**Verdict:** INCOMPLETE / GATE_FAILED (`uhqs-v5.2-measured-renorm`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | 22.46| F| 0.5| [quick SCORECARD](../conformance/latest/results-5.0.1/dionaea/ftp/quick/SCORECARD.txt) |
| **Full (authoritative)** | **22.4** | **F** | **0.5** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.1/dionaea/ftp/full/proof/full-run.cast) |

**Report hub:** [dionaea / ftp](../conformance/latest/results-5.0.1/dionaea/ftp/index.md) · [Tutorial](../conformance/latest/results-5.0.1/dionaea/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/dionaea/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/dionaea/ftp/EXECUTION-STEPS.md)

Archived 4.x 57.96 / D is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : dionaea-ftp
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : ftp
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  16.9/100       0.30     PARTIAL (codes=[220, 530, 530])
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1023.7ms P95=1056.7ms P99=1058.5ms TPS_limit=150.0ms proto=ftp)
Module F: Static Code Audit         :  66.3/100       0.20     PARTIAL (bandit HIGH=9)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 22.40 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```
