# Honeypot Telemetry: Operational, Privacy, and Legal Safety

**Status:** Informative · general operational guidance · not legal advice<br>
**Review date:** 2026-09-18

Honeypots intentionally receive hostile and unexpected traffic. Their telemetry
can contain IP addresses, account identifiers, personal data, secrets, malware,
illegal content, privileged communications, or third-party data. Technical
containment does not create legal authority to collect, retain, inspect, or share it.

## Before collection

- Record the system owner, purpose, authorized networks, approver, operating
  jurisdiction, and prohibited activity. Obtain written authorization for the
  decoy, monitoring, active probes, and any interaction with third-party systems.
- Complete privacy, labor/employee-monitoring, communications-interception,
  sector, and cross-border review as applicable. Define controller/processor and
  service-provider roles where relevant.
- Use synthetic identities and bait. Never plant real customer data, production
  credentials, private keys, tokens, or credentials that work outside the decoy.
- Default-deny egress and administrative access. Separate collection, analysis,
  and production networks; document an emergency shutdown path.

## Data handling controls

| Area | Minimum practice |
| --- | --- |
| Purpose and minimization | Collect fields needed for a documented security purpose; disable unnecessary payload/body capture |
| Credentials and secrets | Treat as high-risk; prevent replay, mask in routine views, and rotate any credential that might be real |
| Retention | Define event-class retention and deletion/review dates; do not keep raw data indefinitely “just in case” |
| Access | Least privilege, MFA, separate analyst/admin roles, access logging, and periodic entitlement review |
| Integrity | Time synchronization, immutable or append-only evidence where justified, provenance, and cryptographic digests |
| Security | Encrypt in transit and at rest; isolate malware; scan exports; test restoration and deletion procedures |
| Sharing | Apply TLP or an equivalent marking, redact/pseudonymize, verify recipient authority, and control onward sharing |
| Rights and incidents | Maintain escalation paths for data-subject requests, accidental collection, breach assessment, and legal hold |

Pseudonymization reduces exposure but does not necessarily make data anonymous.
Publicly routable source addresses and attacker-supplied identifiers should not be
presumed non-personal. Preserve raw payloads only when the need and safeguards
justify the risk.

## Publication rule

Published scorecards and evidence packs should contain only sanitized,
non-sensitive evidence. Before release:

- remove credentials, tokens, payload bodies, personal identifiers, internal
  topology, and exploitable configuration;
- replace raw events with bounded excerpts or aggregates when they prove the
  criterion;
- verify licenses, malware-handling restrictions, contractual terms, and
  information-sharing markings; and
- have a second reviewer confirm redaction and intended audience.

UHBS assurance levels describe reproducibility of evidence. They do not describe
privacy compliance, legal admissibility, intelligence reliability, or permission
to deploy. See [2026 framework and regulatory context](../mappings/regulatory-context.md).
