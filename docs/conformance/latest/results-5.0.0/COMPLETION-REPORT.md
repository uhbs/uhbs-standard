# results-5.0.0 completion (always-grade regrade)

- **Date:** 2026-09-27
- **Branch:** `benchmark-refresh-results-v1`
- **scoring_model_id:** `uhqs-v5.1-always-grade`
- **Method:** Recomputed UHQS from existing module scores in each `report.json` (no Docker re-probe). Safety Gate is a δ_C factor, not an eligibility cliff.

## Summary (full runs)

| Metric | Count |
| --- | ---: |
| Full units with numeric UHQS | 92 |
| Still `uhqs=null` | 0 |
| Grade F | ~91 |
| Grade D | 1 (`beelzebub/http`) |
| `INCOMPLETE` verdict | majority |
| `GATE_FAILED` | `cowrie/ssh` (+ quick twin) |
| `GATE_PASSED` | few (e.g. `echidra`, `mockssh` where present) |
| Module C = 0 | essentially all full units |

See [ALWAYS-GRADE-REGRADE.md](ALWAYS-GRADE-REGRADE.md) for the per-unit table and CTI notes.

## CTI analyst findings (honest)

1. **Mass Module C=0** — almost every unit publishes C=0 / incomplete telemetry. Grades therefore mostly sit in **F** after δ_C=0.75. That is consistent with the lab harness gap, **not** a claim that every honeypot is equally useless as a sensor. Do not cite these as CTI-collection readiness scores until Module C sinks work.
2. **INCOMPLETE is mostly harness** — C/D not measured → status INCOMPLETE → δ_C 0.75. Product protocol/behavior scores (A/B) can still look fine (e.g. HoneyWire A=100) while the composite is F.
3. **Cowrie SSH `GATE_FAILED`** — OOB leak measured; UHQS=18.98 / F with δ_C=0.5. Logical for containment; still has C=0 so telemetry story is weak.
4. **`echidra` `GATE_PASSED` with D=0** — verdict vs containment score are inconsistent; treat as lab labeling debt, not a clean pass narrative.
5. **Weak A + stronger B** (Cowrie SSH, some OpenCanary UDP) — often probe/coverage quirks, not “behavior without a protocol.”
6. **Krawl / pyrdp near-zero** — A≈0 and F≈0; look like failed/near-dead lab surfaces, not competitive decoys.

## What was not done

- No full Docker re-probe of all 92 units (would not fix C=0 without harness work).
- Lab Module C sinks / egress deny profiles remain follow-on work.
