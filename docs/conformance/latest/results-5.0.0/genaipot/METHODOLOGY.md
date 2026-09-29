# Methodology: GenAIPot UHBS lab (results-5.0.1)

**Status:** Informative  
**UHBS:** 5.0.1 · Images `uhbs:5.0.1` (quick) / `uhbs:5.0.1-full` (full)  
**Upstream commit:** `205ffe40008f2e76e0decdb01bc19bf8e00acd8a` (`main`)

## Runtime

- Strategy: `upstream-docker`
- Base image: `python:3.9-slim`
- Reason: upstream-docker Hub image annls/genaipot:latest (Dockerfile FROM python:3.9-slim). ls1911/GenAIPot clone required auth; SHA matches eduardobsg/GenAIPot@205ffe4.
- Target image: `annls/genaipot:latest` (`sha256:627d7fde6d4a6f937fde3b3366fb55605a90cea6370e1f5beac9c39d8ecfeeac`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

GenAIPot (SMTP :25), GenAIPot (POP3 :110) — quick and full for each. Honest v5: **ungraded (INCOMPLETE and/or GATE_FAILED)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
