# Methodology: mysql-honeypotd UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `955ecce4ce22c8588da1f023dfd790099755d575` (`master`)

## Runtime

- Strategy: `upstream-docker`
- Base image: `scratch`
- Reason: upstream-docker: alpine:3.24 build, scratch static release (MINIMALISTIC_BUILD). Do not pass -f/-x; those flags are unrecognized in the minimal binary.
- Target image: `mysql-honeypotd:uhbs-lab` (`sha256:9445e1b2ea7b16061cb3218a56ce374f3bf401155aa83e32980078da5736e9b1`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

mysql-honeypotd (MySQL :3306) — quick and full for each. Honest v5: **INCOMPLETE / ungraded (non-SSH Module D)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
