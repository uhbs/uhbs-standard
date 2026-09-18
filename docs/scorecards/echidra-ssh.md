# Scorecard: Low-Interaction / SSH decoy (EchidraOSS proof)

**Status:** Informative · evaluation proof (not an endorsement)  
**Proof label:** [Qyleron/EchidraOSS](https://github.com/Qyleron/EchidraOSS) · report hub: [`../conformance/reports/echidra/`](../conformance/reports/echidra/index.md)

| Field | Value |
| --- | --- |
| Target | Low-Interaction SSH decoy |
| Class | Low-Interaction |
| Protocol | SSH `:2222` |
| Evaluated | 2026-09-15 (full Docker lab) |
| Spec | UHBS 5.0.0 (lab harness image 4.0.0) |

## Module Results

| Evaluation Module | Score (0–100) | Weight | Status |
| --- | ---: | ---: | --- |
| Module A: Protocol Fidelity | 21.5/100 | 0.30 | PARTIAL |
| Module B: Behavioral Realism | 25.0/100 | 0.15 | PARTIAL |
| Module C: Telemetry Quality | 55.0/100 | 0.25 | PARTIAL |
| Module D: Safety & Containment (\(C\)) | 100.0/100 | GATE | GATE PASSED |
| Module E: Scalability & Latency | 55.0/100 | 0.10 | PARTIAL (P95: ~1814 ms) |
| Module F: Static Code Audit | 70.0/100 | 0.20 | PASSED (SAST gate capped) |

## Safety Gate & Composite

| Metric | Value |
| --- | --- |
| Safety Gate Multiplier \(\delta_C\) | 1.0 (\(C = 100 \ge 95\)) |
| **Final Composite Score (UHQS 4.0)** | **43.45 / 100** |
| Grade | **F (Fail)** |
| Production baseline (UHQS &gt; 80 + gate) | **NOT MET** (gate cleared; UHQS below 80) |

## Artifacts

- Fixture: [`../conformance/fixtures/echidra-low-interaction.scorecard.json`](../conformance/fixtures/echidra-low-interaction.scorecard.json)
- Full scorecard: [`../conformance/reports/echidra/full/SCORECARD.txt`](../conformance/reports/echidra/full/SCORECARD.txt)
- Quick scorecard: [`../conformance/reports/echidra/quick/SCORECARD.txt`](../conformance/reports/echidra/quick/SCORECARD.txt) (UHQS **57.33** / D)
- Tutorial: [`../conformance/reports/echidra/TUTORIAL.md`](../conformance/reports/echidra/TUTORIAL.md)
- Original project: [github.com/Qyleron/EchidraOSS](https://github.com/Qyleron/EchidraOSS)

```bash
uhbs validate-scorecard docs/conformance/fixtures/echidra-low-interaction.scorecard.json --strict
```
