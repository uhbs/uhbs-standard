#!/usr/bin/env python3
"""Rebuild mkdocs.yml nav: Get started + Published grades nested by honeypot."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MKDOCS = ROOT / "mkdocs.yml"
text = MKDOCS.read_text()

# Everything before "nav:" stays; we replace from nav: to EOF (file ends with nav)
head, _, _ = text.partition("\nnav:\n")
if not head.endswith("\n"):
    head += "\n"

# Build Published grades from report directories that have index.md
reports = ROOT / "docs" / "conformance" / "reports"
# Preserve a sensible human order: featured first, then alpha
featured = [
    "espot",
    "miniprint",
    "conpot",
    "cowrie",
    "endlessh",
    "opencanary",
    "beelzebub",
    "HellPot",
    "HoneyWire",
    "llm-honeypot",
    "honeyagents",
    "llmpot",
    "datatrap",
    "honeymcp",
    "genaipot",
]

skip_note_dirs = set()  # detected by TUTORIAL absence + skip language later

# Discover all report dirs with index.md
all_dirs = sorted(
    [p for p in reports.iterdir() if p.is_dir() and (p / "index.md").exists()],
    key=lambda p: p.name.lower(),
)
by_name = {p.name: p for p in all_dirs}

ordered: list[Path] = []
seen: set[str] = set()
for name in featured:
    if name in by_name:
        ordered.append(by_name[name])
        seen.add(name)
for p in all_dirs:
    if p.name not in seen and p.name not in {"READING-UHQS"}:
        ordered.append(p)

# Label helpers
DISPLAY = {
    "espot": "ESPot",
    "miniprint": "miniprint",
    "conpot": "Conpot",
    "cowrie": "Cowrie",
    "endlessh": "Endlessh",
    "opencanary": "OpenCanary",
    "beelzebub": "Beelzebub",
    "HellPot": "HellPot",
    "HoneyWire": "HoneyWire",
    "llm-honeypot": "LLM Honeypot",
    "honeyagents": "HoneyAgents",
    "llmpot": "LLMPot",
    "datatrap": "DataTrap",
    "honeymcp": "HoneyMCP",
    "genaipot": "GenAIPot",
    "elastichoney": "Elastichoney",
    "honeypot-ftp": "honeypot-ftp",
    "qeeqbox-honeypots": "qeeqbox",
    "sentrypeer": "SentryPeer",
    "wordpot": "wordpot",
    "mockssh": "MockSSH",
    "heralding": "Heralding",
    "owasp-python-honeypot": "OWASP Python-Honeypot",
    "owa-honeypot": "owa-honeypot",
    "honeyup": "honeyup",
    "modpot": "modpot",
    "Krawl": "Krawl",
    "flux": "flux",
    "fortigate-vpn-ssl": "fortigate-vpn-ssl",
    "honeytrap": "honeytrap",
    "portlurker": "portlurker",
    "sticky_elephant": "sticky_elephant",
    "kippo": "kippo",
    "nosqlpot": "nosqlpot",
    "pyrdp": "pyRDP",
    "artillery": "Artillery",
    "honeyhttpd": "HoneyHTTPD",
    "shiva": "SHIVA",
    "sshesame": "sshesame",
    "ssh-honeypotd": "ssh-honeypotd",
    "express-honeypot": "express-honeypot",
    "mailoney": "mailoney",
    "pghoney": "pghoney",
    "mysql-honeypotd": "mysql-honeypotd",
    "Log4Pot": "Log4Pot",
    "node-ftp-honeypot": "node-ftp-honeypot",
    "ssh-auth-logger": "ssh-auth-logger",
    "trapster": "Trapster",
    "dionaea": "Dionaea",
    "galah": "galah (skipped)",
    "SMTPLLMPot": "SMTPLLMPot (skipped)",
    "tanner": "tanner (skipped)",
    "glastopf": "glastopf (skipped)",
    "lophiid": "lophiid (skipped)",
    "fapro": "FaPro (skipped)",
    "glutton": "glutton (skipped)",
    "HoneyPy": "HoneyPy (skipped)",
    "masscanned": "masscanned (skipped)",
    "honeyplc": "HoneyPLC (skipped)",
    "Malbait": "Malbait (skipped)",
    "blacknet": "blacknet (skipped)",
    "telnet-iot-honeypot": "telnet-iot-honeypot (skipped)",
    "ssh-honeypot": "ssh-honeypot (skipped)",
    "acra": "Acra (skipped)",
    "ensnare": "Ensnare (skipped)",
    "snare": "snare (skipped)",
}


def label(name: str) -> str:
    return DISPLAY.get(name, name)


def indent(level: int) -> str:
    return "  " * level


lines: list[str] = ["nav:", "  - Home: index.md"]

# Get started
lines += [
    "  - Get started:",
    "      - Install & use UHBS: tooling/install-and-use.md",
    "      - CLI & Validator: tooling/cli.md",
    "      - MCP server (AI hosts): tooling/mcp.md",
    "      - MCP honeypot grading: architecture/mcp-honeypot-grading.md",
]

# Specification
lines += [
    "  - Specification:",
    "      - Status of This Document: specification/status.md",
    "      - Core Principles: specification/core-principles.md",
    "      - Modules A–F: specification/modules.md",
    "      - Scoring Formula: specification/scoring-formula.md",
    "      - Target Profiles (TPS): specification/target-profiles.md",
]

lines += [
    "  - Lab harness: reference-implementation.md",
]

# Published grades
lines += [
    "  - Published grades:",
    "      - What these pages are: conformance/index.md",
    "      - All lab reports: conformance/reports/index.md",
    "      - How to read a grade: conformance/reports/READING-UHQS.md",
    "      - Awesome honeypots triage: conformance/awesome-honeypots/TRIAGE.md",
    "      - Awesome deferred protocols: conformance/awesome-honeypots/DEFERRED-PROTOCOLS.md",
    "      - ESPot lab note (legacy path): conformance/lab-espot-web-api.md",
]

for d in ordered:
    name = d.name
    kids: list[tuple[str, str]] = []
    rel = f"conformance/reports/{name}"
    kids.append(("Report hub", f"{rel}/index.md"))
    # protocol hubs
    for sub in sorted(p for p in d.iterdir() if p.is_dir() and (p / "index.md").exists()):
        kids.append((f"{sub.name} hub", f"{rel}/{sub.name}/index.md"))
    if (d / "TUTORIAL.md").exists():
        kids.append(("Reproduce grade", f"{rel}/TUTORIAL.md"))
    if (d / "METHODOLOGY.md").exists():
        kids.append(("Methodology", f"{rel}/METHODOLOGY.md"))

    lines.append(f"      - {label(name)}:")
    for title, path in kids:
        lines.append(f"          - {title}: {path}")

# Mappings
lines += [
    "  - Mappings:",
    "      - Index: mappings/index.md",
    "      - ATT&CK: mappings/attack.md",
    "      - D3FEND: mappings/d3fend.md",
    "      - Engage: mappings/engage.md",
    "      - NIST: mappings/nist.md",
    "      - IEC 62443: mappings/iec-62443.md",
    "      - Related frameworks: mappings/related-frameworks.md",
]

# AEP
lines += [
    "  - Advanced Evidence (optional):",
    "      - Overview: advanced-evidence/index.md",
    "      - Methodology: advanced-evidence/methodology.md",
    "      - Metrics: advanced-evidence/metrics.md",
    "      - Runbook: advanced-evidence/runbook.md",
    "      - Reporting: advanced-evidence/reporting.md",
    "      - CLI Reference: advanced-evidence/cli.md",
    "      - SLM evaluator (alpha): advanced-evidence/slm-alpha.md",
    "      - Beginner tutorial: advanced-evidence/tutorial-beginner.md",
    "      - Advanced tutorial: advanced-evidence/tutorial-advanced.md",
    "      - Research foundations & credits: advanced-evidence/research-foundations.md",
    "      - Improvement notes: advanced-evidence/improvement-notes.md",
]

# Experimental
lines += [
    "  - Experimental (optional):",
    "      - Overview: experimental/index.md",
    "      - Matrix CLI: experimental/cli-matrix.md",
    "      - GenAI/MCP CLI: experimental/cli-genai-bench.md",
    "      - Provenance CLI: experimental/cli-provenance.md",
    "      - Matrix beginner tutorial: experimental/tutorial-matrix-beginner.md",
    "      - Matrix advanced tutorial: experimental/tutorial-matrix-advanced.md",
    "      - GenAI beginner tutorial: experimental/tutorial-genai-beginner.md",
    "      - GenAI advanced tutorial: experimental/tutorial-genai-advanced.md",
    "      - Provenance beginner tutorial: experimental/tutorial-provenance-beginner.md",
    "      - Architecture: architecture/experimental-benchmarks.md",
    "      - RFC 0002: rfcs/0002-experimental-benchmark-extensions.md",
]

lines += [
    "  - Registry: registry.md",
    "  - Scorecards:",
    "      - Official Examples: scorecards/index.md",
]

# Keep existing scorecard entries by extracting from old nav
old_nav = text.split("\nnav:\n", 1)[1]
# Extract scorecard lines
sc_lines = []
in_sc = False
for line in old_nav.splitlines():
    if line.startswith("  - Scorecards:"):
        in_sc = True
        continue
    if in_sc:
        if line.startswith("  - ") and not line.startswith("      "):
            break
        if line.strip().startswith("- ") and "scorecards/" in line:
            sc_lines.append(line)
lines.extend(sc_lines)

lines += [
    "  - Governance:",
    "      - RFCs: rfcs/README.md",
    "      - RFC-0001 Baseline: rfcs/0001-uhbs-4.0-baseline.md",
    "      - RFC Template: rfcs/0000-template.md",
    "  - Roadmap: roadmap.md",
    "",
]

MKDOCS.write_text(head + "\n".join(lines))
print(f"Wrote {MKDOCS} ({len(lines)} nav lines)")
