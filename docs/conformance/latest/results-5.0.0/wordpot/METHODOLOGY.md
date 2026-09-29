# wordpot (gbrindisi) (http) methodology (results-5.0.1)

**UHBS:** 5.0.1 · strategy `custom-base` · base `python:2.7-slim`

Upstream is Python 2 (print statements) + Flask 0.10. Ubuntu latest has no Python 2, so python:2.7-slim is required.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/gbrindisi/wordpot.git |
| Branch / commit | `master` / `e96889bd5a35bbdd9fb2dd4cd583475cf7d25962` |
| Target image | `wordpot:uhbs-lab` |
| Host / port | `wordpot-lab` : `8080` |
| Inventory | `docs/conformance/labs/wordpot/inventory.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

`UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
