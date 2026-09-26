# Elastichoney (jordan-wright) (http) methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `ubuntu-wrapper` · base `ubuntu:latest`

Upstream Dockerfile is golang:1.3-onbuild (unusable). Built with golang:1.22 and ran on ubuntu:latest; anonymous=true avoids outbound IP lookup.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/jordan-wright/elastichoney.git |
| Branch / commit | `master` / `1b03740e34c6a60991432d53c237773d484571eb` |
| Target image | `elastichoney:uhbs-lab` |
| Host / port | `elastichoney-lab` : `9200` |
| Inventory | `docs/conformance/labs/elastichoney/inventory.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

`UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
