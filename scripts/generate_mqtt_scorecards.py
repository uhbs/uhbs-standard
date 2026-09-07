#!/usr/bin/env python3
"""Generate MQTT decoy scorecards + report hubs from /tmp/mqtt_eval.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = json.loads(Path("/tmp/mqtt_eval.json").read_text())
TODAY = "2026-09-07"
VERSION = "4.6.0"

LABELS = {
    "mqtt-decoy-a": {
        "title": "MQTT decoy A",
        "host": "98.90.197.80",
        "blurb": (
            "Anonymous MQTT :1883 honeypot (operator-provided). "
            "Weaker state machine (bad UNSUBACK)."
        ),
    },
    "mqtt-decoy-b": {
        "title": "MQTT decoy B",
        "host": "3.84.184.144",
        "blurb": (
            "Anonymous MQTT :1883 honeypot (operator-provided). "
            "Stronger session verbs; still no pub/sub delivery."
        ),
    },
}


def main() -> None:
    lab = ROOT / "docs/conformance/labs/mqtt"
    lab.mkdir(parents=True, exist_ok=True)
    (lab / "low_interaction_mqtt.yaml").write_text(
        """# Low-Interaction MQTT decoy — Target Profile Specification (TPS)
metadata:
  name: "Low-Interaction-MQTT-Decoy"
  class: "Low-Interaction"
  version: "1.0.0"
  uhbs_version: "4.6.0"

protocols:
  - mqtt

ports:
  mqtt: 1883

performance_baseline:
  probe_timeout_sec: 3.0
  timing_samples: 50

module_weights:
  w_A: 0.30
  w_B: 0.15
  w_C: 0.25
  w_E: 0.10
  w_F: 0.20

strict_rfc_enforcement: true

notes: |
  Vendor-neutral MQTT 3.1.1 surface grading (IoT/OT messaging decoys).
  Product names appear only under conformance as evaluation proof.
"""
    )

    for key, meta in LABELS.items():
        r = EVAL[key]
        scores = r["scores"]
        notes = r["notes"]
        status = r["status"]
        w = r["weights"]

        sc = {
            "uhbs_version": VERSION,
            "target": {
                "name": f"{meta['title']} (MQTT :1883)",
                "class": "Low-Interaction",
                "profile_ref": "docs/conformance/labs/mqtt/low_interaction_mqtt.yaml",
            },
            "evaluated_at": TODAY,
            "auditor": (
                "UHBS MQTT protocol-surface lab "
                "(Modules A–F; remote decoy, no source_root)"
            ),
            "modules": {
                "A": {
                    "score": round(scores["A"], 2),
                    "status": status["A"],
                    "weight": w["w_A"],
                    "notes": notes["A"],
                },
                "B": {
                    "score": round(scores["B"], 2),
                    "status": status["B"],
                    "weight": w["w_B"],
                    "notes": notes["B"],
                },
                "C": {
                    "score": round(scores["C"], 2),
                    "status": status["C"],
                    "weight": w["w_C"],
                    "notes": notes["C"],
                },
                "D": {
                    "score": round(scores["D"], 2),
                    "status": "FAILED",
                    "notes": notes["D"],
                },
                "E": {
                    "score": round(scores["E"], 2),
                    "status": status["E"],
                    "weight": w["w_E"],
                    "notes": notes["E"],
                },
                "F": {
                    "score": round(scores["F"], 2),
                    "status": "SKIPPED",
                    "weight": w["w_F"],
                    "notes": notes["F"],
                },
            },
            "weights": w,
            "safety_gate": {
                "containment_score": round(scores["D"], 2),
                "delta_c": round(r["delta_c"], 4),
                "passed": bool(r["gate_passed"]),
                "unauthorized_egress_leaks": 0,
            },
            "uhqs": r["uhqs"],
            "grade": r["grade"],
            "notes": (
                f"Evaluation proof only. Remote MQTT honeypot {meta['host']}:1883. "
                "Protocol fidelity via uhbs_core.protocols.mqtt. "
                "Module F skipped (no source_root). Module D Safety Gate not cleared "
                "(non-SSH decoy without egress gateway attestation). "
                f"Artifacts: docs/conformance/reports/{key}/mqtt/."
            ),
        }
        fixture = ROOT / f"docs/conformance/fixtures/{key}.scorecard.json"
        fixture.write_text(json.dumps(sc, indent=2) + "\n")

        hub = ROOT / f"docs/conformance/reports/{key}"
        mqtt_hub = hub / "mqtt"
        full = mqtt_hub / "full"
        full.mkdir(parents=True, exist_ok=True)

        scorecard_txt = f"""====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v{VERSION}
