# 2026 Framework and Regulatory Context

**Status:** Informative · not legal advice<br>
**UHBS scope:** Technical lab evidence about a decoy; not organizational compliance<br>
**Source review date:** 2026-09-18

!!! warning "No certification or safe-harbor claim"
    A UHBS result does not certify a product, organization, control environment, or
    legal obligation. Even a complete, independently reproduced A-grade assessment
    covers only the declared target, profile, checks, evidence, and scoring model.
    Determine applicability and sufficiency with qualified security, privacy, and
    legal reviewers in each jurisdiction.

## Pinned source register

| Source and status | Why a reviewer may consult it | UHBS boundary |
| --- | --- | --- |
| [NIST CSF 2.0, CSWP 29](https://doi.org/10.6028/NIST.CSWP.29), final, 2024 | Cyber-risk outcomes and governance vocabulary | UHBS evidence may inform selected outcomes; it is not a CSF Profile or Tier determination |
| [NIST SP 800-53 Rev. 5](https://doi.org/10.6028/NIST.SP.800-53r5), final with current errata; [SP 800-53A Rev. 5](https://doi.org/10.6028/NIST.SP.800-53Ar5), final, 2022 | Control and assessment-method vocabulary | A UHBS check is not a 53A control assessment unless separately tailored and performed |
| [NIST SP 800-55 Vol. 1](https://doi.org/10.6028/NIST.SP.800-55v1) and [Vol. 2](https://doi.org/10.6028/NIST.SP.800-55v2), final, 2024 | Measure selection, validation, and measurement-program governance | Informs measurement discipline; does not validate UHQS for every operating context |
| [NIST SP 800-61 Rev. 3](https://doi.org/10.6028/NIST.SP.800-61r3), final, April 2025 | Incident-response outcomes aligned to CSF 2.0 | Decoy telemetry may support detection/response; UHBS does not assess the incident-response program |
| [NIST SP 800-92](https://doi.org/10.6028/NIST.SP.800-92), final, 2006 | Final NIST log-management guidance | [Rev. 1](https://csrc.nist.gov/pubs/sp/800/92/r1/ipd) is an **Initial Public Draft** (2023), not final as of this review |
| [OASIS STIX 2.1](https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html) and [TAXII 2.1](https://docs.oasis-open.org/cti/taxii/v2.1/os/taxii-v2.1-os.html), OASIS Standards, 10 June 2021 | Optional CTI structure and exchange | UHBS validates a claimed format only; STIX/TAXII output is not universally required |
| [MITRE ATT&CK v19.2](https://attack.mitre.org/resources/versions/), current at review (Enterprise/Mobile/ICS; August 2026 agile update) | Resolve claimed technique IDs and deprecated/revoked state | ATT&CK tags describe observations or mapping intent, not coverage or prevention |
| [MITRE D3FEND](https://d3fend.mitre.org/) and [Engage](https://engage.mitre.org/) | Defensive-technique and adversary-engagement vocabulary | Conceptual mappings only; record retrieval/review date because these knowledge bases evolve |
| [IEC 62443-2-1:2024](https://webstore.iec.ch/en/publication/62883), [3-2:2020](https://webstore.iec.ch/en/publication/30727), [3-3:2013](https://webstore.iec.ch/en/publication/7033), [4-1:2018](https://webstore.iec.ch/en/publication/33615), [4-2:2019](https://webstore.iec.ch/en/publication/34421) | IACS security programs, risk, system, lifecycle, and component requirements | An ICS-SCADA score is not an IEC 62443 security-level or conformity assessment |
| [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) and ISO/IEC 27002:2022 | ISMS requirements and information-security controls | UHBS neither audits an ISMS nor grants ISO certification |
| [NIS2, Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj), transposition deadline 17 October 2024 | Risk management, incident handling/reporting, supply-chain and governance duties for in-scope entities | National implementing law, sector, entity size, and supervisory guidance control applicability |
| [DORA, Regulation (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj), applicable since 17 January 2025 | ICT risk, resilience testing, incidents, and third-party risk in the financial sector | A honeypot grade does not establish DORA conformity or authorize threat-led penetration testing |
| [EU Cyber Resilience Act, Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj) | Product cybersecurity and vulnerability handling | Article 14 reporting applies **11 September 2026**; main obligations apply **11 December 2027**. Product/operator scope still requires legal analysis |
| [EU GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj) | Lawfulness, purpose limitation, minimization, retention, security, and data-subject rights | Honeypot IP addresses, identifiers, payloads, and credentials may be personal data; a UHBS result does not establish a lawful basis |

## Appropriate evidence statement

Use narrowly scoped language:

> “This UHBS 5.0.0 evidence pack may support review of [named outcome/control]
> for [system and period]. The relationship is informative and does not establish
> compliance, certification, control effectiveness outside the tested scope, or
> legal authorization.”

Mappings are governed by the
[Framework Crosswalk Governance](../governance/framework-crosswalks.md) process.
