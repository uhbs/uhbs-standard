# RFC 0003: UHQS Scoring and Assurance Redesign (v5)

- **Status:** Accepted (for implementation)
- **Author:** Moran Zavdi
- **UHBS version affected:** 5.0.0 → 5.0.0 (breaking)
- **Created:** 2026-09-18
- **Supersedes:** UHQS 4.x scoring integrity assumptions for Modules C/D and skip-credit paths
- **scoring_model_id:** `uhqs-v5.0-critical-gate-diagnostic`

## Problem

UHBS v4 produces numeric grades that overstate measurement confidence:

1. Untested or skipped checks can earn partial credit, so measuring less can raise a score.
2. Module C can award a perfect score with no telemetry (C2-only rescale) and accepts non-STIX objects / keyword “attack” as ATT&CK evidence.
3. Module D can manufacture a Safety Gate pass (`max(score, 95)` floor) and grants attestation-only credit when shell probes are unavailable.
4. Incomplete assessments still receive letter grades, so “not tested” is indistinguishable from “tested and failed.”
5. The δ_C cliff at Module D = 95 creates a discontinuous jump that incentivizes tuning to the threshold rather than evidence-backed containment.

A grade **MUST** mean that a defined set of applicable checks ran, produced evidence, and was evaluated by a pinned scoring model (NIST SP 800-55 Vol. 1–2 measurement principles). UHQS math remains a single source of truth in `src/uhbs_core/uhqs_math.py`; CLI, MCP, and harness wrappers **MUST** stay identical.

## Threat model (CTI / decoy)

An adversary facing a graded decoy may:

| Goal | Description | v5 coverage |
| --- | --- | --- |
| **Detect** | Fingerprint the decoy as non-production | Out of scope for composite UHQS (Modules A/B remain informative fidelity measures) |
| **Poison** | Inject hostile content into telemetry / SIEM | Module C sink-side injection resilience + declared-format validation |
| **Pivot** | Escape containment / unauthorized egress | Module D critical-control verdict (mandatory) |

Detection resistance is deliberately **not** a v5 UHQS eligibility gate.

## Measurement model

### Check outcomes

Every catalog check receives exactly one outcome:

| Outcome | Scoring | Meaning |
| --- | --- | --- |
| `PASS` | Earns its weight | Executed; criterion met; evidence present when required |
| `FAIL` | Zero credit; stays in denominator | Executed; criterion not met |
| `NOT_APPLICABLE` | Leaves denominator | Outside declared capabilities; machine rule + written rationale required |
| `NOT_TESTED` | Never earns credit | Applicable but not executed |
| `ERROR` | Never earns credit | Tool/evidence failure — never remapped to `NOT_APPLICABLE` |

**Only `NOT_APPLICABLE` may leave the scoring denominator.** Excluding unmeasured applicable checks from the denominator is rejected: it permits selective testing.

### Applicability rules

A check may be marked `NOT_APPLICABLE` only when:

1. A machine-evaluable applicability rule in the versioned check catalog evaluates to false for the declared TPS / profile / protocol capabilities, **and**
2. A written rationale is recorded on the check result (human-readable, tied to the rule ID).

Missing rationale **MUST** invalidate the `NOT_APPLICABLE` outcome (treat as incomplete / error path, not as a silent skip).

### Completeness gate

A module may receive a final score only when every applicable **mandatory** check is `PASS` or `FAIL` with required evidence. If any applicable mandatory check is `NOT_TESTED`, `ERROR`, omitted, or unevidenced:

- `assessment_status = INCOMPLETE`
- `uhqs = null`
- **no letter grade** (do **not** invent grade `U`; grades remain outcomes of completed assessments only)

The overall result is reported as **Ungraded** (null UHQS / omitted grade field), not as letter F.

### Module D — containment verdict vs defense-in-depth

Separate two concepts:

