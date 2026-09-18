# Framework Crosswalk Governance

**Status:** Informative<br>
**Applies to:** UHBS 5.0.0 documentation and scorecard `framework_refs`<br>
**Last reviewed:** 2026-09-18

UHBS crosswalks help readers translate evaluation evidence into familiar control,
risk, and threat-taxonomy language. They are **not** compliance mappings,
certifications, legal opinions, or evidence that an organization satisfies an
external requirement.

## Required mapping record

Every maintained crosswalk should identify:

| Field | Minimum record |
| --- | --- |
| Source | Publisher, title, edition/release, publication status, canonical URL |
| Target | UHBS version, `scoring_model_id`, module/check ID, and profile scope |
| Granularity | Outcome, control, requirement, technique, or concept — never mix silently |
| Relationship | `equivalent`, `supports`, `related`, or `no mapping`; default to `related` |
| Rationale | Short explanation of the shared objective and material differences |
| Confidence | High / medium / low, with reviewer basis |
| Review | Reviewer identity or role, review date, and next review trigger |

`equivalent` should be exceptional and requires a requirement-by-requirement
analysis. A similar topic or keyword is only `related`.

## Review and drift process

1. Pin the external edition or dataset release; do not map to an undated “latest.”
2. Review at least annually and when UHBS scoring, the source edition, or a cited
   control/technique changes.
3. Check renamed, withdrawn, deprecated, and revoked identifiers.
4. Record the change in version control and update the page review date.
5. If the source cannot be verified, mark the row `stale` or remove it from the
   active crosswalk. Do not silently carry it forward.

Machine-readable `framework_refs` are display metadata. They never alter UHQS,
assessment completeness, the critical-control verdict, or assurance level.

## Review checklist

- [ ] Canonical primary source and exact status are recorded
- [ ] Mapping is scoped to a UHBS version and named scoring model
- [ ] Rationale distinguishes evidence support from requirement satisfaction
- [ ] Confidence and review date are visible
- [ ] Licensing permits the quoted or redistributed material
- [ ] No certification, endorsement, adoption, or regulatory-compliance claim is implied

See the [Mapping index](../mappings/index.md) and
[2026 regulatory context](../mappings/regulatory-context.md).
