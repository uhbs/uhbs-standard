# HoneyUp (http) methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `ubuntu-wrapper` · base `ubuntu:latest`

Upstream docker-compose + Dockerfile.dev reclones GitHub during build. Lab builds the cloned HEAD tree on ubuntu:latest with cargo.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/LogoiLab/honeyup.git |
| Branch / commit | `master` / `2d0169da30e76eed979a9a0950015b90f0454740` |
| Target image | `honeyup:uhbs-lab` |
| Host / port | `honeyup-lab` : `4000` |
| Inventory | `docs/conformance/labs/honeyup/inventory.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

`UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
