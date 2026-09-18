# RFC 0003: UHQS Scoring and Assurance Redesign (v5)

- **Status:** Accepted (normative for UHBS 5.0.0)
- **Author:** Moran Zavdi
- **UHBS version affected:** 5.0.0 (breaking)
- **Created:** 2026-09-18
- **Supersedes:** UHQS 4.x scoring integrity assumptions in Modules C/D and skip-credit paths
- **scoring_model_id:** `uhqs-v5.0-critical-gate-diagnostic`

## Problem

UHBS v4 produces numeric grades that overstate measurement confidence:

1. Untested or skipped checks can earn partial credit, so measuring less can raise a score.
2. Module C can award a perfect score with no telemetry (C2-only rescale) and accepts non-STIX objects / keyword “attack” as ATT&CK evidence.
3. Module D can manufacture a Safety Gate pass (`max(score, 95)` floor) and grants attestation-only credit when shell probes are unavailable.
4. Incomplete assessments still receive letter grades, so “not tested” is indistinguishable from “tested and failed.”

A grade must mean that a defined set of applicable checks ran, produced evidence, and was evaluated by a pinned scoring model (NIST SP 800-55 Vol. 1–2 measurement principles).

## Threat model (CTI / decoy)

An adversary facing a graded decoy may:

| Goal | Description | v5 coverage |
| --- | --- | --- |
| **Detect** | Fingerprint the decoy as non-production | Out of scope for composite UHQS (Modules A/B remain informative) |
| **Poison** | Inject hostile content into telemetry / SIEM | Module C sink-side injection resilience + format validation |
| **Pivot** | Escape containment / unauthorized egress | Module D critical-control verdict (mandatory) |

## Measurement model

### Check outcomes

Every catalog check receives exactly one outcome:

| Outcome | Scoring | Meaning |
| --- | --- | --- |
| `PASS` | Earns its weight | Executed; criterion met; evidence present when required |
| `FAIL` | Zero credit; stays in denominator | Executed; criterion not met |
| `NOT_APPLICABLE` | Leaves denominator | Outside declared capabilities; machine rule + written rationale required |
| `NOT_TESTED` | Zero credit; stays in denominator | Applicable but not executed |
| `ERROR` | Zero credit; stays in denominator | Tool/evidence failure — never remapped to `NOT_APPLICABLE` |

Only `NOT_APPLICABLE` may leave the scoring denominator.

### Assessment completeness

A module may receive a final score only when every applicable **mandatory** check is `PASS` or `FAIL` with required evidence. Otherwise:

- `assessment_status = INCOMPLETE`
- `uhqs = null`
- **no letter grade** (do not invent grade `U`)

Omitting, erroring, or leaving unevidenced a mandatory applicable check cannot produce a grade.

### Module D — critical controls vs defense-in-depth

Separate two concepts:

1. **Containment verdict** (`critical_control_verdict`): all applicable critical controls must `PASS` with evidence. Unauthorized egress, exposed runtime sockets, writable escape surfaces, or equivalent boundary violations → `GATE_FAILED`. Missing evidence → `INCOMPLETE` / Ungraded.
2. **Defense-in-depth score**: diagnostic 0–100 Module D score for non-critical hardening. It must not average away a critical failure.

Removed from v4:

- `max(score, 95.0)` floor
- Non-SSH attestation ladder that awarded points for `UHBS_AIRGAP_ATTESTED` alone
- Fail-open `containment_measured=False` → `δ_C = 1.0`

`UHBS_AIRGAP_ATTESTED` may describe the environment but **cannot** satisfy a technical control.

### Composite UHQS (selected model)

**Chosen model** (after synthetic sensitivity / known-good vs known-bad calibration documented below):  
**Binary critical-control eligibility gate + diagnostic module scores; no composite grade on gate failure or incomplete assessment.**

When the assessment is complete and the critical-control verdict is `GATE_PASSED`:

\[
\mathrm{UHQS} = w_A S_A + w_B S_B + w_C S_C + w_E S_E + w_F S_F
\]

with \(\delta_C = 1.0\) (gate already satisfied). Module D’s defense-in-depth score is published but not weighted into the sum (same structural role as v4: containment is a gate, not an averageable term).

