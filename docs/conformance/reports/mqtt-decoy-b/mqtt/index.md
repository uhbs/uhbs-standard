# mqtt-decoy-b — MQTT

**Status:** Informative · evaluation proof  
**UHBS:** 4.6.0 · **Class:** Low-Interaction · **Protocol:** `mqtt`  
**Target id:** `mqtt-decoy-b` · **Evaluated:** 2026-09-07  
**Endpoint:** `3.84.184.144:1883` (operator-provided honeypot)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Full](full/README.md) | **21.41** | F | 0.3025 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) |

Anonymous MQTT :1883 honeypot (operator-provided). Stronger session verbs; still no pub/sub delivery.

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.8 | 0.30 | PASSED | fsm=67 nego=100 timing=100 |
| Module B: Behavioral Realism | 65.0 | 0.15 | PARTIAL | mqtt.payload.pubsub_echo |
| Module C: Telemetry Quality | 100.0 | 0.25 | PASSED | — |
| Module D: Safety & Containment (C) | 55.0 | GATE | FAILED | Non-SSH decoy; Safety Gate not cleared |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | P50=57.7ms P95=65.7ms P99=66.9ms TPS_limit=300.0ms proto=mqtt |
| Module F: Static Code Audit | 0.0 | 0.20 | SKIPPED | no source_root |
| Safety Gate δ_C | 0.3025 | GATE | — | Containment multiplier |

## MQTT fidelity highlights

Shallow vs real-enough discriminators from `uhbs_core.protocols.mqtt`:

- Bad protocol level 99 accepted → FSM fail (both decoys)
- Pub/sub cross-client echo missing → payload fail (both decoys)
- Decoy A also fails UNSUBSCRIBE (returns SUBACK-shaped reply)

Published scorecard: [`../../../scorecards/mqtt-decoy-b.md`](../../../scorecards/mqtt-decoy-b.md)
