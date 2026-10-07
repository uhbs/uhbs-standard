#!/usr/bin/env python3
"""Generate results-5.0.1 hub pages (unit + product level) from run artifacts.

Completes the publish step for the 5.0.1 coverage wave: hub index.md pages were
seeded as worker placeholders, but the graded runs already exist on disk. Every
number on a generated page comes verbatim from report.json / SCORECARD.txt —
no authored scores. Units without completed runs keep their placeholders.

Page formats mirror the published reports/ tree:

* unit page: run table (quick + full), module breakdown, verbatim SCORECARD
* product page: per-protocol table linking the unit pages

Usage:
    python scripts/generate_hub_pages.py [--write]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/conformance/latest/results-5.0.1/benchmark-manifest.yaml"
BASE = "docs/conformance/latest/results-5.0.1"

MOD_ROW = re.compile(
    r"^Module ([A-F]): (.+?)\s*:\s*([\d.]+)/100\s+(\S+)\s+([A-Z_ ]+?)(?:\s\((.*)\))?$"
)
DATE_RE = re.compile(r"^Evaluation Date\s*: (\d{4}-\d{2}-\d{2})$", re.M)
GRADE_RE = re.compile(r"^GRADE ([A-F])")
TITLE_RE = re.compile(r"^# (.+)$", re.M)


def letter(report: dict) -> str:
    grade = str((report.get("uhqs") or {}).get("grade") or "")
    m = GRADE_RE.match(grade)
    return m.group(1) if m else "—"


def module_table(sc_txt: str, full: tuple[str, str, str, str]) -> str:
    rows = ["| Module | Score | Weight | Status | Notes |", "| --- | ---: | --- | --- | --- |"]
    for line in sc_txt.splitlines():
        m = MOD_ROW.match(line)
        if not m:
            continue
        _letter, name, score, weight, status, note = m.groups()
        rows.append(
            f"| Module {_letter}: {name.strip()} | {score} | {weight} | {status} | {(note or '').strip()} |"
        )
    rows.append(
        f"| Safety Gate δ_C | {full[2]} | GATE | — | Gate {full[3].split(' / ')[1]}; δ_C={full[2]} applied to composite |"
    )
    return "\n".join(rows)


def up_path(rel_from_base: str, target: str) -> str:
    """Relative link from docs/conformance/<rel>/index.md to a docs/conformance path."""
    depth = rel_from_base.count("/") + 1
    return "../" * depth + target


def build_unit_page(unit: dict) -> str | None:
    d = ROOT / unit["latest_path"]
    full_rj_p, full_sc_p = d / "full" / "report.json", d / "full" / "SCORECARD.txt"
    quick_rj_p = d / "quick" / "report.json"
    if not (full_rj_p.is_file() and full_sc_p.is_file()):
        return None
    full_r = json.loads(full_rj_p.read_text())
    full_sc = full_sc_p.read_text()
    u = full_r["uhqs"]
    fuhqs, fgrade = f"{float(u['uhqs']):g}", letter(full_r)
    fdc = f"{float(u['delta_c']):g}"
    full = (fuhqs, fgrade, fdc, f"{full_r.get('assessment_status')} / {full_r.get('critical_control_verdict')}")
    quick = None
    if quick_rj_p.is_file():
        qr = json.loads(quick_rj_p.read_text())
        qu = qr.get("uhqs") or {}
        if isinstance(qu.get("uhqs"), (int, float)):
            quick = (f"{float(qu['uhqs']):g}", letter(qr), f"{float(qu['delta_c']):g}",
                     f"{qr.get('assessment_status')} / {qr.get('critical_control_verdict')}")
    date = DATE_RE.search(full_sc)
    eval_date = date.group(1) if date else ""

    old = (d / "index.md").read_text() if (d / "index.md").is_file() else ""
    title_m = TITLE_RE.search(old)
    title = title_m.group(1).strip() if title_m else f"{unit['unit_id']}"

    rel = unit["latest_path"][len("docs/conformance/"):]  # e.g. latest/results-5.0.1/<...>
    reading = up_path(rel, "reports/READING-UHQS.md")
    exec_steps = "EXECUTION-STEPS.md" if (d / "EXECUTION-STEPS.md").is_file() else None

    lines = [
        f"# {title}",
        "",
        "**Status:** Informative · evaluation proof  ",
        f"**UHBS:** 5.0.1 · **Class:** {u.get('profile_class') or unit.get('class_name') or '—'} · "
        f"**Protocol:** `{unit['protocol_id']}`  ",
        f"**Target id:** `{unit['unit_id']}` · **Evaluated:** {eval_date}",
        "",
        "| Run | UHQS | Grade | δ_C | Verdict | Artifacts |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    if quick:
        lines.append(
            f"| [Quick](quick/SCORECARD.txt) | **{quick[0]}** | {quick[1]} | {quick[2]} | "
            f"{quick[3]} | [`report.json`](quick/report.json) |"
        )
    lines.append(
        f"| [Full](full/SCORECARD.txt) (authoritative) | **{full[0]}** | {full[1]} | {full[2]} | "
        f"{full[3]} | [`report.json`](full/report.json) |"
    )
    lines += [
        "",
        "## Full run — module breakdown",
        "",
        module_table(full_sc, full),
        "",
        "## Full scorecard (verbatim)",
        "",
        "```text",
        full_sc.rstrip("\n"),
        "```",
        "",
        "## Replication",
        "",
    ]
    if exec_steps:
        lines.append(f"- Execution steps: [{exec_steps}]({exec_steps})")
    lines += [
        f"- How to read UHQS: [CTI / blue-team guide]({reading})",
        "- Tutorial & methodology live on the [product hub](../index.md) (multi-protocol products)"
        if unit.get("layout") == "multi"
        else "- Tutorial & methodology: see the product hub for this decoy",
        "",
        "> Named product is evaluation proof only — not a UHBS endorsement.",
        "",
    ]
    return "\n".join(lines)


def build_product_page(product_rel: str, units: list[dict]) -> str | None:
    d = ROOT / BASE / product_rel
    idx = d / "index.md"
    old = idx.read_text() if idx.is_file() else ""
    title_m = TITLE_RE.search(old)
    title = title_m.group(1).strip() if title_m else product_rel
    # Placeholder titles were seeded with a trailing first-protocol suffix —
    # a product hub covers all protocols, so strip it.
    for u in units:
        suffix = f" ({u['protocol_id']})"
        if title.lower().endswith(suffix.lower()):
            title = title[: -len(suffix)]
            break
    repo = next((u.get("upstream_repo") for u in units if u.get("upstream_repo")), None)

    lines = [
        f"# {title}",
        "",
        "**Status:** Informative · evaluation proof  ",
    ]
    if repo:
        lines.append(f"**Upstream:** [{repo}]({repo})  ")
    lines += [
        "",
        "| Protocol | Class / port | Quick | Full |",
        "| --- | --- | --- | --- |",
    ]
    for u in sorted(units, key=lambda x: x["protocol_id"]):
        proto = u["protocol_id"]
        display = proto.replace("_", " ").upper()
        unit_idx = f"[{display}]({proto}/index.md)"
        cls = f"{u.get('class_name') or '—'} · :{u.get('target_port') or '?'}"
        full_rj = d / proto / "full" / "report.json"
        if full_rj.is_file():
            fr = json.loads(full_rj.read_text())
            fu = fr["uhqs"]
            fcell = f"[{float(fu['uhqs']):g} / {letter(fr)}]({proto}/index.md)"
            qrj = d / proto / "quick" / "report.json"
            if qrj.is_file():
                qr = json.loads(qrj.read_text())
                qu = qr.get("uhqs") or {}
                qcell = (
                    f"[{float(qu['uhqs']):g} / {letter(qr)}]({proto}/index.md)"
                    if isinstance(qu.get("uhqs"), (int, float))
                    else "—"
                )
            else:
                qcell = "—"
        else:
            unit_idx = display
            qcell = fcell = "pending refresh"
        lines.append(f"| {unit_idx} | {cls} | {qcell} | {fcell} |")
    lines += [
        "",
    ]
    if (d / "TUTORIAL.md").is_file() or (d / "METHODOLOGY.md").is_file():
        tut = "[Tutorial](TUTORIAL.md)" if (d / "TUTORIAL.md").is_file() else None
        meth = "[Methodology](METHODOLOGY.md)" if (d / "METHODOLOGY.md").is_file() else None
        lines.append("- " + " · ".join(x for x in (tut, meth) if x))
    lines += [
        "",
        "> Named product is evaluation proof only — not a UHBS endorsement.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--write", action="store_true", help="apply changes (default: dry-run)")
    args = p.parse_args(argv)

    manifest = yaml.safe_load(MANIFEST.read_text())
    units = [u for u in manifest["units"] if u.get("layout") == "multi"]
    singles = [u for u in manifest["units"] if u.get("layout") != "multi"]

    unit_pages: list[tuple[str, str]] = []
    for u in units + singles:
        page = build_unit_page(u)
        if page:
            unit_pages.append((f"{u['latest_path']}/index.md", page))

    products: dict[str, list[dict]] = {}
    for u in units:
        products.setdefault(u["latest_path"].rsplit("/", 1)[0], []).append(u)
    product_pages: list[tuple[str, str]] = []
    for prod, us in sorted(products.items()):
        if not any(
            (ROOT / u["latest_path"] / "full" / "report.json").is_file() for u in us
        ):
            continue
        page = build_product_page(prod[len("docs/conformance/latest/results-5.0.1/"):], us)
        if page:
            product_pages.append((f"{prod}/index.md", page))

    print(f"unit pages: {len(unit_pages)} | product pages: {len(product_pages)}")
    for fp, _ in unit_pages + product_pages:
        print("  ", fp)
    if args.write:
        for fp, content in unit_pages + product_pages:
            (ROOT / fp).write_text(content)
        print(f"wrote {len(unit_pages) + len(product_pages)} pages")
    else:
        print("dry-run only — pass --write to apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
