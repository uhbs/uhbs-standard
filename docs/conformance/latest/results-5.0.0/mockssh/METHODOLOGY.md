# MockSSH methodology (results-5.0.1)

**UHBS:** 5.0.1 · strategy `ubuntu-wrapper` · base `ubuntu:24.04`

No upstream Docker image. Ubuntu 24.04 wrapper installs the tree with `pip install -e .`. `examples/mock_cisco.py` binds `127.0.0.1:9999`; lab entry listens `0.0.0.0:2222` so the grader on `uhbs-lab` can reach it. Auth is `testadmin` / `x`. Cisco CLI decoy — not a POSIX shell.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/ncouture/MockSSH.git |
| Branch / commit | `main` / `d2d49b6121544818560ce8e56f306ccf75f961b3` |
| Target image | `mockssh:uhbs-lab` |
| Host / port | `mockssh-lab` : `2222` |
| Verdict | COMPLETE / GATE_PASSED / UHQS 41.75 / F |

Limitations: `UHBS_AIRGAP_ATTESTED=1` is operator attestation. Product name is evaluation proof only.
