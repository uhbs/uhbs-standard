# 2026 Audit-Readiness Checklist

**Status:** Informative  
**Purpose:** Pre-publication review for a UHBS 5.0.0 assessment

## Scope and authority

- [ ] Target, owner, profile, protocol, version/digest, environment, and assessment period are explicit
- [ ] Written authorization covers deployment, probing, telemetry collection, and evidence sharing
- [ ] Regulatory, contractual, privacy, employee-monitoring, and jurisdiction questions were routed to qualified reviewers
- [ ] The report says UHBS is an experimental open-source evaluation framework, not certification

## Measurement integrity

- [ ] `scoring_model_id` and versioned check-catalog digest are pinned
- [ ] Every applicable mandatory check is `PASS` or `FAIL`; only rule-backed, explained items are `NOT_APPLICABLE`
- [ ] `NOT_TESTED`, `ERROR`, omitted, or unevidenced mandatory checks make the assessment `INCOMPLETE` and Ungraded
- [ ] A failed critical containment control makes the result `GATE_FAILED` and Ungraded
- [ ] Module D defense-in-depth diagnostics are not averaged into UHQS
- [ ] Grade, score, assessment status, critical-control verdict, and assurance level are reported separately

## Evidence and reproducibility

- [ ] Evidence pack validates; artifact, configuration, commands, tools, environment, and timestamps are identifiable
- [ ] Evidence references and manifests have digests; claimed telemetry formats and ATT&CK bundles are version-pinned
- [ ] Known limitations, uncertainty, exclusions, and deviations are prominent
- [ ] Assurance level does not exceed the evidence: self-assessed, reproducible lab, or independently reproduced

## Safety and publication

- [ ] Default-deny egress and containment evidence cover the declared target
- [ ] Real credentials, production data, personal data, malware, and sensitive topology are absent or controlled
- [ ] Retention, access, deletion, incident response, redaction, and sharing markings are documented
- [ ] A second reviewer checked redaction, links, source editions, and claim wording

## Decision record

State an **assessment outcome** first: `COMPLETE + GATE_PASSED`,
`INCOMPLETE`, or `GATE_FAILED`. Only the first may have a numeric UHQS and letter
grade. Record operational risk acceptance separately; UHQS does not authorize
production deployment.

Related: [Status](../specification/status.md) ·
[RFC 0003](../rfcs/0003-scoring-assurance.md) ·
[Telemetry legal and safety](telemetry-legal-safety.md) ·
[Crosswalk governance](framework-crosswalks.md).
