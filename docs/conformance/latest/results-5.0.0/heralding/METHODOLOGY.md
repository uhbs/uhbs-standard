# Methodology: heralding UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `ac12724ab38c4e2fe78f07d1bc35e6e586ba69c0` (`master`)

## Runtime

- Strategy: `custom-base`
- Base image: `python:3.11-slim-bookworm`
- Reason: custom-base: upstream python:3.9-slim-bullseye apt indexes 404; ubuntu:latest + CPython 3.14 failed psycopg2-binary.
- Target image: `heralding:uhbs-lab` (`sha256:3acb74f08830ef00aefd5c19bc94697f41317827928c14ac14b09d9c018a37f4`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

Heralding (FTP :21), Heralding (SMTP :25), Heralding (SSH :22) — quick and full for each. Honest v5: **ungraded (INCOMPLETE and/or GATE_FAILED)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
