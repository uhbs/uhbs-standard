# Scorecard: dionaea — smb (results-5.0.1)

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **5.0.1** · **Class:** Low-Interaction · **Protocol / surface:** `smb`  
**Target id (lab):** `dionaea-smb` · **Evaluation date:** 2026-09-27  
**Verdict:** INCOMPLETE / GATE_FAILED (`uhqs-v5.2-measured-renorm`)

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| Quick | 28.98| F| 0.5| [quick SCORECARD](../conformance/latest/results-5.0.1/dionaea/smb/quick/SCORECARD.txt) |
| **Full (authoritative)** | **33.1** | **F** | **0.5** | Verbatim SCORECARD below + [`full-run.cast`](../conformance/latest/results-5.0.1/dionaea/smb/full/proof/full-run.cast) |

**Report hub:** [dionaea / smb](../conformance/latest/results-5.0.1/dionaea/smb/index.md) · [Tutorial](../conformance/latest/results-5.0.1/dionaea/TUTORIAL.md) · [Methodology](../conformance/latest/results-5.0.1/dionaea/METHODOLOGY.md) · [Execution steps](../conformance/latest/results-5.0.1/dionaea/smb/EXECUTION-STEPS.md)

Archived 4.x 52.01 / D is **not** the current published result.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v5.0.1
====================================================================================
Target System         : dionaea-smb
System Profile Class  : Low-Interaction
Scoring Model         : uhqs-v5.2-measured-renorm
Assessment Status     : INCOMPLETE
Critical Controls     : GATE_FAILED
Protocols             : smb
Evaluation Date       : 2026-09-27
Evaluation Type       : Full-Spectrum (Static Audit + Dynamic Sandbox)
Environment           : Isolated Sandbox
MCP Surface Depth     : unknown
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  70.4/100       0.30     PASSED (median=0.456ms pstdev=200.658ms (target jitter often <2ms vs native))
Module B: Behavioral Realism        :  65.0/100       0.15     PARTIAL (no payload probe implemented)
Module C: Telemetry Assurance       :   0.0/100       0.25     INCOMPLETE (UHBS v5 Module C: declared-format validation; sink-side C2; ground-truth C4)
Module D: Safety & Containment (C)  :  75.0/100       GATE     PASSED (User=(empty→root) UsernsMode=(empty))
Module E: Scalability & Latency     :  55.0/100       0.10     PARTIAL (P50=1023.7ms P95=1059.0ms P99=1065.4ms TPS_limit=150.0ms proto=smb)
Module F: Static Code Audit         :  66.3/100       0.20     PARTIAL (bandit HIGH=9)
------------------------------------------------------------------------------------
SAFETY GATE / CRITICAL CONTROLS        : INCOMPLETE (δ_C=0.5; defense-in-depth C=75.0; composite still published)
FINAL COMPOSITE SCORE (UHQS 5.0.1)      : 33.10 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
scoring_model_id                      : uhqs-v5.2-measured-renorm
====================================================================================
```