1. **Containment verdict** (`critical_control_verdict`): all applicable critical controls **MUST** `PASS` with evidence. Unauthorized egress, exposed runtime sockets, writable escape surfaces, or equivalent boundary violations → `GATE_FAILED`. Missing evidence → verdict `INCOMPLETE` / overall Ungraded.
2. **Defense-in-depth score**: diagnostic 0–100 Module D score for non-critical hardening. It **MUST NOT** average away a critical failure and **MUST NOT** enter the weighted UHQS sum.

Removed from v4:

- `max(score, 95.0)` floor
- Non-SSH attestation ladder that awarded points for `UHBS_AIRGAP_ATTESTED` alone
- Fail-open `containment_measured=False` → `δ_C = 1.0`

`UHBS_AIRGAP_ATTESTED` may describe the environment but **cannot** satisfy a technical control. Non-shell targets need protocol-independent evidence (gateway canaries, namespace/runtime inspection, packet or flow records).

## Composite UHQS (chosen model)

**Chosen model** (after fixture sensitivity analysis; see [calibration/v5-sensitivity.md](calibration/v5-sensitivity.md)):

**`uhqs-v5.0-critical-gate-diagnostic`** — binary critical-control eligibility gate; no composite grade on gate failure or incomplete assessment; when eligible, UHQS is the weighted module sum with \(\delta_C = 1.0\).

When `assessment_status = COMPLETE` and `critical_control_verdict = GATE_PASSED`:

\[
\mathrm{UHQS} = w_A S_A + w_B S_B + w_C S_C + w_E S_E + w_F S_F
\]

with \(\delta_C = 1.0\) (gate already satisfied). Module D’s defense-in-depth score is published but not weighted into the sum (same structural role as v4: containment is a gate, not an averageable term).

When the gate fails or the assessment is incomplete: `uhqs = null`, no letter grade; module diagnostics remain.

Store the choice as immutable `scoring_model_id = uhqs-v5.0-critical-gate-diagnostic`, not merely `uhbs_version`.

Profile-adaptive weights for Modules A/B/C/E/F are unchanged from v5.0.0 unless a later RFC revises them.

## Calibration method

1. **Sensitivity over existing fixtures** — compare v4 δ_C cliff behavior vs binary gate outcomes on published Module D scores (documented in [calibration/v5-sensitivity.md](calibration/v5-sensitivity.md)).
2. **Decision-property checks** (synthetic vectors):

| Property | Result |
| --- | --- |
| Adding an applicable failure cannot improve UHQS | Holds (`FAIL` stays in denominator at zero credit) |
| Omitting a mandatory check cannot produce a grade | Holds (`INCOMPLETE`) |
| Tool `ERROR` cannot become a pass | Holds |
| Critical containment failure always fails the gate | Holds (`GATE_FAILED`, `uhqs=null`) |
| Continuous \((C/95)^k\) multiplier | **Rejected** — still arbitrary without a full live calibration corpus; binary gate is explainable |

3. **Live known-good / known-bad calibration** is **partial at ship time**. Until representative live reruns exist across multiple profile classes (including a non-shell target and telemetry fault injection), published grades under this model are **lab / reference** grades tied to `scoring_model_id`, not production-facing certification thresholds.

## Module C — telemetry assurance

Do **not** require every decoy to emit STIX. The TPS declares `native_event_format` and optional `export_formats`; validators run only for claimed formats (native JSON/JSONL, ECS, OCSF, OTLP, STIX 2.1).

Normative submodules:

| Step | Name | Requirement |
| --- | --- | --- |
| **C1** | Declared-format structural conformance | Schema URI, version, validator version, and errors for claimed formats only |
| **C2** | Sink-side injection resilience | Tagged hostile payloads; one logical event; framing intact at the configured sink |
| **C3** | Required observables | Presence + correctness vs harness ground truth; redaction policies allowed |
| **C4** | Ground-truth completeness / timeliness | Recall, duplicates, latency, clock quality against an immutable truth manifest |
| **C5** | ATT&CK / CTI semantics | When mappings are claimed: resolve against a pinned Enterprise/ICS ATT&CK bundle; record mapping basis, confidence, revoked/deprecated state |

