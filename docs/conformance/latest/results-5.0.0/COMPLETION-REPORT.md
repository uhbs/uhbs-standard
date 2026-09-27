# results-5.0.0 completion (measured-renorm)

- **Date:** 2026-09-27
- **Branch:** `benchmark-refresh-results-v1`
- **scoring_model_id:** `uhqs-v5.2-measured-renorm`
- **Method:** Recomputed UHQS from existing module scores. Unmeasured modules excluded (weights renormalized). Only `GATE_FAILED` applies δ_C=0.5.

## Full-run grade mix (92 units)

| Grade | Count |
| --- | ---: |
| B | 10 |
| C | 28 |
| D | 21 |
| F | 33 |

Top: `trapster/telnet` 85.0 B · Bottom: `node-ftp-honeypot/ftp` 5.0 F · `cowrie/ssh` GATE_FAILED 18.98 F.

See [ALWAYS-GRADE-REGRADE.md](ALWAYS-GRADE-REGRADE.md).

## Why this is not “all F”

Prior always-grade still treated unmeasured Module C as **0 in the average** and applied δ_C=0.75 for INCOMPLETE — double-penalizing harness gaps. Measured-renorm grades the modules that actually ran.