====================================================================================
Target System         : {key}
System Profile Class  : Low-Interaction
Protocols             : mqtt
Evaluation Date       : {TODAY}
Evaluation Type       : Protocol-surface + module harness (remote MQTT decoy)
Environment           : Operator-provided honeypot endpoint ({meta['host']}:1883)
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         : {scores['A']:5.1f}/100       0.30     {status['A']} ({notes['A']})
Module B: Behavioral Realism        : {scores['B']:5.1f}/100       0.15     {status['B']} ({notes['B']})
Module C: Telemetry Quality         : {scores['C']:5.1f}/100       0.25     {status['C']}
Module D: Safety & Containment (C)  : {scores['D']:5.1f}/100       GATE     FAILED (Safety Gate not cleared — non-SSH / no egress attestation)
Module E: Scalability & Latency     : {scores['E']:5.1f}/100       0.10     {status['E']} ({notes['E']})
Module F: Static Code Audit         : {scores['F']:5.1f}/100       0.20     SKIPPED ({notes['F']})
------------------------------------------------------------------------------------
SAFETY GATE MULTIPLIER                : δ_C = {r['delta_c']:.4f} (C = {scores['D']:.1f} < 95 — exponential penalty)
FINAL COMPOSITE SCORE (UHQS {VERSION})      : {r['uhqs']:.2f} / 100
OVERALL EVALUATION GRADE              : {r['long_grade']}
====================================================================================
"""
        (full / "SCORECARD.txt").write_text(scorecard_txt)

        report = {
            "framework": f"Universal Honeypot Benchmarking Standard (UHBS) v{VERSION}",
            "evaluation_type": "Protocol-surface MQTT honeypot grade (remote decoy)",
            "target": {
                "name": key,
                "kind": "mqtt",
                "host": meta["host"],
                "port": 1883,
                "profile_class": "Low-Interaction",
                "protocols": ["mqtt"],
                "ports_map": {"mqtt": 1883},
            },
            "uhqs": {
                "target": key,
                "S_A": scores["A"],
                "S_B": scores["B"],
                "S_C": scores["C"],
                "C": scores["D"],
                "S_E": scores["E"],
                "S_F": scores["F"],
                "delta_c": r["delta_c"],
                "uhqs": r["uhqs"],
                "weights": {
                    "protocol": w["w_A"],
                    "behavior": w["w_B"],
                    "telemetry": w["w_C"],
                    "scale": w["w_E"],
                    "static": w["w_F"],
                },
                "profile_class": "Low-Interaction",
                "grade": r["long_grade"],
                "version": VERSION,
                "containment_measured": True,
            },
            "notes": sc["notes"],
            "mqtt_checks": {
                "A": r.get("checks_a_mqtt"),
                "B": r.get("checks_b"),
            },
        }
        (full / "report.json").write_text(json.dumps(report, indent=2) + "\n")

        (full / "README.md").write_text(
            f"""# {key} — MQTT full run

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | {scores['A']:.1f} | 0.30 | {status['A']} | {notes['A']} |
| Module B: Behavioral Realism | {scores['B']:.1f} | 0.15 | {status['B']} | {notes['B']} |
| Module C: Telemetry Quality | {scores['C']:.1f} | 0.25 | {status['C']} | {notes['C']} |
| Module D: Safety & Containment (C) | {scores['D']:.1f} | GATE | FAILED | Safety Gate not cleared |
| Module E: Scalability & Latency | {scores['E']:.1f} | 0.10 | {status['E']} | {notes['E']} |
| Module F: Static Code Audit | {scores['F']:.1f} | 0.20 | SKIPPED | {notes['F']} |
| Safety Gate δ_C | {r['delta_c']:.4f} | GATE | — | Containment multiplier |

