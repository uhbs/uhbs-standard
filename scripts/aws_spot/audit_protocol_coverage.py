#!/usr/bin/env python3
"""Audit honeypot docs/configs for documented protocols vs UHBS graded units.

Writes:
  .local/benchmark-refresh/protocol-audit/coverage.json
  docs/conformance/protocol-coverage-audit.md
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "aws_spot"))
sys.path.insert(0, str(ROOT / "src"))

from lab_recipes import RECIPES, recipe_for  # noqa: E402

from uhbs_core.protocols.registry import list_protocols  # noqa: E402

UHBS = set(list_protocols()) - {"generic"}

# Explicit alias → UHBS plugin key
ALIASES = {
    "https": "http",
    "http/s": "http",
    "http(s)": "http",
    "ssh_tarpit": "ssh",
    "ssh-tarpit": "ssh",
    "sshd": "ssh",
    "sftp": "ssh",
    "ftps": "ftp",
    "smtp/s": "smtp",
    "smtps": "smtp",
    "imap/s": "imap",
    "imaps": "imap",
    "pop3/s": "pop3",
    "pop3s": "pop3",
    "mqtts": "mqtt",
    "mqtt/s": "mqtt",
    "redis-server": "redis",
    "memcached": "memcache",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "mssql": "mssql",
    "ms-sql": "mssql",
    "sqlserver": "mssql",
    "tds": "mssql",
    "mysql": "mysql",
    "mariadb": "mysql",
    "postgresql": "postgres",
    "pgsql": "postgres",
    "postgres": "postgres",
    "telnetd": "telnet",
    "smb/cifs": "smb",
    "cifs": "smb",
    "samba": "smb",
    "microsoft-ds": "smb",
    "sip/s": "sip",
    "sips": "sip",
    "tftp": "tftp",
    "snmp": "snmp",
    "ntp": "ntp",
    "vnc": "vnc",
    "rdp": "rdp",
    "git": "git",
    "modbus": "modbus",
    "s7": "s7comm",
    "s7comm": "s7comm",
    "bacnet": "bacnet",
    "coap": "coap",
    "ldap": "ldap",
    "elasticsearch": "elasticsearch",
    "elastic": "elasticsearch",
    "pjl": "pjl",
    "jetdirect": "pjl",
    "ipp": "ipp",
    "socks": "socks5",
    "socks5": "socks5",
    "http-proxy": "httpproxy",
    "httpproxy": "httpproxy",
    "mcp": "mcp",
    "oracle": "oracle",
    "dns": "dns",
    "dhcp": "dhcp",
    "irc": "irc",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "bluetooth": "bluetooth",
    "bt": "bluetooth",
    "ssdp": "upnp",
    "upnp": "upnp",
    "pptp": "pptp",
}

# Tokens that look like protocols but are not UHBS grading targets
NOISE = {
    "tcp",
    "udp",
    "icmp",
    "ip",
    "ipv4",
    "ipv6",
    "ssl",
    "tls",
    "json",
    "xml",
    "api",
    "rest",
    "rpc",
    "unix",
    "websocket",
    "ws",
    "wss",
    "quic",
    "grpc",
}

# Known documented surfaces per product (from upstream docs / conf) — seed corrections.
# These override/extend regex extraction when README is sparse.
KNOWN_DOCUMENTED: dict[str, list[str]] = {
    # Dionaea README "Protocols" list (+ service yaml names blackhole/epmap/mirror).
    # Dionaea README "Protocols" list (blackhole/epmap/mirror are meta/sinks, not
    # separate UHBS-gradable listeners — keep as unsupported).
    "dionaea": [
        "blackhole",
        "epmap",
        "ftp",
        "http",
        "memcache",
        "mirror",
        "mqtt",
        "mssql",
        "mysql",
        "pptp",
        "sip",
        "smb",
        "tftp",
        "upnp",
    ],
    "opencanary": [
        "ftp",
        "http",
        "ssh",
        "telnet",
        "redis",
        "mysql",
        "rdp",
        "sip",
        "snmp",
        "ntp",
        "tftp",
        "vnc",
        "git",
        "smb",
    ],
    # Conpot default/ICS templates commonly documented.
    "conpot": ["modbus", "s7comm", "bacnet", "http", "ipmi", "guardian_ast", "enip"],
    "cowrie": ["ssh", "telnet"],
    # Beelzebub README example services table.
    "beelzebub": [
        "ssh",
        "http",
        "telnet",
        "rdp",
        "vnc",
        "mysql",
        "postgres",
        "mssql",
        "redis",
        "memcache",
        "smb",
        "ldap",
        "mqtt",
        "mcp",
    ],
    # Heralding shared auth honeypot suite (upstream capabilities).
    "heralding": [
        "ssh",
        "ftp",
        "telnet",
        "smtp",
        "http",
        "pop3",
        "imap",
        "mysql",
        "postgres",
        "vnc",
        "socks5",
    ],
    # qeeqbox/honeypots README feature list.
    "qeeqbox-honeypots": [
        "dhcp",
        "dns",
        "elasticsearch",
        "ftp",
        "httpproxy",
        "http",
        "imap",
        "ipp",
        "irc",
        "ldap",
        "memcache",
        "mssql",
        "mysql",
        "ntp",
        "oracle",
        "pjl",
        "pop3",
        "postgres",
        "rdp",
        "redis",
        "sip",
        "smb",
        "smtp",
        "snmp",
        "socks5",
        "ssh",
        "telnet",
        "vnc",
    ],
    # Trapster Community README protocol table.
    "trapster": [
        "ftp",
        "ssh",
        "telnet",
        "dns",
        "http",
        "snmp",
        "ldap",
        "mssql",
        "mysql",
        "rdp",
        "vnc",
    ],
    "datatrap": ["ssh", "http", "mysql", "postgres", "redis", "telnet"],
    "llmpot": ["modbus", "http", "s7comm"],
    "genaipot": ["smtp", "pop3"],
    "nosqlpot": ["redis"],
    "honeytrap": ["ssh"],  # framework; graded SSH listener in lab recipe
    "artillery": ["generic"],
    "portlurker": ["generic"],
    # Explicit single-protocol products (avoid README false positives).
    "HellPot": ["http"],
    "Log4Pot": ["http"],
    "elastichoney": ["http"],
    "espot": ["http"],
    "express-honeypot": ["http"],
    "flux": ["http"],
    "honeyhttpd": ["http"],
    "honeyup": ["http"],
    "wordpot": ["http"],
    "modpot": ["http"],
    "owa-honeypot": ["http"],
    "fortigate-vpn-ssl": ["http"],
    "HoneyWire": ["http"],
    "Krawl": ["http"],
    "miniprint": ["pjl"],
    "mailoney": ["smtp"],
    "shiva": ["smtp"],
    "sentrypeer": ["sip"],
    "pghoney": ["postgres"],
    "sticky_elephant": ["postgres"],
    "mysql-honeypotd": ["mysql"],
    "honeypot-ftp": ["ftp"],
    "node-ftp-honeypot": ["ftp"],
    "endlessh": ["ssh"],
    "ssh-auth-logger": ["ssh"],
    "ssh-honeypotd": ["ssh"],
    "sshesame": ["ssh"],
    "mockssh": ["ssh"],
    "kippo": ["ssh"],
    "honeyagents": ["ssh"],
    "llm-honeypot": ["ssh"],
    "honeytrap": ["ssh"],
    "echidra": ["ssh"],
    "honeymcp": ["mcp"],
    "owasp-python-honeypot": ["http"],
    "pyrdp": ["rdp"],
}

# Not UHBS plugins today (product-specific or missing)
UNSUPPORTED_CANON = {
    "blackhole",
    "epmap",
    "mirror",
    "ipmi",
    "guardian_ast",
    "enip",
    "couchdb",
    "cassandra",
    "rsyslog",
    "printer",
}


def canon(token: str) -> str | None:
    t = token.strip().lower().replace("_", "-")
    t = t.replace("protocol:", "").strip()
    if not t or t in NOISE:
        return None
    if t in ALIASES:
        return ALIASES[t]
    if t in UHBS:
        return t
    # hyphenated variants
    t2 = t.replace("-", "")
    for u in UHBS:
        if u.replace("-", "") == t2:
            return u
    return t  # keep unknown as raw for unsupported list


def extract_protocols_section(text: str) -> set[str]:
    """Pull tokens only from a README 'Protocols' / 'Supported Protocols' section."""
    found: set[str] = set()
    for m in re.finditer(
        r"(?is)(?:^|\n)#+\s*(?:supported\s+)?protocols?\b\s*\n(.*?)(?=\n#+\s|\Z)",
        text,
    ):
        block = m.group(1)
        for token in re.findall(
            r"(?im)^\s*(?:[-*]|\|)\s*`?([a-z][a-z0-9_+/-]{1,20})`?",
            block,
        ):
            c = canon(token.split()[0].strip("|").strip())
            if c:
                found.add(c)
        for token in re.findall(
            r"(?i)\|\s*([A-Za-z][A-Za-z0-9_+/-]{1,20})\s*(?:\(|\|)",
            block,
        ):
            c = canon(token)
            if c:
                found.add(c)
    return found


def extract_from_text(text: str) -> set[str]:
    found = extract_protocols_section(text)
    if found:
        return found
    # Fall back: inventory protocol: keys only (not full README word scan).
    for m in re.finditer(
        r"(?im)^\s*protocol:\s*[\"']?([a-z][a-z0-9_+/-]{1,20})",
        text,
    ):
        c = canon(m.group(1))
        if c:
            found.add(c)
    for m in re.finditer(
        r"(?im)^\s*protocols:\s*\[([^\]]+)\]",
        text,
    ):
        for part in m.group(1).split(","):
            c = canon(part.strip().strip("\"'"))
            if c:
                found.add(c)
    return found


def read_texts(bench: str, repo_dir: Path, inv_path: Path | None) -> str:
    chunks: list[str] = []
    candidates = []
    if inv_path and inv_path.is_file():
        candidates.append(inv_path)
        candidates.extend(inv_path.parent.glob("*.yaml"))
        candidates.extend(inv_path.parent.glob("*.yml"))
        candidates.extend(inv_path.parent.glob("*.md"))
    if repo_dir.is_dir():
        for rel in (
            "README.md",
            "README.rst",
            "README",
            "docker-compose.yml",
            "docker-compose.yaml",
            "conf",
            "config",
            "docs",
        ):
            p = repo_dir / rel
            if p.is_file():
                candidates.append(p)
            elif p.is_dir():
                candidates.extend(list(p.rglob("*.yaml"))[:40])
                candidates.extend(list(p.rglob("*.yml"))[:40])
                candidates.extend(list(p.rglob("*.md"))[:20])
    seen = set()
    for p in candidates:
        try:
            rp = p.resolve()
        except OSError:
            continue
        if rp in seen or not p.is_file():
            continue
        seen.add(rp)
        try:
            if p.stat().st_size > 2_000_000:
                continue
            chunks.append(p.read_text(encoding="utf-8", errors="replace")[:200_000])
        except OSError:
            continue
    return "\n".join(chunks)


def main() -> int:
    conn = sqlite3.connect(ROOT / ".local/benchmark-refresh/results-5.0.1.sqlite3")
    rows = conn.execute(
        "SELECT unit_id, protocol_id, inventory_path, latest_path FROM benchmark_units"
    ).fetchall()
    conn.close()

    graded: dict[str, set[str]] = defaultdict(set)
    inventories: dict[str, Path] = {}
    for uid, proto, inv, _lp in rows:
        r = recipe_for(uid)
        if not r:
            continue
        bench = r["bench"]
        if proto:
            graded[bench].add(canon(proto) or proto)
        if inv:
            inventories[bench] = ROOT / inv

    report: dict[str, dict] = {}
    missing_gradable: list[dict] = []
    unsupported_hits: dict[str, set[str]] = defaultdict(set)

    for uid, recipe in sorted(RECIPES.items()):
        bench = recipe["bench"]
        if bench in report:
            continue
        repo_dir = ROOT / ".local" / "labs" / bench
        inv = inventories.get(bench)
        # Prefer curated upstream protocol lists. Regex extraction is too noisy
        # (CI badges / words like "git", "port") for single-protocol products.
        if bench in KNOWN_DOCUMENTED:
            documented = {canon(x) or x for x in KNOWN_DOCUMENTED[bench]}
        else:
            text = read_texts(bench, repo_dir, inv)
            documented = extract_from_text(text)
            # Keep only UHBS plugins + known-unsupported tokens from extraction.
            documented = {
                p
                for p in documented
                if p in UHBS or p in UNSUPPORTED_CANON
            }
        documented.discard(None)
        documented.discard("generic")

        g = graded.get(bench, set())
        # Only keep meaningful documented tokens
        doc_uhbs = sorted(p for p in documented if p in UHBS)
        doc_unsup = sorted(
            p for p in documented if p not in UHBS and p not in {"generic", "ssh_tarpit"}
        )
        for u in doc_unsup:
            unsupported_hits[u].add(bench)

        miss = sorted(set(doc_uhbs) - g)
        for m in miss:
            missing_gradable.append(
                {
                    "bench": bench,
                    "protocol": m,
                    "unit_id": f"{bench}-{m}" if not bench.endswith(f"-{m}") else bench,
                    "repo": recipe.get("repo"),
                    "image": recipe.get("image"),
                }
            )

        report[bench] = {
            "repo": recipe.get("repo"),
            "graded_protocols": sorted(g),
            "documented_uhbs_supported": doc_uhbs,
            "documented_unsupported": doc_unsup,
            "missing_gradable": miss,
            "unit_count": len([u for u, r in RECIPES.items() if r["bench"] == bench]),
        }

    out_dir = ROOT / ".local" / "benchmark-refresh" / "protocol-audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "uhbs_plugins": sorted(UHBS),
        "benches": report,
        "missing_gradable_units": missing_gradable,
        "unsupported_protocols": {
            k: sorted(v) for k, v in sorted(unsupported_hits.items())
        },
    }
    (out_dir / "coverage.json").write_text(json.dumps(payload, indent=2) + "\n")

    md = ["# Protocol coverage audit (local Docker wave)", ""]
    md.append(
        "Generated by `scripts/aws_spot/audit_protocol_coverage.py`. "
        "Compares documented honeypot surfaces to UHBS protocol plugins and graded units."
    )
    md.append("")
    md.append(f"- UHBS plugins: `{len(UHBS)}`")
    md.append(f"- Benches audited: `{len(report)}`")
    md.append(f"- Missing gradable unit slots: `{len(missing_gradable)}`")
    md.append("")
    md.append("## Unsupported protocols (documented, no UHBS plugin)")
    md.append("")
    md.append("| Protocol | Seen on benches |")
    md.append("| --- | --- |")
    for proto, benches in sorted(unsupported_hits.items()):
        md.append(f"| `{proto}` | {', '.join(f'`{b}`' for b in sorted(benches))} |")
    md.append("")
    md.append("## Missing gradable units (documented + UHBS plugin, not graded)")
    md.append("")
    md.append("| Bench | Protocol | Suggested unit_id |")
    md.append("| --- | --- | --- |")
    for row in missing_gradable:
        md.append(f"| `{row['bench']}` | `{row['protocol']}` | `{row['unit_id']}` |")
    md.append("")
    md.append("## Per-bench summary")
    md.append("")
    for bench, info in sorted(report.items()):
        md.append(f"### {bench}")
        md.append("")
        md.append(f"- Graded: {', '.join(f'`{p}`' for p in info['graded_protocols']) or '_none_'}")
        md.append(
            "- Documented (UHBS-supported): "
            + (", ".join(f"`{p}`" for p in info["documented_uhbs_supported"]) or "_none_")
        )
        if info["documented_unsupported"]:
            md.append(
                "- Documented (unsupported): "
                + ", ".join(f"`{p}`" for p in info["documented_unsupported"])
            )
        if info["missing_gradable"]:
            md.append(
                "- **Missing to grade:** "
                + ", ".join(f"`{p}`" for p in info["missing_gradable"])
            )
        md.append("")

    md_path = ROOT / "docs" / "conformance" / "protocol-coverage-audit.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / 'coverage.json'}")
    print(f"wrote {md_path}")
    print(f"missing_gradable={len(missing_gradable)} unsupported={len(unsupported_hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
