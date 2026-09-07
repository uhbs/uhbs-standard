# Reproduce grade — mqtt-decoy-b

This target is an **external MQTT honeypot** (`3.84.184.144:1883`), not a Docker recipe in-tree.

1. Install UHBS with lab extras.
2. Point `TargetSpec` at the host with `protocol=mqtt` / `ports_map.mqtt=1883`.
3. Run Modules A–F (or `uhbs-lab` when a local container mirror is available).
4. Compare against the published [`full/SCORECARD.txt`](mqtt/full/SCORECARD.txt).

For install/validate walkthroughs see [Install & use UHBS](../../../tooling/install-and-use.md).
