# Log4Pot (thomaspatzke) (http) methodology (results-5.0.1)

**UHBS:** 5.0.1 · strategy `ubuntu-wrapper` · base `ubuntu:latest`

No upstream Dockerfile. README allows running without Azure extras via python log4pot-server.py. Ubuntu latest + python3 (stdlib HTTP server).

| Field | Value |
| --- | --- |
| Upstream | https://github.com/thomaspatzke/Log4Pot.git |
| Branch / commit | `master` / `5002b1fe0f82359ef32dbc3a899e8a701dc3256e` |
| Target image | `log4pot:uhbs-lab` |
| Host / port | `Log4Pot-lab` : `8080` |
| Inventory | `docs/conformance/labs/Log4Pot/inventory.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

`UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
