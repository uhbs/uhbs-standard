# NIST CSF & SP 800-53 Mapping (Informative)

**Status:** Informative · not a NIST assessment or certification<br>
**Sources:** [NIST CSF 2.0 / CSWP 29](https://doi.org/10.6028/NIST.CSWP.29)
(final, 2024) · [SP 800-53 Rev. 5](https://doi.org/10.6028/NIST.SP.800-53r5)
(final, 2020 with updates) ·
[SP 800-53A Rev. 5](https://doi.org/10.6028/NIST.SP.800-53Ar5) (final, 2022)<br>
**UHBS target / review:** 5.0.0 · `uhqs-v5.0-critical-gate-diagnostic` · 2026-09-18

| UHBS area | NIST CSF 2.0 function | Example SP 800-53 controls |
| --- | --- | --- |
| Dual-plane audit (static + dynamic) | Identify / Protect / Detect | CA-2, CA-8, RA-5, SI-2 |
| Module A–B deception realism | Detect / Deceive (org-specific) | SI-4, SC-7 (deception as control) |
| Module C telemetry quality | Detect / Respond | AU-2, AU-3, AU-6, SI-4 |
| Module D Safety Gate | Protect / Respond | SC-7, SC-39, CM-7, SI-3 |
| Module E resilience | Protect / Recover | SC-5, CP-2 |
| Module F white-box / secrets | Identify / Protect | RA-5, SA-11, IA-5, CM-6 |
| TPS + sandbox prerequisites | Protect | CM-2, SC-7, CM-3 |
| Assessment decision record | Govern / Protect | CA-6, PM-9 (risk acceptance remains organizational) |

These are concept-level `related` mappings with **medium confidence**: the
objectives overlap, but UHBS check procedures are not SP 800-53A assessment
objectives or methods. Organizations may use a UHBS evidence pack as one input
to a separately scoped control assessment. They must not call a UHBS grade NIST
certification, authorization, CSF Tier, or proof that a control is implemented
or effective.

Measurement design also references
[SP 800-55 Vol. 1 and Vol. 2](https://csrc.nist.gov/pubs/sp/800/55/v1/final)
(final, December 2024). Telemetry programs may consult
[SP 800-92](https://doi.org/10.6028/NIST.SP.800-92) (final, 2006);
SP 800-92 Rev. 1 remains an **Initial Public Draft** as of this review.

Governance: [Framework Crosswalk Governance](../governance/framework-crosswalks.md).
