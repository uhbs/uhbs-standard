# Methodology: HoneyMCP UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `966bb908d140809957ba01e05132631c514ade5d` (`main`)

## Runtime

- Strategy: `upstream-docker`
- Base image: `debian:bookworm-slim`
- Reason: Upstream Dockerfile (rust:1.89-slim-bookworm builder, debian:bookworm-slim runtime). Lab patch raises governor per_second(50)/burst_size(500).
- Target image: `honeymcp:uhbs-lab` (`sha256:7110d509ad99de427cc88c0a00a0f8136a51a1c0b9a033b0868cb51954707a83`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

HoneyMCP (MCP :8080) — quick and full for each. Honest v5: **INCOMPLETE / ungraded (non-SSH Module D)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
