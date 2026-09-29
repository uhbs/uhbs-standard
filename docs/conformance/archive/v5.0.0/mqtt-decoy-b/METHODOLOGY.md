# Methodology — mqtt-decoy-b

## Scope

Remote protocol-surface grade of an operator-provided MQTT honeypot at `3.84.184.144:1883`.

- **In scope:** Modules A/B via `MQTTPlugin`, Module E latency, Module C/D harness defaults for non-SSH decoys, Module F skipped without `source_root`.
- **Out of scope:** Claiming a commercial product identity; full Docker reproduce recipe (endpoint is external).

## Profile

[`labs/mqtt/low_interaction_mqtt.yaml`](../../labs/mqtt/low_interaction_mqtt.yaml) — class `Low-Interaction`, protocol `mqtt`.

## How to re-probe

See the companion [TUTORIAL](TUTORIAL.md). Use `protocol=mqtt` and `ports_map.mqtt=1883` against `3.84.184.144`.

## Limitations

Safety Gate (Module D) did not clear: no SSH exec surface and no `UHBS_EGRESS_GATEWAY_LOG` attestation. UHQS is therefore δ_C-penalized. Module F is SKIPPED without source. Prefer a sandboxed lab with source + logs for claim-grade full spectrum runs.
