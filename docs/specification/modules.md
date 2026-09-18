# Evaluation Modules (A–F)

UHBS v5.0.0 defines six evaluation modules under scoring model
`uhqs-v5.0-critical-gate-diagnostic` ([RFC 0003](../rfcs/0003-scoring-assurance.md)).
Module **D** is a **critical-control gate** plus a separate defense-in-depth diagnostic
score. Incomplete mandatory measurement yields an **Ungraded** result (`uhqs=null`),
not a manufactured letter grade.

Check outcomes: `PASS` | `FAIL` | `NOT_APPLICABLE` | `NOT_TESTED` | `ERROR`.
Only `NOT_APPLICABLE` leaves the denominator (machine rule + written rationale required).

---

## Module A: Protocol & Syntax Fidelity

**Objective:** Verify that the honeypot accurately implements the targeted protocol and does not reveal its emulated nature through network artifacts or timing side-channels.

| Step | Name | Procedure |
| --- | --- | --- |
| **A1** | Protocol FSM Inspection | Issue valid, out-of-order, and invalid protocol verbs sequentially; verify exact protocol-mandated status codes. |
| **A2** | Header & Negotiation Parity | Query capability negotiation strings, cipher suites, and server headers; compare against standard OS/device fingerprint baselines for the target protocol. |
| **A3** | Statistical Side-Channel Analysis | Measure response timing jitter across 1,000 simple queries; require inter-arrival-time distribution to match the gold baseline using a two-sample goodness-of-fit test. |

---

## Module B: Behavioral & Stateful Realism

**Objective:** Confirm that the honeypot maintains consistent session state, persists dynamic modifications, and handles non-standard attacker inputs.

| Step | Name | Procedure |
| --- | --- | --- |
| **B1** | Cross-Session State Persistence | Modify session state (file create, coil change, DB insert) and re-query; assert 100% of dynamic state changes persist. |
| **B2** | Payload Handling & Execution | Send class-tailored workloads; process realistically or fail gracefully without stack traces or dropped connections. |
| **B3** | Non-UTF8 & Input Stress Fuzzing | Flood with raw binary, null bytes, and improper encodings; confirm zero unhandled exceptions or unexpected resets. |

---

## Module C: Telemetry Assurance & Pipeline Resilience

**Objective:** Ensure the decoy produces structured, sink-verified telemetry that matches harness ground truth and resists poisoning. Detection resistance is out of scope for composite UHQS (threat model: poison / pivot are in scope for C/D).

Do **not** require universal STIX emission. The TPS declares `native_event_format` and optional `export_formats`; validators run only for claimed formats.

| Step | Name | Procedure |
| --- | --- | --- |
| **C1** | Declared-format structural conformance | Validate claimed formats only (native JSON/JSONL against a target schema; ECS/OCSF against pinned schema/version; OTLP JSON against declared version; STIX 2.1 with a standards-aware validator when STIX export is claimed). Record schema URI, version, validator version, and errors. Format conformance alone does not imply semantic quality. |
| **C2** | Sink-side injection resilience | Inject tagged ANSI, delimiter, control-character, Unicode, multiline, nested-object, oversized, and formula-injection payloads. Read the corresponding event from the **configured sink** and verify: one logical event; hostile content preserved as data without changing record structure; declared framing still parses; no forged fields or second events; downstream test parser remains available. Score the sink, not whether a shell accepted a command. |
| **C3** | Required observables vs ground truth | Measure per-profile required observables (presence + correctness) against harness ground truth: event/observer time with timezone, endpoints, protocol action, auth result, lawful credential/command content, session ID, file digest linked to retained artifact, outbound destination, and related integrity checks (event-ID stability, ordering, truncation disclosure). Redaction/marking policies are allowed; do not reward unnecessary sensitive-data retention. |
| **C4** | Ground-truth completeness & timeliness | Emit uniquely tagged interactions with an immutable truth manifest. Match events in an observation window and report recall, required-field accuracy, duplicate rate, delivery latency, late/missing events, and clock offset/uncertainty. Do not label unmatched background events as false positives unless the environment guarantees isolation. |
| **C5** | ATT&CK / CTI semantics | When ATT&CK mappings are claimed, resolve IDs against a repository-pinned Enterprise/ICS ATT&CK STIX bundle. Record bundle version, mapping basis (`observed` / `inferred` / `analyst_asserted`), confidence, source event references, and revoked/deprecated status. Interoperability tests loss-aware transformation into a declared export — not universal STIX round-trip. OASIS STIX/TAXII 2.1 apply only where CTI exchange is claimed. |

