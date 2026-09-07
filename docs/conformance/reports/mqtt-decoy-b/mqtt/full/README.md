# mqtt-decoy-b — MQTT full run

| Module | Score | Weight | Status | Notes |
| --- | ---: | --- | --- | --- |
| Module A: Protocol Fidelity | 86.8 | 0.30 | PASSED | fsm=67 nego=100 timing=100 |
| Module B: Behavioral Realism | 65.0 | 0.15 | PARTIAL | mqtt.payload.pubsub_echo |
| Module C: Telemetry Quality | 100.0 | 0.25 | PASSED | UHBS C1 schema: STIX 2.1 / OTel / ECS best-effort validators |
| Module D: Safety & Containment (C) | 55.0 | GATE | FAILED | Safety Gate not cleared |
| Module E: Scalability & Latency | 100.0 | 0.10 | PASSED | P50=57.7ms P95=65.7ms P99=66.9ms TPS_limit=300.0ms proto=mqtt |
| Module F: Static Code Audit | 0.0 | 0.20 | SKIPPED | no source_root configured |
| Safety Gate δ_C | 0.3025 | GATE | — | Containment multiplier |

**UHQS:** **21.41** · **Grade:** F

Artifacts: [`SCORECARD.txt`](SCORECARD.txt) · [`report.json`](report.json)
