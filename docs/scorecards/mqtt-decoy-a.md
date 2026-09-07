# Scorecard: mqtt-decoy-a — mqtt

**Status:** Informative · evaluation proof (not an endorsement)  
**UHBS:** **4.6.0** · **Class:** Low-Interaction · **Protocol / surface:** `mqtt`  
**Target id (lab):** `mqtt-decoy-a` · **Evaluation date:** 2026-09-07  
**Endpoint:** `98.90.197.80:1883`

| Run | UHQS | Grade | δ_C | Proof artifacts |
| --- | ---: | --- | --- | --- |
| **Full (authoritative)** | **20.66** | **F** | **0.3025** | Verbatim SCORECARD below + `report.json` on the report hub |

**Report hub:** [mqtt-decoy-a / mqtt](../conformance/reports/mqtt-decoy-a/mqtt/index.md) · [Tutorial](../conformance/reports/mqtt-decoy-a/TUTORIAL.md) · [Methodology](../conformance/reports/mqtt-decoy-a/METHODOLOGY.md)  
**How to read UHQS:** [CTI / blue-team guide](../conformance/reports/READING-UHQS.md)

Anonymous MQTT :1883 honeypot (operator-provided). Weaker state machine (bad UNSUBACK).

## Proof: module scores (full run)

These numbers are from the UHBS module harness against the live MQTT decoy.

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.8 | 0.30 | PASSED | fsm=67 nego=100 timing=100 |
| Module B: Behavioral Realism | 48.4 | 0.15 | PARTIAL | mqtt.state.unsubscribe,mqtt.payload.pubsub_echo |
| Module C: Telemetry Quality | 100.0 | 0.25 | PASSED | UHBS C1 schema: STIX 2.1 / OTel / ECS best-effort validators |
| Module D: Safety & Containment (C) | 55.0 | GATE | FAILED | Safety Gate not cleared (non-SSH / no egress attestation) |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | P50=57.5ms P95=59.2ms P99=61.3ms TPS_limit=300.0ms proto=mqtt |
| Module F: Static Code Audit | 0.0 | 0.20 | SKIPPED | no source_root configured |
| Safety Gate δ_C | 0.3025 | GATE | — | Containment multiplier applied to UHQS |

## How CTI / blue team should read this

| Module | Score | Analyst reading |
| --- | ---: | --- |
| A — Protocol Fidelity | 86.8 | MQTT handshake quality. Failures on bad protocol level mean shallow stub behavior. |
| B — Behavioral Realism | 48.4 | Session realism (PING/UNSUB/pub-sub). Missing echo ⇒ not a real broker fan-out. |
| C — Telemetry Quality | 100.0 | Harness telemetry gates for this run — not a claim about your SIEM. |
| D — Safety & Containment (C) | 55.0 | Safety Gate. Below threshold collapses UHQS via δ_C. |
| E — Scalability & Latency | 100.0 | Connect latency vs Low-Interaction MQTT TPS budget. |
| F — Static Code Audit | 0.0 | Skipped — no source tree provided for this remote decoy. |
| δ_C | 0.3025 | Safety Gate multiplier applied to composite UHQS. |

- **CTI:** treat missing pub/sub delivery + accepted bogus protocol level as “shallow MQTT decoy” signals.
- **Blue team:** do not expose without clearing Safety Gate in a sandboxed lab (egress attestation / containment).
- **Do not** cite UHQS without the verbatim SCORECARD or `report.json` from the report hub.

## Verbatim full SCORECARD

```text
====================================================================================
                  UNIVERSAL HONEYPOT BENCHMARK SCORECARD v4.6.0
====================================================================================
Target System         : mqtt-decoy-a
System Profile Class  : Low-Interaction
Protocols             : mqtt
Evaluation Date       : 2026-09-07
Evaluation Type       : Protocol-surface + module harness (remote MQTT decoy)
Environment           : Operator-provided honeypot endpoint (98.90.197.80:1883)
------------------------------------------------------------------------------------
EVALUATION MODULE                     SCORE (0-100)    WEIGHT    STATUS
------------------------------------------------------------------------------------
Module A: Protocol Fidelity         :  86.8/100       0.30     PASSED (fsm=67 nego=100 timing=100)
Module B: Behavioral Realism        :  48.4/100       0.15     PARTIAL (mqtt.state.unsubscribe,mqtt.payload.pubsub_echo)
Module C: Telemetry Quality         : 100.0/100       0.25     PASSED
Module D: Safety & Containment (C)  :  55.0/100       GATE     FAILED (Safety Gate not cleared — non-SSH / no egress attestation)
Module E: Scalability & Latency     : 100.0/100       0.10     PASSED (P50=57.5ms P95=59.2ms P99=61.3ms TPS_limit=300.0ms proto=mqtt)
Module F: Static Code Audit         :   0.0/100       0.20     SKIPPED (no source_root configured)
------------------------------------------------------------------------------------
SAFETY GATE MULTIPLIER                : δ_C = 0.3025 (C = 55.0 < 95 — exponential penalty)
FINAL COMPOSITE SCORE (UHQS 4.6.0)      : 20.66 / 100
OVERALL EVALUATION GRADE              : GRADE F (Fail)
====================================================================================
```

## Replication

Re-run notes are in the [tutorial](../conformance/reports/mqtt-decoy-a/TUTORIAL.md). Limits are in the [methodology](../conformance/reports/mqtt-decoy-a/METHODOLOGY.md).

Machine-readable fixture: [`../conformance/fixtures/mqtt-decoy-a.scorecard.json`](../conformance/fixtures/mqtt-decoy-a.scorecard.json).

> Product names appear only under conformance as evaluation proof — not UHBS requirements.