!!! tip "Collection Capability Profile (informative)"
    An informative **Collection Capability Profile** may summarize event completeness, field richness, artifact retention, and engagement depth. It is **not** “intelligence quality” and **MUST NOT** alter UHQS.

!!! tip "Force multiplier"
    Telemetry integrity multiplies the value of the entire security stack. Corrupted or injectable logs can blind SIEM/SOAR pipelines — Module C is a critical quality dimension independent of deception realism.

---

## Module D: Safety, Containment & Boundary Controls

**Objective:** Guarantee that the honeypot cannot be exploited to breach underlying infrastructure, escalate privileges, or conduct outbound attacks.

Module D has two **separate** outputs:

1. **Critical-control verdict** (`GATE_PASSED` | `GATE_FAILED` | `INCOMPLETE`) — eligibility for a composite UHQS.
2. **Defense-in-depth score** (0–100) — diagnostic hardening only; **MUST NOT** clear or weaken the verdict.

| Step | Name | Procedure |
| --- | --- | --- |
| **D1** | Out-of-Band (OOB) Egress Sweeps | Attempt ICMP, DNS tunneling, HTTP/S, and raw TCP/UDP egress; confirm **0%** unauthorized traffic exits the sandbox. Failures of applicable critical egress controls → `GATE_FAILED`. |
| **D2** | Container Escape & LPE | Execute standard container breakout checks (runtime control sockets, cgroups abuse, sensitive `/proc` or `/sys` mounts); confirm zero access to underlying host hardware or runtime namespaces. Exposed sockets / writable escape surfaces → `GATE_FAILED`. |
| **D3** | GenAI Boundary & Prompt Injection *(if applicable)* | Multi-turn indirect prompt injections and context exhaustion; verify zero system-prompt leaks or guardrail breaches. Mark `NOT_APPLICABLE` only with catalog rule + rationale when GenAI is not in scope. |
| **D-DiD** | Defense-in-depth controls | Additional hardening checks contribute only to the diagnostic Module D score. They **MUST NOT** average away a critical failure. |

Removed from v4: `max(score, 95)` floor; attestation-only credit for `UHBS_AIRGAP_ATTESTED`; fail-open unmeasured containment → pass. Environment attestation may describe the lab but **cannot** satisfy a technical control.

!!! danger "Critical-control gate"
    Under `uhqs-v5.0-critical-gate-diagnostic`, a failed or incomplete critical-control verdict yields **Ungraded** (`uhqs=null`). There is no continuous \(\delta_C = (C/100)^2\) penalty and no letter grade for incomplete containment measurement.

---

## Module E: Scalability, Latency & Stress Performance

**Objective:** Evaluate performance under sustained, automated attack conditions.

| Step | Name | Procedure |
| --- | --- | --- |
| **E1** | Connection Saturation Stress | Ramp workers to peak capacity; measure P50/P95/P99; ensure P95 remains below the TPS threshold (standard **&lt; 150 ms**). |
| **E2** | Resource Exhaustion & Circuit Breaking | Flood memory-intensive operations; verify clean circuit-breaker engagement with **zero crashes** or thread-blocking loops. |

| Metric | Requirement |
| --- | --- |
| P95 latency | &lt; 150 ms under peak concurrent load (unless TPS overrides) |
| P50 / P99 | Recorded for full latency distribution |
| Crashes | **0** allowed under resource exhaustion |

---

## Module F: White-Box Static Code Audit

**Objective:** Analyze honeypot source and deployment artifacts for vulnerabilities discoverable prior to deployment.

| Step | Name | Procedure |
| --- | --- | --- |
| **F1** | Static Security & SAST | Execute industry-standard SAST and container image scanners across the repository and deployment artifacts; target zero High or Critical vulnerabilities, RCE flaws, or insecure system command wrappers. |
| **F2** | Hardcoded Key & Secret Detection | Scan for embedded keys, static seeds, default SSH host keys, static MACs; target zero deterministic secrets. |
| **F3** | Coverage & Unsupported Command Review | Compare handlers vs. target standards; measure fully handled requests vs. unhandled fallback stubs. |
