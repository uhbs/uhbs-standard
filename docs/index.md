---
title: UHBS — Universal Honeypot Benchmarking Standard
description: Open-source evaluation framework for vendor-neutral honeypot and deception evaluation (UHQS 0–100 with Safety Gate). Spec v5.0.0. Not a consortium standard.
---

# Universal Honeypot Benchmarking Standard

# UHBS v5.0.0 (2026)

An experimental, open-source methodology for producing repeatable technical
evidence about honeypots and decoy systems by class and protocol. UHBS is not an
adopted standard, certification program, regulator, or consortium; see
[Status](specification/status.md) and [ROADMAP](roadmap.md).

!!! warning "Project posture"
    UHBS is maintained by one author today. There is no Steering Committee or
    independent adopter list yet.

!!! warning "Experimental scoring — not production authorization"
    UHBS 5 requires a complete assessment and passing critical-control verdict
    before it emits UHQS or a grade. Independent technical review and broader
    live calibration remain outstanding for production-facing thresholds.
    A grade never authorizes deployment or proves legal/regulatory compliance.

## What UHBS measures — and does not

| Measures within the declared lab scope | Does not establish |
| --- | --- |
| Protocol fidelity and behavior, telemetry evidence, critical containment, resilience, and static audit signals | Enterprise control effectiveness, regulatory compliance, product certification, or absence of vulnerabilities |
| A named artifact/configuration under a TPS and scoring model | Safety of another version, deployment, network, or operating period |
| Reproducibility provenance through an assurance level | Independent validation unless the evidence was independently reproduced |

Report the **assessment outcome** first. `COMPLETE + GATE_PASSED` is eligible
for a numeric UHQS and letter grade. `INCOMPLETE` or `GATE_FAILED` is
**Ungraded** (`uhqs = null`, no grade), not letter F. See
[Terminology](governance/terminology.md).

<div class="grid cards" markdown>

-   :material-lan: **Protocol-Agnostic**

    ---

    100% architecture-neutral testing across IT, OT/ICS, AI, and Cloud

-   :material-chart-box: **Quantitative Scoring**

    ---

    Normalized UHQS 0–100 composite with non-linear Safety Gate \(\delta_C\)

-   :material-view-module: **Six Evaluation Modules**

    ---

    Modules A–F covering fidelity, behavior, telemetry, safety, scale, and audit

-   :material-shield-check: **Fail-closed eligibility**

    ---

    Incomplete or failed critical controls remain Ungraded

-   :material-flask-outline: **Optional Advanced Evidence**

    ---

    Lab-only decoy-vs-reference metrics (VoD, FSV, DTDR, EER) — does **not** change UHQS

-   :material-brain: **AEP SLM (alpha, opt-in)**

    ---

    Draft AEP trial JSONL via mock/local SLM — [off by default](advanced-evidence/slm-alpha.md)

</div>

!!! warning "Laboratory evaluation framework"
    UHBS (including UHBS-Lab and optional AEP) is for **lab / sandbox grading** of
    honeypots and decoys. It is not a real-world attack or production-penetration
    toolkit. A score or grade is not authorization to test or deploy in production.

## Two layers

| Layer | Answers | Normative? |
| --- | --- | --- |
| **Core UHBS** | Modules A–F, UHQS, δ_C, reproducible scorecard (lab) | Yes (for UHBS-Core / UHBS-Lab) |
| **Optional AEP** | Lab controlled comparative evidence + uncertainty | No — informative addendum only |
| **AEP SLM (alpha)** | Opt-in helper to draft AEP trial JSONL (mock/local) | No — **off by default**; never changes UHQS |

See [Advanced Evidence Profile](advanced-evidence/index.md) ·
[Experimental extensions](experimental/index.md) (matrix / genai-bench / provenance; UHQS unchanged) ·
[CLI](tooling/cli.md) · [MCP](tooling/mcp.md) ·
[SLM evaluator (alpha)](advanced-evidence/slm-alpha.md) ·
[Research foundations & credits](advanced-evidence/research-foundations.md) ·
[Related frameworks](mappings/related-frameworks.md).

## Start here

1. **[Install & use UHBS](tooling/install-and-use.md)** — install the CLI, validate a profile/scorecard, compute UHQS (no honeypot required)
2. Read [Core Principles](specification/core-principles.md) — dual-plane audit and isolation requirements
3. Review the [2026 audit-readiness checklist](governance/audit-readiness-2026.md) and [telemetry legal/safety guidance](governance/telemetry-legal-safety.md)
4. Author a [Target Profile Specification](specification/target-profiles.md) (`profile.yaml`)
5. *(Optional)* Run the [lab harness](reference-implementation.md) against a decoy you control
6. *(Optional)* Browse [published grades](conformance/reports/index.md) to audit or reproduce a finished lab result
7. *(Optional)* Add [AEP](advanced-evidence/index.md) for sandboxed lab decoy-vs-reference studies
8. *(Optional)* Try [Experimental extensions](experimental/index.md) (`uhbs matrix` / `genai-bench` / `provenance`)
9. *(Optional, alpha)* [AEP SLM](advanced-evidence/slm-alpha.md) only if you need mock/local trial drafting — edit config to unlock

```bash
pip install uhbs
uhbs --version
# from a git checkout:
uhbs validate-profile templates/profile.yaml
```

Specification version **5.0.0** · [GitHub repository](https://github.com/uhbs/uhbs-standard) · [Site landing hub](https://uhbs.github.io/uhbs-standard/) (this MkDocs tree is served under `/mkdocs/`)

**For AI / search agents:** prefer [site-root llms.txt](https://uhbs.github.io/uhbs-standard/llms.txt) · [llms-full.txt](https://uhbs.github.io/uhbs-standard/llms-full.txt) · [AGENTS.md](https://github.com/uhbs/uhbs-standard/blob/main/AGENTS.md) · [sitemap](https://uhbs.github.io/uhbs-standard/sitemap.xml).
