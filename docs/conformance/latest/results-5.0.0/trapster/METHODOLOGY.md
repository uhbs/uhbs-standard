# Methodology: Trapster Community multi-protocol UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `c6cc6638e9cc9fd28e38ec6846f2b92cbf01d2b7` (`main`)

## Runtime

- Strategy: `upstream-docker` (README `docker compose up --build`; `Dockerfile` `FROM python:3.11-slim`)
- Reason not Ubuntu latest: upstream ships a maintained Python 3.11 slim image as the documented install path
- Target image: `trapster:uhbs-lab` (`sha256:08f0789a3544e085f1be690f1fcf7fde76e3e1d67121696b48a1ab14de612c8c`)
- Network: Docker `uhbs-lab`, alias `trapster-lab`
- Lab overlay: `docs/conformance/labs/trapster/trapster.conf` (non-privileged ports)
- AI extras are installed by the upstream Dockerfile but no API key is provided

## What was graded in this pass

SSH `:2222`, HTTP `:8080`, FTP `:2121`, and Telnet `:2323` — quick and full for each, all **INCOMPLETE / ungraded** (honest v5 Safety Gate). Module F completed at 70.0 on full runs. Module C failed or stayed incomplete on declared native_json vs terminal logs. Module D critical controls remained NOT_TESTED/ERROR under `UHBS_AIRGAP_ATTESTED=1` plus empty egress canary (non-SSH units also need gateway/packet evidence).

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- Telemetry: docker logs dumped to `.local/labs/trapster-telemetry/trapster.log` (default JSON-to-terminal logger)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x SSH UHQS 44.38 / F
- First boot generates RSA-3072 SSH host keys (~1–2 minutes)
- Product name is evaluation proof only
