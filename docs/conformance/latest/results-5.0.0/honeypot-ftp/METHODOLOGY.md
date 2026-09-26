# Methodology: honeypot-ftp UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `c7b7cbed4c52d3d84b62676dd1a359c6d9da2696` (`master`)

## Runtime

- Strategy: `ubuntu-wrapper`
- Base image: `ubuntu:latest`
- Reason: ubuntu-wrapper: no upstream Dockerfile; Twisted FTP lab entry ftp_lab.py plus base/handler stubs.
- Target image: `honeypot-ftp:uhbs-lab` (`sha256:7ef087855d43efbabddee32c56b5ff87db7f29702a33c58af123758571e1a7ff`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

honeypot-ftp (FTP :21) — quick and full for each. Honest v5: **INCOMPLETE / ungraded (non-SSH Module D)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
