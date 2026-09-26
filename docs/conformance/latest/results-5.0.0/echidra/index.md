# EchidraOSS — UHBS lab reports (results-5.0.0)

**Proof label:** [Qyleron/EchidraOSS](https://github.com/Qyleron/EchidraOSS)  
**Class / protocol:** `Low-Interaction` · SSH · port `2222`  
**UHBS:** 5.0.0 · evaluation proof only (not an endorsement)  
**Upstream:** `main` @ `50305356ffe49a20459b89b071dc30bb2598e88b`

## Results at a glance

| Mode | UHQS | Grade | δ_C | Safety Gate | Folder |
| --- | --- | --- | --- | --- | --- |
| **Quick** | **ungraded** | — | 1.0 | INCOMPLETE (F skipped) | [`quick/`](quick/README.md) |
| **Full** | **36.58** | **F** | 1.0 | GATE_PASSED | [`full/`](full/README.md) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../fixtures/echidra-low-interaction.scorecard.json`](../../../fixtures/echidra-low-interaction.scorecard.json)  
Archive: [`../../../archive/v5.0.0/echidra/`](../../../archive/v5.0.0/echidra/)

## Contents

| Document | Purpose |
| --- | --- |
| [TUTORIAL.md](TUTORIAL.md) | Reproduce clone / Compose / quick / full |
| [METHODOLOGY.md](METHODOLOGY.md) | Runtime, images, limitations |
| [EXECUTION-STEPS.md](EXECUTION-STEPS.md) | Exact command sequence |
| [`quick/SCORECARD.txt`](quick/SCORECARD.txt) | Quick scorecard |
| [`full/SCORECARD.txt`](full/SCORECARD.txt) | Full scorecard (authoritative) |

## Module snapshot (full)

| Module | Score | Status |
| --- | --- | --- |
| A Protocol | 44.4 | PARTIAL (accepted null ID) |
| B Behavior | 25.0 | PARTIAL (marker missing across sessions) |
| C Telemetry | 0.0 | PARTIAL (declared-format / no markers) |
| D Containment | 0.0 (diagnostic) | GATE_PASSED (stable) |
| E Scale | 55.0 | PARTIAL (P95 ~1813 ms vs 100 ms TPS) |
| F Static | 70.0 | PASSED |

Back to the [results-5.0.0 index](../index.md).
