# UHQS v5 sensitivity notes (fixture corpus)

**Status:** Informative  
**Related:** [RFC 0003](../0003-scoring-assurance.md)  
**scoring_model_id (chosen):** `uhqs-v5.0-critical-gate-diagnostic`  
**Date:** 2026-09-18

## Scope

Sensitivity over published v5.0.0 conformance fixtures under `docs/conformance/fixtures/` (historical UHQS 4.x math). This is **not** a live known-good/known-bad calibration.

## v4 δ_C cliff

Under UHQS 4.x:

\[
\delta_C =
\begin{cases}
1.0 & C \ge 95 \\
(C/100)^{2} & C < 95
\end{cases}
\]

| Module D (\(C\)) | \(\delta_C\) | Effect |
| ---: | ---: | --- |
| 100 / 95 | 1.00 | Full composite |
| 94 | ≈ 0.88 | Immediate cliff below the floor |
| 90 | 0.81 | Graded UHQS still emitted (19% cut) |
| 75 | 0.56 | Graded UHQS still emitted |
| 0 | 0.00 | UHQS collapses to 0 |

The discontinuity at 95, plus the historical `max(score, 95)` floor, incentivizes tuning Module D to clear the threshold rather than demonstrating critical controls with evidence.

## Fixture Module D distribution (n=39)

| Module D band | Count (approx.) | v4 outcome | Binary-gate implication* |
| --- | ---: | --- | --- |
| \(C = 100\) | 7 | \(\delta_C=1\), graded | Eligible only if critical controls actually PASS |
| \(C = 90\) | 26 | \(\delta_C=0.81\), **still graded** | Would not clear a critical-control gate if 90 reflects failed/partial containment |
| \(C = 75\) | 2 | \(\delta_C=0.56\), graded | `GATE_FAILED` → `uhqs=null` |
| \(C \le 55\) | 3 | Heavily penalized / fail | `GATE_FAILED` → `uhqs=null` |
| Synthetic fail (\(C=0\)) | 1 | UHQS null / fail | `GATE_FAILED` |

\*Binary gate uses **critical-control evidence**, not the legacy numeric 95 threshold. Numeric D scores above are proxies for sensitivity only.

## Comparison: cliff vs binary gate

| Property | v4 continuous cliff | Binary critical-control gate |
| --- | --- | --- |
| Failed containment still yields a letter grade | Yes (reduced UHQS) | No (`uhqs=null`) |
| Incomplete / unmeasured mandatory checks | Can still grade | `INCOMPLETE` / Ungraded |
| Explainability | Exponent arbitrary | Pass/fail eligibility |
| Gaming surface | Floor + cliff at 95 | Critical controls + evidence |

**Conclusion:** choose **`uhqs-v5.0-critical-gate-diagnostic`**. Continuous \((C/95)^k\) was considered and **rejected** as arbitrary without a full live calibration corpus.

## Open live-corpus items

Ship-time live known-good/known-bad calibration remains **partial**. Before treating thresholds as production-facing:

1. Representative live reruns across ≥3 profile classes (include a non-shell / OT or Web-API target).
2. Intentional weak-decoy and egress-leak known-bad cases with evidence packs.
3. Telemetry fault injection (zero telemetry, sink poison, ATT&CK ID forgery) as known-bad Module C vectors.
4. Independent technical review of RFC 0003 responses (single-maintainer project — not committee approval).
5. Publish v5 synthetic fixtures under `docs/conformance/fixtures/v5/`; keep v4 URLs as historical.
