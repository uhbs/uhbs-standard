# How to read UHBS lab proof (CTI & blue team)

**Audience:** cyber threat intelligence analysts, detection engineers, and blue-team operators reviewing published UHBS evaluation proof.  
**Current specification:** UHBS 5.0.1 · **Nature of these pages:** informative lab evidence — **not** product endorsements, certifications, regulatory assessments, or “best honeypot” rankings.

!!! note "Check the scoring model"
    Published report paths include historical v4 artifacts. Preserve and cite the
    `uhbs_version` and `scoring_model_id` shown by the artifact; do not recalculate
    or compare a v4 grade as though it used v5 completeness and assurance rules.

## What a published grade is

An always-grade lab run produces a **UHQS** score (0–100) and letter grade under
a named **class**, protocol, and scoring model (`uhqs-v5.2-measured-renorm`). Inspect
`assessment_status`, `critical_control_verdict`, and `assurance_level` alongside
the grade. Unmeasured modules are **excluded** from the composite (weights
renormalized). Only `GATE_FAILED` applies δ_C=0.5; incompleteness is a status
label, not a haircut.

| Module | Question it answers | Blue-team / CTI use |
| --- | --- | --- |
| **A — Protocol fidelity** | Does the decoy speak the protocol well enough to look like a real service? | Whether scanners and commodity malware will stay engaged long enough to leave telemetry |
| **B — Behavioral realism** | Do post-connect behaviors (auth, sessions, payloads) feel plausible? | Whether interactive attackers / bots continue; weak B often means “credential logger only” |
| **C — Telemetry quality** | Can the harness observe useful session evidence from the lab setup? | When measured: analyst-usable logs for *this* lab. When unmeasured: excluded from UHQS (does not force F) |
| **D — Safety & containment** | Do critical containment controls pass with evidence? | Factor via δ_C only on `GATE_FAILED` (0.5); verdict stays on the card |
| **E — Scalability & latency** | Timing vs TPS P95 expectations | Whether the decoy remains responsive under probe load |
| **F — Static code audit** | Source-level signals from the checkout used in the lab | Hygiene / supply-chain posture of **that** tree — not a full CVE audit |

**Prefer `full/`** over `quick/` when making operational judgments. Quick runs are smoke-oriented (fewer timing samples, often SAST skipped).

## Trust checklist (before you cite a grade)

1. Open the **product hub** → protocol page → confirm **full** UHQS and module table.
2. Open `SCORECARD.txt`, `report.json`, and the evidence manifest under `full/` — machine-readable artifacts outrank a summary page.
3. Confirm status/verdict, scoring model, target digest, evidence coverage, and assurance level.
4. Read **Methodology** for lab image, ports, containment evidence, and limitations.
5. Read **Tutorial** if you need to re-run the same UHBS-Lab path.
6. Treat product names as **proof labels only** (vendor-neutral UHBS vocabulary is class + protocol).

## How CTI analysts should use these pages

- Map **protocol + interaction depth** to collection strategy (Internet noise vs targeted intrusion).
- Use module notes (auth failed, tarpit, banner quirks) to anticipate **what ATT&CK-ish activity** you will and will not see.
- Do **not** treat UHQS as “threat level” or malware sophistication — it grades the **decoy**, not the attacker.

## How blue teams should use these pages

- Decide whether a decoy is suitable as a **sensor** (telemetry) vs a **delay/tarpit** vs a **credential sink**.
- Check the **critical-control verdict and Module D evidence** before any deployment decision.
- Expect to **wire your own** logging/SIEM; Module C reflects the graded lab harness, not your enterprise pipeline.
- Replicate with the tutorial before trusting numbers in change-control or architecture reviews.

## Grade and outcome

Letter bands are **A ≥ 90**, **B ≥ 80**, **C ≥ 70**, **D ≥ 50**, else **F**.
`GATE_FAILED` and `INCOMPLETE` still publish a letter grade with a lower δ_C
(0.5 / 0.75). F is a low composite, not “refused to grade.” No outcome is
production authorization or proof of compliance.
