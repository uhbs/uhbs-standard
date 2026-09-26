# Methodology: Cowrie UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `fef0d620962e23194a9d34a048488f9c76c85835` (`main`)

## Runtime

- Strategy: `upstream-docker`
- Base image: `gcr.io/distroless/python3-debian13`
- Reason: Official cowrie/cowrie:latest (OCI base gcr.io/distroless/python3-debian13); lab overlay enables Telnet :2223.
- Target image: `cowrie/cowrie:latest` (`sha256:92b9220978bc6095fb72b1a046240604ed03a5be1344abf6a2dd04eadd4cd330`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

Cowrie (SSH :2222), Cowrie (Telnet :2223) — quick and full for each. Honest v5: **ungraded (INCOMPLETE and/or GATE_FAILED)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
