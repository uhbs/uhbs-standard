# Universal Scoring Methodology (UHQS 5.0.1)

**Status:** Normative  
**scoring_model_id:** `uhqs-v5.2-measured-renorm` (harness; supersedes the
historical `uhqs-v5.0-critical-gate-diagnostic` null-UHQS cliff for published runs)

The key words **MUST**, **SHOULD**, and **MAY** are interpreted as in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). See
[Status of This Document](status.md). Normative design intent is recorded in
[RFC 0003](../rfcs/0003-scoring-assurance.md).

## Assessment status and scoring model identity

Every scorecard **MUST** declare:

| Field | Requirement |
| --- | --- |
| `scoring_model_id` | Immutable model identity; reference harness uses `uhqs-v5.2-measured-renorm` |
| `assessment_status` | `COMPLETE` or `INCOMPLETE` |
| `critical_control_verdict` | `GATE_PASSED`, `GATE_FAILED`, or `INCOMPLETE` |

Implementations **MUST NOT** conflate `scoring_model_id` with `specification_version` / `uhbs_version`. Historical UHQS 4.x scorecards remain interpretable only under their original model.

### Always-numeric results

When module scores are present, `uhqs` **MUST** be a numeric composite (not `null`).
Safety honesty lives in `assessment_status` / `critical_control_verdict` and δ_C:

- Module D diagnostic **MUST** be numeric and **MUST NOT** use stub `0.0` for unmeasured paths (floor `1.0` when no scored checks ran).
- `GATE_PASSED` implies Module D diagnostic > 0.
- Letter grades **MAY** still be emitted from the numeric UHQS; operators **MUST** read the verdict fields before treating a run as approved.

## Composite Score Formula

The **Universal Honeypot Quality Score (UHQS)** **MUST** be computed as a
normalized value from **0 to 100** from measured modules A/B/C/E/F (unmeasured
modules excluded; remaining weights renormalized):

\[
\mathrm{UHQS} = \delta_C \cdot \frac{\sum_i w_i \cdot S_i}{\sum_i w_i}
\]

for measured \(i \in \{A,B,C,E,F\}\).

!!! note "Measured vs unmeasured (harness enforcement, since the 5.0.1 rescore)"
    A module is **unmeasured** when the harness marks it incomplete (e.g. the
    telemetry sink checks never ran, or SAST was skipped) — it is excluded and
    the remaining weights renormalize. A module that **ran and failed** (e.g.
    declared telemetry format does not match the records) is a *measured zero*
    and counts with full weight. Composites renormalized over fewer than
    **4 of 5** measured modules are published with
    `assessment_status=INCOMPLETE` (partial measurement — not comparable
    across units).

![UHQS formula explainer: weighted modules A–F multiplied by Safety Gate δ_C from Module D](../assets/uhqs-formula-explainer.svg)

| Symbol | Meaning |
| --- | --- |
| \(S_A, S_B, S_C, S_E, S_F\) | Normalized scores (0–100) for Modules A, B, C, E, and F |
| \(w_A, w_B, w_C, w_E, w_F\) | Dimension weights assigned by profile class |
| \(\delta_C\) | Critical-control gate multiplier (see table below) |

Implementations **MUST** round UHQS to **two decimal places** (half-up /
Python `round` semantics as used by the reference harness).

!!! note
    Module D does **not** appear as a weighted term \(w_D \cdot S_D\). Containment is a
    **gate factor** (`critical_control_verdict` → δ_C). The defense-in-depth Module D
    score is diagnostic only and **MUST NOT** clear or weaken the gate. The v4
    `max(score, 95)` floor and attestation-only credit are removed.

    The public landing page typesets these formulas with [KaTeX](https://katex.org/); this document is the normative source.

## Critical-control gate (\(\delta_C\))

Containment is **not** averaged into the weighted sum. Under measured-renorm:

| `critical_control_verdict` | \(\delta_C\) | UHQS |
| --- | ---: | --- |
| `GATE_PASSED` | 1.0 | base × 1.0 |
| `INCOMPLETE` | 1.0 | base × 1.0 (verdict remains `INCOMPLETE`) |
| `GATE_FAILED` | 0.5 | base × 0.5 |

Continuous multipliers of the form \((C/95)^k\) are **not** used: they remain
arbitrary without a full live calibration corpus (see
[v5 sensitivity notes](../rfcs/calibration/v5-sensitivity.md)).

## Check outcomes (denominator rules)

Module scores aggregate catalog checks with outcomes
`PASS` | `FAIL` | `NOT_APPLICABLE` | `NOT_TESTED` | `ERROR`.

- Only `NOT_APPLICABLE` **MAY** leave the scoring denominator (requires machine rule + rationale).
- Applicable mandatory `NOT_TESTED` or `ERROR` **MUST** make the assessment `INCOMPLETE` (status field; UHQS still numeric).
- `FAIL` earns zero credit and **MUST** remain in the denominator.

## Profile-Adaptive Weight Distributions

Weights **MUST** match the profile class declared in the TPS. All rows sum to **1.00**.

| Target Profile Category | Class enum | \(w_A\) | \(w_B\) | \(w_C\) | \(w_E\) | \(w_F\) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| POSIX / Interactive Shells | `POSIX-Shell` | 0.20 | 0.25 | 0.20 | 0.15 | 0.20 |
| GenAI-augmented shells | `GenAI-Shell` | 0.20 | 0.25 | 0.20 | 0.15 | 0.20 |
| Low-Interaction Emulators | `Low-Interaction` | 0.30 | 0.15 | 0.25 | 0.10 | 0.20 |
| Industrial / OT / SCADA | `ICS-SCADA` | 0.35 | 0.20 | 0.15 | 0.10 | 0.20 |
| Web & Cloud APIs | `Web-API` | 0.25 | 0.20 | 0.20 | 0.15 | 0.20 |
| Database decoys | `Database` | 0.25 | 0.25 | 0.20 | 0.10 | 0.20 |

Industrial/OT/SCADA profiles assign the highest protocol fidelity weight (**0.35**).
`GenAI-Shell` **MUST** use the same weights as `POSIX-Shell` unless an accepted RFC
changes that mapping.

## Letter Grades (Normative Banding)

Letter grades map from numeric UHQS. Operators **MUST** also read
`critical_control_verdict` / `assessment_status` — a letter does not mean the Safety
Gate passed.

| UHQS | Grade | Label |
| ---: | :---: | --- |
| 90 – 100 | A | Highest composite band |
| 80 – 89.99 | B | High composite band |
| 70 – 79.99 | C | Moderate composite band |
| 50 – 69.99 | D | Low composite band |
| &lt; 50 | F | Lowest composite band |

## Operational decision boundary (Informative)

UHQS bands classify the eligible composite; they do not approve or prohibit
production use. Historical guidance called **UHQS > 80** plus a passing Safety
Gate a “Production Baseline.” In v5, organizations that retain this value must
treat it as their own candidate internal threshold and document separate risk,
architecture, privacy, legal, and operational approval. Live calibration and
independent technical review of production-facing thresholds remain incomplete;
see [Status of This Document](status.md).

## Reference computation

These normative numbers **MUST** match `uhbs score` and `uhbs_core.uhqs_math.compute_uhqs`
(CLI / MCP / harness wrappers) under `scoring_model_id = uhqs-v5.2-measured-renorm`.

**v4 historical note:** Published fixtures under `docs/conformance/fixtures/` (root) were
graded under UHQS 4.x and **MUST NOT** be re-derived as v5 grades without re-running
labs. Synthetic v5 golden vectors live under `docs/conformance/fixtures/v5/`.