When the gate fails or the assessment is incomplete: `uhqs = null`, no letter grade; module diagnostics remain.

Store the choice as immutable `scoring_model_id = uhqs-v5.0-critical-gate-diagnostic`, not merely `uhbs_version`.

### Calibration summary (synthetic)

Decision properties tested on synthetic vectors before freezing the model:

| Property | Result |
| --- | --- |
| Adding an applicable failure cannot improve UHQS | Holds (FAIL stays in denominator at zero credit) |
| Omitting a mandatory check cannot produce a grade | Holds (`INCOMPLETE`) |
| Tool `ERROR` cannot become a pass | Holds |
| Critical containment failure always fails the gate | Holds (`GATE_FAILED`, `uhqs=null`) |
| Continuous \((C/95)^k\) multiplier | Rejected — still arbitrary without live corpus; binary gate is explainable |

Known-good vector: all mandatory PASS + critical controls PASS → graded UHQS.  
Known-bad vector: egress leak on a critical control → `GATE_FAILED`, `uhqs=null`.  
Incomplete vector: mandatory `NOT_TESTED` → `INCOMPLETE`, `uhqs=null`.

Live multi-class corpus recalibration remains a follow-up; production-looking thresholds must not be claimed until representative live reruns exist. Until then, published grades under this model are **lab / reference** grades tied to `scoring_model_id`.

## Module C — telemetry assurance

Do **not** require every decoy to emit STIX. The TPS declares `native_event_format` and optional `export_formats`; validators run only for claimed formats (native JSON/JSONL, ECS, OCSF, OTLP, STIX 2.1).

Normative submodules:

- **C1** Declared-format structural conformance (schema URI, version, validator version, errors)
- **C2** Sink-side injection resilience (tagged hostile payloads; one logical event; framing intact)
- **C3** Required observables vs ground truth (presence + correctness; redaction policies allowed)
- **C4** Ground-truth completeness / timeliness (recall, duplicates, latency, clock quality)
- **C5** CTI semantics when ATT&CK mappings are claimed (pinned Enterprise/ICS bundle; mapping basis, confidence, revoked/deprecated)

Informative **Collection Capability Profile** may summarize completeness/richness; it is not “intelligence quality” and does not alter UHQS.

## Evidence and assurance

A graded result requires a schema-valid evidence pack: run identity, `scoring_model_id`, check-catalog ID/hash, harness/plugin versions, target/environment digests, per-check outcomes and evidence hashes, module completeness, and `assurance_level` ∈ {`SELF_ASSESSED`, `REPRODUCIBLE_LAB`, `INDEPENDENTLY_REPRODUCED`}. Signature/attestation reference is reserved.

## Compatibility / migration

- Breaking change: all v4 fixtures and published grades are **historical** under scoring model UHQS 4.x.
- Existing conformance **report URLs remain resolvable**; pages gain “UHBS v4.6.1 historical scoring model” metadata and links to v5 methodology.
- Parallel validators: v4 schemas retained under `schemas/v4/` for historical scorecards; v5 schemas are authoritative for new evaluations.
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

Framework mappings remain informative and machine-readable; they are not certification.

## Alternatives considered

- Exclude unmeasured checks from the denominator and disclose coverage — **rejected**; permits selective testing.
- Continuous \(\delta_C = (C/95)^k\) with \(k=2.34\) — **deferred/rejected** without live calibration; binary gate selected.
- Invent grade `U` for ungraded — **rejected**; incomplete assessments omit the grade field / set null.
- Require universal STIX emission — **rejected**; validate declared formats only.

## Security / Safety Gate notes

Lab/network probes remain CLI-only. Do not expose containment probes or live telemetry injection via MCP. Critical-control failures are fail-closed.

## Review

Independent technical review of this RFC and responses should be published before treating grade thresholds as production-facing. The project remains single-maintainer; review is not committee approval.

## References

- `docs/specification/scoring-formula.md`
- `docs/specification/modules.md`
- `src/uhbs_core/uhqs_math.py`
- `ROADMAP.md`
- `GOVERNANCE.md`
