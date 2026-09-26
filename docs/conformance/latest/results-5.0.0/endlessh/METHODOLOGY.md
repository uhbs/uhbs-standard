# Endlessh (skeeto SSH tarpit) methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `upstream-docker` · base `alpine:3.9`

Upstream Dockerfile pins alpine:3.9 for the C builder/runtime; Ubuntu latest is not the documented image.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/skeeto/endlessh.git |
| Branch / commit | `master` / `dfe44eb2c5b6fc3c48a39ed826fe0e4459cdf6ef` |
| Target image | `endlessh:lab` |
| Host / port | `endlessh-lab` : `2222` |
| Inventory | `docs/conformance/labs/endlessh/inventory.yaml` |
| Quick TPS | `docs/conformance/labs/endlessh/low_interaction_quick.yaml` |
| Full TPS | `docs/conformance/labs/endlessh/low_interaction_full.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

Limitations: `UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
