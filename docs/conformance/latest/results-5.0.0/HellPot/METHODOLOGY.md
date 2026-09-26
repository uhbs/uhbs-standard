# HellPot (yunginnanet) (http) methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `ubuntu-wrapper` · base `ubuntu:latest`

Upstream Dockerfile is golang:1.23 + distroless; lab uses golang:1.23 builder then ubuntu:latest runtime with catch-all bind and no curl UA blacklist.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/yunginnanet/HellPot.git |
| Branch / commit | `main` / `0ba62c99ea4599ec32474e4982a8ea4d4105c471` |
| Target image | `hellpot:uhbs-lab` |
| Host / port | `HellPot-lab` : `8080` |
| Inventory | `docs/conformance/labs/HellPot/inventory.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

`UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