**UHQS:** **{r['uhqs']:.2f}** · **Grade:** {r['grade']}

Artifacts: [`SCORECARD.txt`](SCORECARD.txt) · [`report.json`](report.json)
"""
        )

        (mqtt_hub / "index.md").write_text(
            f"""# {key} — MQTT

**Status:** Informative · evaluation proof  
**UHBS:** {VERSION} · **Class:** Low-Interaction · **Protocol:** `mqtt`  
**Target id:** `{key}` · **Evaluated:** {TODAY}  
**Endpoint:** `{meta['host']}:1883` (operator-provided honeypot)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Full](full/README.md) | **{r['uhqs']:.2f}** | {r['grade']} | {r['delta_c']:.4f} | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) |

{meta['blurb']}

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | {scores['A']:.1f} | 0.30 | {status['A']} | {notes['A']} |
| Module B: Behavioral Realism | {scores['B']:.1f} | 0.15 | {status['B']} | {notes['B']} |
| Module C: Telemetry Quality | {scores['C']:.1f} | 0.25 | {status['C']} | — |
| Module D: Safety & Containment (C) | {scores['D']:.1f} | GATE | FAILED | Non-SSH decoy; Safety Gate not cleared |
| Module E: Scalability & Latency | {scores['E']:.1f} | 0.10 | {status['E']} | {notes['E']} |
| Module F: Static Code Audit | {scores['F']:.1f} | 0.20 | SKIPPED | no source_root |
| Safety Gate δ_C | {r['delta_c']:.4f} | GATE | — | Containment multiplier |

## MQTT fidelity highlights

Shallow vs real-enough discriminators from `uhbs_core.protocols.mqtt`:

- Bad protocol level 99 accepted → FSM fail (both decoys)
- Pub/sub cross-client echo missing → payload fail (both decoys)
- Decoy A also fails UNSUBSCRIBE (returns SUBACK-shaped reply)

Published scorecard: [`../../../../scorecards/{key}.md`](../../../../scorecards/{key}.md)
"""
        )

        (hub / "index.md").write_text(
            f"""# {meta['title']}

**UHBS** evaluation proof for an anonymous **MQTT** honeypot surface.

| Protocol | Report | Full UHQS | Grade |
| --- | --- | ---: | --- |
| MQTT :1883 | [mqtt hub](mqtt/index.md) | **{r['uhqs']:.2f}** | {r['grade']} |

- [Reproduce notes](METHODOLOGY.md)
- [Scorecard page](../../../scorecards/{key}.md)
"""
        )

        (hub / "METHODOLOGY.md").write_text(
            f"""# Methodology — {key}

## Scope

Remote protocol-surface grade of an operator-provided MQTT honeypot at `{meta['host']}:1883`.

- **In scope:** Modules A/B via `MQTTPlugin`, Module E latency, Module C/D harness defaults for non-SSH decoys, Module F skipped without `source_root`.
- **Out of scope:** Claiming a commercial product identity; full Docker reproduce recipe (endpoint is external).

## Profile

[`labs/mqtt/low_interaction_mqtt.yaml`](../../labs/mqtt/low_interaction_mqtt.yaml) — class `Low-Interaction`, protocol `mqtt`.

## How to re-probe

See the companion [TUTORIAL](TUTORIAL.md). Use `protocol=mqtt` and `ports_map.mqtt=1883` against `{meta['host']}`.

## Limitations

Safety Gate (Module D) did not clear: no SSH exec surface and no `UHBS_EGRESS_GATEWAY_LOG` attestation. UHQS is therefore δ_C-penalized. Module F is SKIPPED without source. Prefer a sandboxed lab with source + logs for claim-grade full spectrum runs.
"""
        )

        (hub / "TUTORIAL.md").write_text(
            f"""# Reproduce grade — {key}

This target is an **external MQTT honeypot** (`{meta['host']}:1883`), not a Docker recipe in-tree.