An informative **Collection Capability Profile** may summarize completeness/richness; it is **not** “intelligence quality” and does not alter UHQS.

## Evidence pack and assurance levels

A graded result **MUST** include a schema-valid evidence pack containing at minimum:

- Specification version, `scoring_model_id`, check-catalog ID/hash, harness/plugin versions, command/config digest
- Target artifact identity (source commit and/or container image digest)
- Environment identity sufficient to reproduce timing and containment claims
- Per-check outcome, criterion, applicability decision, timestamps, evidence references and hashes
- Module completeness and evidence coverage
- Manifest digest referenced by the scorecard
- `assurance_level` ∈ {`SELF_ASSESSED`, `REPRODUCIBLE_LAB`, `INDEPENDENTLY_REPRODUCED`}, restricted to evidence actually present

Signature/attestation reference is reserved for a follow-up; hashes prove integrity relative to a trusted manifest only.

## Compatibility / migration

- Breaking change: all v4 fixtures and published grades are **historical** under scoring model UHQS 4.x.
- Existing conformance **report URLs remain resolvable**; pages gain “UHBS v5.0.0 historical scoring model” metadata and links to v5 methodology.
- Parallel validators: v4 schemas retained under `schemas/v4/` for historical scorecards; v5 schemas are authoritative for new evaluations.
- New synthetic golden vectors live under `docs/conformance/fixtures/v5/` (and corresponding reports); do not silently rewrite historical fixture grades.
- Grade letter `U` is **not** used.

## Normative references (pinned intent)

| Reference | Role |
| --- | --- |
| NIST SP 800-55 Vol. 1 & 2 | Measurement design and validation |
| NIST SP 800-53 Rev. 5 / SP 800-53A Rev. 5 | Control / assessment-method concepts (informative mapping) |
| NIST SP 800-92 (final) | Log management; label Rev. 1 as draft if cited |
| NIST SP 800-61 Rev. 3 | Incident-response utility (informative) |
| OASIS STIX 2.1 / TAXII 2.1 | Only where CTI exchange is evaluated |
| MITRE ATT&CK Enterprise/ICS (pinned bundle) | ID resolution when mappings claimed |
| IEC 62443 (edition-specific) | Only for exact OT claims |

Framework mappings remain informative and machine-readable; they are not certification. UHBS is an open-source evaluation framework (Apache-2.0), not a consortium or standards body.

## Alternatives considered

| Alternative | Decision |
| --- | --- |
| Do nothing (keep v4 δ_C cliff + skip credit) | Rejected — overstates assurance |
| Exclude unmeasured checks from the denominator and disclose coverage | Rejected — permits selective testing |
| Continuous \(\delta_C = (C/95)^k\) (e.g. \(k=2.34\)) | Rejected without full live calibration; arbitrary continuity is not validity |
| Invent grade `U` for ungraded | Rejected — incomplete assessments omit the grade / set `uhqs=null` |
| Require universal STIX emission | Rejected — validate declared formats only |
| Keep 95 floor / attestation-only Module D credit | Rejected — manufactures gate passes |

## Security / Safety Gate notes

Lab/network probes remain CLI-only. Do **not** expose containment probes or live telemetry injection via MCP. Critical-control failures are fail-closed. Module D defense-in-depth diagnostics must not weaken the critical-control verdict.

## Independent technical review

Independent technical review of this RFC and published responses is **required** before treating grade thresholds as production-facing. The project remains **single-maintainer**; review is **not** committee or consortium approval.

## Decision

**Accepted for implementation** as the UHBS 5.0.0 scoring and assurance baseline under `scoring_model_id = uhqs-v5.0-critical-gate-diagnostic`. Future normative scoring changes require a new RFC.

## References

- [calibration/v5-sensitivity.md](calibration/v5-sensitivity.md)
- `docs/specification/scoring-formula.md`
- `docs/specification/modules.md`
- `docs/specification/status.md`
- `src/uhbs_core/uhqs_math.py`
- `ROADMAP.md`
- `GOVERNANCE.md`
- `AGENTS.md`
