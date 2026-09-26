# Methodology: pghoney UHBS lab (results-5.0.0)

**Status:** Informative  
**UHBS:** 5.0.0 · Images `uhbs:5.0.0` (quick) / `uhbs:5.0.0-full` (full)  
**Upstream commit:** `f5d367f749f7e9353421aaf44dad856df490c441` (`master`)

## Runtime

- Strategy: `ubuntu-wrapper`
- Base image: `ubuntu:latest`
- Reason: ubuntu-wrapper Go build; hpfeeds disabled; bind 0.0.0.0; go get github.com/lib/pq.
- Target image: `pghoney:uhbs-lab` (`sha256:09367f266cf3fde5bd31d367e5d3b26d6637329d587bcde9b935490c5ee7bc4e`)
- Network: Docker `uhbs-lab` (inventory aliases, no host port publish)

## What was graded in this pass

pghoney (Postgres :5432) — quick and full for each. Honest v5: **INCOMPLETE / ungraded (non-SSH Module D)**.

## Measured vs attested

- Air-gap: attested (`UHBS_AIRGAP_ATTESTED=1`), not a physical air-gap
- Egress: empty `egress-gateway.log` canary (no HIT lines)
- SAST: bandit + semgrep under `full/static/` (full image)

## Limitations

- Do not transplant archived 4.x letter grades
- Product name is evaluation proof only
- Module D: attestation never clears the gate; non-SSH units stay INCOMPLETE without gateway/packet evidence
