#!/usr/bin/env python3
"""Rebuild mkdocs.yml nav for scannable, collapsible Material navigation.

- Nest Published grades and Scorecards by honeypot/product (collapsible groups).
- Keep section overview pages near the top of each section.
- Discover scorecards from docs/scorecards/*.md (no flat-list copy/paste).
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MKDOCS = ROOT / "mkdocs.yml"
text = MKDOCS.read_text()

head, _, _ = text.partition("\nnav:\n")
if not head.endswith("\n"):
    head += "\n"

reports = ROOT / "docs" / "conformance" / "reports"
scorecards_dir = ROOT / "docs" / "scorecards"

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
    "qeeqbox": "qeeqbox",
    "sentrypeer": "SentryPeer",
    "wordpot": "wordpot",
    "mockssh": "MockSSH",
    "heralding": "Heralding",
    "owasp-python-honeypot": "OWASP Python-Honeypot",
    "owa-honeypot": "owa-honeypot",
    "honeyup": "honeyup",
    "modpot": "modpot",
    "Krawl": "Krawl",
    "krawl": "Krawl",
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
    "log4pot": "Log4Pot",
    "node-ftp-honeypot": "node-ftp-honeypot",
    "ssh-auth-logger": "ssh-auth-logger",
    "trapster": "Trapster",
    "dionaea": "Dionaea",
    "hellpot": "HellPot",
    "honeywire": "HoneyWire",
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
    "illustrative": "Illustrative",
}

# Longest-prefix first for scorecard stem → product key
SCORECARD_PREFIXES = sorted(
    {
        "owasp-python-honeypot",
        "node-ftp-honeypot",
        "fortigate-vpn-ssl",
        "ssh-auth-logger",
        "ssh-honeypotd",
        "sticky_elephant",
        "express-honeypot",
        "mysql-honeypotd",
        "owa-honeypot",
        "llm-honeypot",
        "honeyagents",
        "elastichoney",
        "honeypot-ftp",
        "honeyhttpd",
        "honeytrap",
        "sentrypeer",
        "opencanary",
        "beelzebub",
        "datatrap",
        "honeymcp",
        "genaipot",
        "miniprint",
        "heralding",
        "portlurker",
        "sshesame",
        "mailoney",
        "pghoney",
        "nosqlpot",
        "trapster",
        "dionaea",
        "endlessh",
        "honeyup",
        "mockssh",
        "modpot",
        "wordpot",
        "artillery",
        "llmpot",
        "cowrie",
        "conpot",
        "espot",
        "hellpot",
        "honeywire",
        "log4pot",
        "krawl",
        "flux",
        "kippo",
        "pyrdp",
        "shiva",
        "qeeqbox",
        "illustrative",
    },
    key=len,
    reverse=True,
)

# Explicit overrides when the filename suffix is not a clean protocol token
SCORECARD_OVERRIDES: dict[str, tuple[str, str]] = {
    "espot-web-api": ("espot", "HTTP"),
    "miniprint-low-interaction": ("miniprint", "PJL"),
    "conpot-ics-scada": ("conpot", "Modbus"),
    "endlessh-ssh-tarpit": ("endlessh", "SSH tarpit"),
    "opencanary-web-api": ("opencanary", "HTTP"),
    "illustrative-posix-genai": ("illustrative", "POSIX / GenAI"),
    "honeypot-ftp": ("honeypot-ftp", "FTP"),
    "datatrap-postgres": ("datatrap", "PostgreSQL"),
    "sticky_elephant-postgres": ("sticky_elephant", "PostgreSQL"),
    "qeeqbox-postgres": ("qeeqbox", "PostgreSQL"),
    "pghoney-postgres": ("pghoney", "PostgreSQL"),
}


def label(name: str) -> str:
    return DISPLAY.get(name, name)


def protocol_label(raw: str) -> str:
    special = {
        "web-api": "HTTP",
        "ics-scada": "Modbus",
        "low-interaction": "PJL",
        "ssh-tarpit": "SSH tarpit",
        "posix-genai": "POSIX / GenAI",
        "postgres": "PostgreSQL",
        "s7comm": "S7comm",
        "generic": "Generic",
    }
    if raw in special:
        return special[raw]
    if raw.isupper() or raw in {"HTTP", "SSH", "FTP", "MCP", "SIP", "SMB", "VNC", "RDP", "NTP", "GIT", "PJL"}:
        return raw
    # mysql, redis, telnet, smtp, pop3, http, ssh, …
    return raw.upper() if len(raw) <= 6 else raw.capitalize()


def parse_scorecard(stem: str) -> tuple[str, str]:
    if stem in SCORECARD_OVERRIDES:
        return SCORECARD_OVERRIDES[stem]
    for prefix in SCORECARD_PREFIXES:
        if stem == prefix:
            return prefix, "Overview"
        if stem.startswith(prefix + "-"):
            return prefix, protocol_label(stem[len(prefix) + 1 :])
    # Fallback: split on last hyphen
    if "-" in stem:
        product, rest = stem.rsplit("-", 1)
        return product, protocol_label(rest)
    return stem, "Scorecard"


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

# Scorecards grouped by product (featured order, then alpha)
groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
for path in sorted(scorecards_dir.glob("*.md")):
    if path.name == "index.md":
        continue
    product, child = parse_scorecard(path.stem)
    groups[product].append((child, f"scorecards/{path.name}"))

sc_order: list[str] = []
sc_seen: set[str] = set()
for name in featured:
    key = name.lower() if name.lower() in {k.lower(): k for k in groups} else name
    # map featured dir names to scorecard product keys
    aliases = {
        "HellPot": "hellpot",
        "HoneyWire": "honeywire",
        "Log4Pot": "log4pot",
        "Krawl": "krawl",
        "qeeqbox-honeypots": "qeeqbox",
    }
    key = aliases.get(name, name)
    if key in groups and key not in sc_seen:
        sc_order.append(key)
        sc_seen.add(key)
for key in sorted(groups.keys(), key=lambda k: label(k).lower()):
    if key not in sc_seen:
        sc_order.append(key)
        sc_seen.add(key)

lines: list[str] = ["nav:", "  - Home: index.md"]

lines += [
    "  - Get started:",
    "      - Install & use UHBS: tooling/install-and-use.md",
    "      - CLI & Validator: tooling/cli.md",
    "      - Lab harness: reference-implementation.md",
    "      - MCP server (AI hosts): tooling/mcp.md",
    "      - MCP honeypot grading: architecture/mcp-honeypot-grading.md",
    "      - Registry: registry.md",
]

lines += [
    "  - Specification:",
    "      - Status of This Document: specification/status.md",
    "      - Core Principles: specification/core-principles.md",
    "      - Modules A–F: specification/modules.md",
    "      - Scoring Formula: specification/scoring-formula.md",
    "      - Target Profiles (TPS): specification/target-profiles.md",
]

lines += [
    "  - Published grades:",
    "      - Overview: conformance/index.md",
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
    for sub in sorted(p for p in d.iterdir() if p.is_dir() and (p / "index.md").exists()):
        kids.append((f"{sub.name.upper() if len(sub.name) <= 6 else sub.name.capitalize()} hub", f"{rel}/{sub.name}/index.md"))
    if (d / "TUTORIAL.md").exists():
        kids.append(("Reproduce grade", f"{rel}/TUTORIAL.md"))
    if (d / "METHODOLOGY.md").exists():
        kids.append(("Methodology", f"{rel}/METHODOLOGY.md"))

    lines.append(f"      - {label(name)}:")
    for title, path in kids:
        lines.append(f"          - {title}: {path}")

lines += [
    "  - Scorecards:",
    "      - Overview: scorecards/index.md",
]
for product in sc_order:
    entries = sorted(groups[product], key=lambda t: t[0].lower())
    if len(entries) == 1:
        child, path = entries[0]
        # Single-page products: keep one leaf under the product label for a consistent collapsible pattern
        lines.append(f"      - {label(product)}:")
        lines.append(f"          - {child}: {path}")
    else:
        lines.append(f"      - {label(product)}:")
        for child, path in entries:
            lines.append(f"          - {child}: {path}")

lines += [
    "  - Mappings:",
    "      - Overview: mappings/index.md",
    "      - ATT&CK: mappings/attack.md",
    "      - D3FEND: mappings/d3fend.md",
    "      - Engage: mappings/engage.md",
    "      - NIST: mappings/nist.md",
    "      - IEC 62443: mappings/iec-62443.md",
    "      - Related frameworks: mappings/related-frameworks.md",
]

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
    "  - Governance:",
    "      - Roadmap: roadmap.md",
    "      - RFCs: rfcs/README.md",
    "      - RFC-0001 Baseline: rfcs/0001-uhbs-4.0-baseline.md",
    "      - RFC Template: rfcs/0000-template.md",
    "",
]

MKDOCS.write_text(head + "\n".join(lines))
print(f"Wrote {MKDOCS} ({len(lines)} nav lines, {len(sc_order)} scorecard groups)")
