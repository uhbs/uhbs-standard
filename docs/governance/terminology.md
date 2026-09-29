# Terminology

**Status:** Informative companion to the v5 specification

- **Assessment status** — Completeness state. `COMPLETE` means all applicable
  mandatory checks produced valid outcomes and evidence; `INCOMPLETE` means they did not.
- **Critical-control verdict** — Module D eligibility result:
  `GATE_PASSED`, `GATE_FAILED`, or `INCOMPLETE`.
- **Assessment outcome** — The combined status and critical-control verdict.
  It is reported before any score or grade.
- **UHQS** — The 0–100 weighted composite for a `COMPLETE + GATE_PASSED`
  assessment under a named `scoring_model_id`.
- **Grade** — Letter representation of an eligible UHQS. It is not a
  certification, product endorsement, or regulatory-compliance result.
- **Ungraded** — `uhqs = null` and no letter grade because the assessment is
  incomplete or a critical control failed. Ungraded is not letter F.
- **Module D diagnostic** — Defense-in-depth score reported for analysis; it is
  not weighted into v5 UHQS and cannot override a critical-control failure.
- **Assurance level** — Evidence provenance/reproducibility label:
  `SELF_ASSESSED`, `REPRODUCIBLE_LAB`, or `INDEPENDENTLY_REPRODUCED`.
  It is not confidence, certification, accreditation, or legal assurance.
- **Target Profile Specification (TPS)** — Declared class, protocol,
  capabilities, requirements, and thresholds that scope an assessment.
- **Evidence pack** — Manifested records supporting check outcomes,
  applicability, target identity, environment, and reproducibility.
- **Normative** — Required to claim UHBS conformance.
- **Informative** — Guidance or mapping that does not alter conformance or UHQS.
- **Historical v4 result** — Preserved result produced by a v4 scoring model.
  It must not be silently recalculated or compared as if it used v5 assurance rules.

Normative definitions and conflict resolution remain in the
[specification](../specification/status.md) and
[RFC 0003](../rfcs/0003-scoring-assurance.md).