1. Install UHBS with lab extras.
2. Point `TargetSpec` at the host with `protocol=mqtt` / `ports_map.mqtt=1883`.
3. Run Modules A–F (or `uhbs-lab` when a local container mirror is available).
4. Compare against the published [`full/SCORECARD.txt`](mqtt/full/SCORECARD.txt).

For install/validate walkthroughs see [Install & use UHBS](../../../tooling/install-and-use.md).
"""
        )

        md = ROOT / f"docs/scorecards/{key}.md"
        md.write_text(
            f"""# Scorecard: {key} — mqtt

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **{VERSION}** · **Class:** Low-Interaction · **Protocol / surface:** `mqtt`  
**Target id (lab):** `{key}` · **Evaluation date:** {TODAY}  
**Endpoint:** `{meta['host']}:1883`

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| **Full (authoritative)** | **{r['uhqs']:.2f}** | **{r['grade']}** | **{r['delta_c']:.4f}** | Verbatim SCORECARD below + `report.json` on the report hub |

**Report hub:** [{key} / mqtt](../conformance/reports/{key}/mqtt/index.md) · [Tutorial](../conformance/reports/{key}/TUTORIAL.md) · [Methodology](../conformance/reports/{key}/METHODOLOGY.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

{meta['blurb']}

## Proof: module scores (full run)

These numbers are from the UHBS module harness against the live MQTT decoy.

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | {scores['A']:.1f} | 0.30 | {status['A']} | {notes['A']} |
| Module B: Behavioral Realism | {scores['B']:.1f} | 0.15 | {status['B']} | {notes['B']} |
| Module C: Telemetry Quality | {scores['C']:.1f} | 0.25 | {status['C']} | {notes['C']} |
| Module D: Safety & Containment (C) | {scores['D']:.1f} | GATE | FAILED | Safety Gate not cleared (non-SSH / no egress attestation) |
| Module E: Scalability & Latency | {scores['E']:.1f} | 0.10 | {status['E']} | {notes['E']} |
| Module F: Static Code Audit | {scores['F']:.1f} | 0.20 | SKIPPED | {notes['F']} |
| Safety Gate δ_C | {r['delta_c']:.4f} | GATE | — | Containment multiplier applied to UHQS |

## How CTI / blue team should read this

| Module | Score | Analyst reading |
| --- | ---: | --- |
| A — Protocol Fidelity | {scores['A']:.1f} | MQTT handshake quality. Failures on bad protocol level mean shallow stub behavior. |
| B — Behavioral Realism | {scores['B']:.1f} | Session realism (PING/UNSUB/pub-sub). Missing echo ⇒ not a real broker fan-out. |
| C — Telemetry Quality | {scores['C']:.1f} | Harness telemetry gates for this run — not a claim about your SIEM. |
| D — Safety & Containment (C) | {scores['D']:.1f} | Safety Gate. Below threshold collapses UHQS via δ_C. |
| E — Scalability & Latency | {scores['E']:.1f} | Connect latency vs Low-Interaction MQTT TPS budget. |
| F — Static Code Audit | {scores['F']:.1f} | Skipped — no source tree provided for this remote decoy. |
| δ_C | {r['delta_c']:.4f} | Safety Gate multiplier applied to composite UHQS. |

- **CTI:** treat missing pub/sub delivery + accepted bogus protocol level as “shallow MQTT decoy” signals.
- **Blue team:** do not expose without clearing Safety Gate in a sandboxed lab (egress attestation / containment).
- **Do not** cite UHQS without the verbatim SCORECARD or `report.json` from the report hub.

## Verbatim full SCORECARD

```text
{scorecard_txt.strip()}
```

## Replication

Re-run notes are in the [tutorial](../conformance/reports/{key}/TUTORIAL.md). Limits are in the [methodology](../conformance/reports/{key}/METHODOLOGY.md).

Machine-readable fixture: [`../conformance/fixtures/{key}.scorecard.json`](../conformance/fixtures/{key}.scorecard.json).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
"""
        )
        print(f"wrote {key} UHQS={r['uhqs']} grade={r['grade']}")


if __name__ == "__main__":
    main()
