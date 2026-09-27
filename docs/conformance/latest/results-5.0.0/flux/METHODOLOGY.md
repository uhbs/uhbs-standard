# flux (http) methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `custom-base` · base `python:3.12-slim`

No upstream Dockerfile. README is pip install aiohttp; python -m flux (Python 3.11+). python:3.12-slim matches documented runtime; bind patched 0.0.0.0:8080; tarpit disabled so grader probes on /login do not hang.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/andrewmichaelsmith/flux.git |
| Branch / commit | `main` / `0db4b8b0b87243d2061137212e49311bfbbd38b1` |
| Target image | `flux:uhbs-lab` |
| Host / port | `flux-lab` : `8080` |
| Inventory | `docs/conformance/labs/flux/inventory.yaml` |
| Verdict | INCOMPLETE / INCOMPLETE |

`UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. Product name is evaluation proof only.
