# Status of This Document

**Status:** Experimental  
**Specification version:** 5.0.0  
**scoring_model_id:** `uhqs-v5.0.0-critical-gate-binary`  
**Keywords:** The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this
document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals, as shown here.

## Completeness disclosure (v5)

UHBS 5.0.0 requires **assessment completeness** before a letter grade:

- Applicable mandatory checks that are `NOT_TESTED` or `ERROR` yield
  `assessment_status = INCOMPLETE`, `uhqs = null`, and **no letter grade** (Ungraded).
- Only `NOT_APPLICABLE` may leave a scoring denominator, and only with a machine
  applicability rule plus written rationale.
- Live known-good/known-bad calibration across profile classes remains **partial at
  ship time**. Until representative live reruns and independent technical review
  responses are published, grades under this model are **lab / reference** grades
  tied to `scoring_model_id`, not production certification. See
  [RFC 0003](../rfcs/0003-scoring-assurance.md) and
  [v5 sensitivity notes](../rfcs/calibration/v5-sensitivity.md).

## Normative vs Informative

| Kind | Meaning |
| --- | --- |
| **Normative** | Requirements that define UHBS conformance |
| **Informative** | Guidance, examples, motivation — not required for conformance |

## Conformance levels

### UHBS-Core (REQUIRED for claiming schema conformance)

An implementation claiming **UHBS-Core** conformance **MUST**:

1. Accept a TPS `profile.yaml` validating against `schemas/profile.schema.json`
2. Emit a scorecard validating against `schemas/scorecard.schema.json`
3. Compute UHQS using the normative formula and critical-control gate under
   `scoring_model_id = uhqs-v5.0.0-critical-gate-binary`
4. Apply profile-class weights that match § Profile-Adaptive Weight Distributions
5. Pass public v5 conformance fixtures under `docs/conformance/fixtures/v5/`
6. Preserve the ability to validate historical v4 scorecards with `schemas/v4/`

### UHBS-Lab (RECOMMENDED for production evaluations)

An implementation claiming **UHBS-Lab** conformance **MUST** satisfy UHBS-Core and **MUST**:

1. Execute Modules A–F with explicit check outcomes (not silent skips)
2. Emit an evidence pack validating against `schemas/evidence-pack.schema.json`
3. Record Module D critical-control evidence (attestation alone is insufficient)
4. Include step-level check results with digests, applicability rationales, and
   `assurance_level` for official/registry scorecards
5. Disclose incomplete modules as Ungraded rather than inventing a letter grade

The reference harness that implements UHBS-Lab is described in
[reference-implementation.md](../reference-implementation.md).

## Project posture

UHBS is an open-source **evaluation framework** (Apache-2.0). It is **not** a standards
body, consortium, or multi-party committee. Claims about committees, neutral
org hosting, and independent adopters belong only on
[ROADMAP.md](../roadmap.md) (Phase 6) until they are real. Independent technical
review of RFC 0003 is required for production-facing thresholds; it is **not**
committee approval.

## Candidate internal deployment threshold (Informative)

Language such as "mandatory industry standard" **MUST NOT** be used for UHBS
today. Organizations **MAY** adopt UHBS as an **internal** gate.

Historical project guidance used **UHQS > 80** plus a passing Safety Gate as a
“Production Baseline.” Under v5 this is a **candidate internal threshold**, not a
validated production baseline:

- only `assessment_status = COMPLETE` and
  `critical_control_verdict = GATE_PASSED` are eligible for UHQS or a grade;
- a passing outcome is necessary evidence, not sufficient authorization to deploy;
- the organization must separately assess architecture, threat model, privacy,
  legal authority, operations, monitoring, and residual risk; and
- the numeric threshold requires independent review and broader live calibration
  before UHBS can present it as production-facing guidance.

Organizations that retain an internal numeric threshold must document it as
their own risk decision, not as UHBS certification or industry consensus.
