# EchidraOSS — published UHBS lab reports

**Proof label:** [Qyleron/EchidraOSS](https://github.com/Qyleron/EchidraOSS)  
**Class / protocol:** `Low-Interaction` · SSH · container port `2222`  
**UHBS:** package **5.0.0** · lab harness image **4.0.0** (SCORECARD banner) · evaluation proof only (not an endorsement)

Echidra is a multi-protocol deceptive honeypot (SSH / HTTP / FTP / Telnet) with
MITRE ATT&CK-tagged classification and a dashboard. This published grade evaluates
the **SSH** listener (asyncssh) with Low-Interaction class weights. Auth for the
lab used `root` / `admin` (Echidra accepts any credentials after a short delay).

## Results at a glance

| Mode | UHQS | Grade | δ_C | Safety Gate | Folder |
| --- | --- | --- | --- | --- | --- |
| **Quick** | **57.33** | D | 1.0 | cleared (C=100) | [`quick/`](quick/) |
| **Full** | **43.45** | F | 1.0 | cleared (C=100) | [`full/`](full/) |

Sanitized fixture (full): [`../../fixtures/echidra-low-interaction.scorecard.json`](../../fixtures/echidra-low-interaction.scorecard.json)

### Why full can score *lower* than quick

Quick leaves `telemetry_dir` unset, so Module C looks optimistic (100) while
skipping SAST. Full mounts real `sessions.jsonl` (C=55, no STIX/OTel/ECS) and
runs bandit/semgrep (F capped at 70). Protocol fidelity stays weak (A≈21–23).

**Takeaway:** cite **full/** for claim-grade evaluation.

## Contents

| Document | Purpose |
| --- | --- |
| [TUTORIAL.md](TUTORIAL.md) | Step-by-step: Docker Compose start, quick + full grades |
| [METHODOLOGY.md](METHODOLOGY.md) | Digests, topology, limitations, verification |
| [`quick/SCORECARD.txt`](quick/SCORECARD.txt) | Human scorecard (quick) |
| [`full/SCORECARD.txt`](full/SCORECARD.txt) | Human scorecard (full) |
| [`full/static/semgrep-report.json`](full/static/semgrep-report.json) | Module F Semgrep |
| [`full/static/bandit-report.json`](full/static/bandit-report.json) | Module F Bandit |

## Module snapshot (full)

| Module | Score | Highlight |
| --- | --- | --- |
| A Protocol | 21.5 | SSH RFC4253; null-in-ID still accepted; **n=1000** timing |
| B Behavior | 25.0 | Cross-session marker missing |
| C Telemetry | 55.0 | `sessions.jsonl` present — no STIX/OTel/ECS (schema-capped) |
| D Containment | 100.0 | Shell egress probes blocked; gate cleared |
| E Scale | 55.0 | SSH session P95 ~1.8 s under concurrency 10 |
| F Static | 70.0 | SAST gate capped (hardcoded banner + findings) |

## Start here

1. [METHODOLOGY.md](METHODOLOGY.md)  
2. [TUTORIAL.md](TUTORIAL.md)  
3. [`full/SCORECARD.txt`](full/SCORECARD.txt) / [`full/report.json`](full/report.json)  

Back to the [reports index](../index.md).
