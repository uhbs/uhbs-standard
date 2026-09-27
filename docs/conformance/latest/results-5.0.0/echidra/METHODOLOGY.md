# EchidraOSS methodology (results-5.0.0)

**UHBS:** 5.0.0 · strategy `upstream-docker` · base `python:3.11-slim`

Upstream documents Docker Compose. The honeypot image is built from the repo `Dockerfile` (`FROM python:3.11-slim`). Ubuntu latest is not the documented image. Lab overlay names the listener `echidra-lab` on external network `uhbs-lab` and drops macOS-incompatible timezone binds. Host-key volume must be `chown 1000:1000` or SSH fails with `PermissionError` on `data/ssh_host_key`.

| Field | Value |
| --- | --- |
| Upstream | https://github.com/Qyleron/EchidraOSS.git |
| Branch / commit | `main` / `50305356ffe49a20459b89b071dc30bb2598e88b` |
| Target image | `echidra-uhbs-honeypot:latest` |
| Host / port | `echidra-lab` : `2222` |
| Auth | `root` / `admin` |
| Inventory | `docs/conformance/labs/echidra/inventory.yaml` |
| Quick TPS | `docs/conformance/labs/echidra/low_interaction_ssh_quick.yaml` |
| Full TPS | `docs/conformance/labs/echidra/low_interaction_ssh_full.yaml` |
| Verdict | COMPLETE / GATE_PASSED / UHQS 36.58 / F |

Limitations: `UHBS_AIRGAP_ATTESTED=1` is operator attestation, not a physical air-gap. `UHBS_SSH_KNOWN_HOSTS` from `ssh-keyscan` is required; without it Module B/D cannot open an SSH session. Product name is evaluation proof only. Postgres `persona_configs` may be missing on a fresh volume; SSH still listens.
