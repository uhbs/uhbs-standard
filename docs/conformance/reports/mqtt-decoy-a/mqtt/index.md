# mqtt-decoy-a — MQTT

**Status:** Informative · evaluation proof  
**UHBS:** 4.6.0 · **Class:** Low-Interaction · **Protocol:** `mqtt`  
**Target id:** `mqtt-decoy-a` · **Evaluated:** 2026-09-07  
**Endpoint:** `98.90.197.80:1883` (operator-provided honeypot)

| Run | UHQS | Grade | δ_C | Artifacts |
| --- | ---: | --- | --- | --- |
| [Full](full/README.md) | **20.66** | F | 0.3025 | [`SCORECARD.txt`](full/SCORECARD.txt) · [`report.json`](full/report.json) |

Anonymous MQTT :1883 honeypot (operator-provided). Weaker state machine (bad UNSUBACK).

## Full run — module breakdown

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.8 | 0.30 | PASSED | fsm=67 nego=100 timing=100 |
| Module B: Behavioral Realism | 48.4 | 0.15 | PARTIAL | mqtt.state.unsubscribe,mqtt.payload.pubsub_echo |
| Module C: Telemetry Quality | 100.0 | 0.25 | PASSED | — |
| Module D: Safety & Containment (C) | 55.0 | GATE | FAILED | Non-SSH decoy; Safety Gate not cleared |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | P50=57.5ms P95=59.2ms P99=61.3ms TPS_limit=300.0ms proto=mqtt |
| Module F: Static Code Audit | 0.0 | 0.20 | SKIPPED | no source_root |
| Safety Gate δ_C | 0.3025 | GATE | — | Containment multiplier |

## MQTT fidelity highlights

Shallow vs real-enough discriminators from `uhbs_core.protocols.mqtt`:

- Bad protocol level 99 accepted → FSM fail (both decoys)
- Pub/sub cross-client echo missing → payload fail (both decoys)
- Decoy A also fails UNSUBSCRIBE (returns SUBACK-shaped reply)

Published scorecard: [`../../../../scorecards/mqtt-decoy-a.md`](../../../../scorecards/mqtt-decoy-a.md)
