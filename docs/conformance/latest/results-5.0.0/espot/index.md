# ESPot — published UHBS lab reports (results-5.0.0)

**Proof label:** [mycert/ESPot](https://github.com/mycert/ESPot)  
**Class / protocol:** `Web-API` · HTTP · port `9200`  
**UHBS:** 5.0.0 · evaluation proof only (not an endorsement)  
**Upstream:** `master` @ `0b126a7783da69d543239606df59211c5d21f1db`

## Results at a glance

| Mode | UHQS | Grade | δ_C | Safety Gate | Folder |
| --- | --- | --- | --- | --- | --- |
| **Quick** | **ungraded** | — | 0.0 | INCOMPLETE | [`quick/`](quick/README.md) |
| **Full** | **ungraded** | — | 0.0 | INCOMPLETE | [`full/`](full/README.md) |

Cast: [`full/proof/full-run.cast`](full/proof/full-run.cast)  
Fixture: [`../../../fixtures/espot-web-api.scorecard.json`](../../../fixtures/espot-web-api.scorecard.json)  
Archive: [`../../../archive/v5.0.0/espot/`](../../../archive/v5.0.0/espot/)

v5 Safety Gate leaves this HTTP decoy **ungraded** (Module C declared-format + Module D non-SSH gateway/packet evidence). Do not cite archived 4.x 63.33 / D as the current result.

## Contents

| Document | Purpose |
| --- | --- |
| [TUTORIAL.md](TUTORIAL.md) | Reproduce clone / Docker / quick / full |
| [METHODOLOGY.md](METHODOLOGY.md) | Runtime, images, limitations |
| [EXECUTION-STEPS.md](EXECUTION-STEPS.md) | Exact command sequence |
| [`quick/SCORECARD.txt`](quick/SCORECARD.txt) | Quick scorecard |
| [`full/SCORECARD.txt`](full/SCORECARD.txt) | Full scorecard (authoritative) |

## Module snapshot (full)

| Module | Score | Status |
| --- | --- | --- |
| A Protocol | 86.75 | PASSED (`HTTP/9.9` still returns 200) |
| B Behavior | 65.0 | PARTIAL |
| C Telemetry | 0.0 | INCOMPLETE (declared-format) |
| D Containment | 0.0 | INCOMPLETE (non-SSH gateway/packet) |
| E Scale | 100.0 | PASSED |
| F Static | 66.64 | PARTIAL (semgrep 2 error/critical of 6) |

Back to the [results-5.0.0 index](../index.md).
