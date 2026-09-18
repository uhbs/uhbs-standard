# RFCs

Normative specification changes for UHBS are proposed here as RFCs (request for comments). This process documents **proposed** changes to the evaluation framework — it is not a standards body, steering committee, or consortium process.

## Index

| RFC | Title | Status |
| --- | --- | --- |
| [0000](0000-template.md) | Template | — |
| [0001](0001-uhbs-4.0-baseline.md) | UHBS 4.0.1 Baseline | Accepted |
| [0002](0002-experimental-benchmark-extensions.md) | Experimental Benchmark Extensions | Draft (informative) |
| [0003](0003-scoring-assurance.md) | UHQS Scoring and Assurance Redesign (v5) | Accepted (for implementation) |

Calibration notes for RFC 0003: [calibration/v5-sensitivity.md](calibration/v5-sensitivity.md).

## How to use this folder

1. Copy [`0000-template.md`](0000-template.md) to a new numbered file when opening a proposal.
2. Describe the problem, the proposed change to UHQS / schemas / protocols, and migration impact.
3. Keep math truth in `src/uhbs_core/uhqs_math.py` if scoring changes; do not invent a second UHQS implementation.
4. Reference [GOVERNANCE.md](https://github.com/uhbs/uhbs-standard/blob/main/GOVERNANCE.md) in the repository root for maintainer expectations.

## What analysts should know

- **Accepted for implementation** RFCs (e.g. RFC 0003) define the target normative surface for the stated UHBS version; treat draft RFCs as discussion only until accepted **and** reflected in a released version.
- Published lab grades and scorecards under `docs/conformance/` that lack
  `scoring_model_id = uhqs-v5.0.0-critical-gate-binary` remain **historical UHQS 4.x**
  evaluation proof. Existing URLs stay resolvable; v5 fixtures live under
  `docs/conformance/fixtures/v5/`.

## Trust

RFC text is discussion or design material for the framework. It does not create mandatory industry requirements or imply multi-party governance that does not exist today. Independent technical review is not committee approval.
