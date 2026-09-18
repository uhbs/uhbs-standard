# ATT&CK Technique Mapping (Informative)

**Status:** Informative · analyst hypothesis, not ATT&CK coverage<br>
**Source:** [MITRE ATT&CK v19.2](https://attack.mitre.org/resources/versions/)
(current at 2026-09-18; Enterprise/Mobile/ICS, August 2026 agile data update)<br>
**UHBS target:** 5.0.0 · `uhqs-v5.0.0-critical-gate-binary`

Maps UHBS evaluation activities to ATT&CK techniques that an analyst may observe
or emulate in an authorized lab. A shared identifier does not mean the decoy
detects, prevents, or completely covers that technique. Validate every claimed ID
against the pinned Enterprise or ICS STIX bundle and record the mapping basis,
confidence, and revoked/deprecated state as required by Module C5.

| UHBS module / step | ATT&CK technique(s) | Notes |
| --- | --- | --- |
| A1 Protocol FSM | T1040, T1595 | Network sniffing / scanning against protocol state |
| A2 Negotiation / fingerprint | T1082, T1016 | System / network discovery via banners & fingerprints |
| A3 Timing side-channel | T1595 | Active scanning with statistical timing |
| B1 Cross-session state | T1059, T1105 | Command execution / ingress tool transfer analogs |
| B2 Payload handling | T1203, T1059 | Exploitation / interpreter abuse against decoy handlers |
| B3 Input fuzzing | T1499 | Endpoint DoS / resource exhaustion via malformed input |
| C1–C4 telemetry validation | — | Format, injection resilience, observables, completeness, and timeliness are measurement checks, not ATT&CK techniques |
| C5 claimed ATT&CK semantics | Claimed IDs only | Resolve against the pinned bundle; do not infer IDs from keywords |
| D1 OOB egress | T1041, T1572, T1090 | Exfiltration / tunneling / proxy from compromised shell |
| D2 Container escape / LPE | T1611, T1068 | Escape to host / privilege escalation |
| D3 Prompt injection (GenAI) | T1059 (adjacent) | LLM boundary bypass — map per org GenAI threat model |
| E1 Connection saturation | T1498, T1499 | Network / endpoint DoS under load |
| E2 Resource exhaustion | T1499 | Resource hijacking / crash loops |
| F1 SAST / vulns | T1190, T1195 | Exploit public-facing app / supply chain |
| F2 Secrets in source | T1552 | Unsecured credentials |
| F3 Coverage gaps | T1083 | File/command discovery of unhandled stubs |

## Using this mapping

1. When publishing a UHBS scorecard, **MAY** attach ATT&CK IDs for failed checks
   via the optional `framework_refs.attack` array (e.g. `["T1595", "T1041"]`) —
   display-only, ignored by UHQS math. See the [Mapping Index](index.md).
2. Module C validates ATT&CK IDs only when the target claims ATT&CK mapping; STIX
   output is optional and governed by the TPS-declared format.
3. Mapping confidence is **low by default** until a human reviewer documents
   observable-to-technique rationale. Mappings never affect UHQS.
4. Review on every ATT&CK dataset update under
   [Framework Crosswalk Governance](../governance/framework-crosswalks.md).
