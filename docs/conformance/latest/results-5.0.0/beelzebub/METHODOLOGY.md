# Methodology: Beelzebub multi-protocol UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `67d5632a754f39f7b14c703d3009193150440116` (`main`)

## Runtime

- Strategy: `upstream-docker` (README `./install.sh --docker` / Compose; `Dockerfile` builder `golang:alpine`, final `scratch`)
- Reason not Ubuntu latest: upstream ships a maintained multi-stage Dockerfile as the documented install path
- Target image: `beelzebub:uhbs-lab` (`sha256:4663259f7336af0895572db5ec697518fc5608846dd54870d0baaec8f70172d3`)
- Network: Docker `uhbs-lab`, alias `beelzebub-lab`
- Lab overlay: `docs/conformance/labs/beelzebub/configurations/` — static SSH/HTTP/Telnet/Redis/MCP YAMLs (no live LLM keys). Upstream `ssh-2222.yaml` is an OpenAI plugin example and is **not** used.
- `logsPath: ./logs` is opened as a file (`os.OpenFile`); host file bind-mounted at `/logs`

## What was graded in this pass

SSH, TELNET, HTTP, MCP, REDIS — quick and full, **INCOMPLETE / ungraded** (honest v5 Safety Gate). Shared target container for all five UHBS-native protocols.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- Telemetry: docker logs dumped to `.local/labs/beelzebub-telemetry/beelzebub-docker.log`
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Scratch final image has no shell; smoke checks run from `uhbs:5.0.0` with `--entrypoint python3`
- Product name is evaluation proof only
