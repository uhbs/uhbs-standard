# UHBS 5.0.1 leaders — who tops the honest scoring model, and why

**Status:** Informative · rescored snapshot (2026-09-28) · scoring model `uhqs-v5.2-measured-renorm`
**Provenance:** `docs/conformance/latest/results-5.0.1/**/full/report.json` (artifacts) · ledger `.local/benchmark-refresh/results-5.0.1.sqlite3`
**Scope:** **124 of 135 full runs valid** (target reachable, Module A > 0) after the 2026-09-28 repair batch. The 11 remaining invalid runs are UDP services that stay silent to standard PDUs (honest `udp_no_reply`, documented in [rerun-runbook.yaml](rerun-runbook.yaml)). A grade is not a certification; UHBS is an evaluation framework, and product names appear here only as evaluation proof.

> **2026-09-28 math correction:** the harness previously scored *unmeasured*
> modules (skipped SAST, unrun telemetry sinks) as product zeros with full
> weight, contradicting the scoring spec. Fixed in the harness and artifacts
> rescored via `scripts/rescore_renorm.py` (pre-fix values preserved in each
> `report.json` under `uhqs_pre_renorm`). Two leaders gained a full grade band
> from the correction.

## The leaderboard (full runs, valid only)

| # | UHQS | Grade | Unit | A Protocol | B Realism | C Telemetry | E Scale | F Static |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 79.98 | C | shiva/smtp | 86.4 | 65.0 | unmeas | 100 | 71.5 |
| 2 | 79.52 | C | sentrypeer/sip | 100.0 | 25.0 | unmeas | 100 | 79.5 |
| 3 | 69.20 | D | conpot/s7comm | 92.0 | 65.0 | unmeas | 100 | 70.0 |
| 4 | 68.82 | D | portlurker/generic | 79.0 | 25.0 | unmeas | 100 | 70.8 |
| 5 | 63.51 | D | conpot/http | 100.0 | 65.0 | unmeas | 100 | 52.5 |
| 6 | 61.94 | D | conpot | 79.0 | 5.0 | unmeas | 100 | 70.0 |
| 7 | 58.59 | D | honeymcp/mcp | 46.5 | 94.3 | meas 0.0 | 100 | 65.5 |
| 8 | 58.48 | D | cowrie/telnet | 97.4 | 65.0 | unmeas | 55 | 70.0 |
| 9 | 57.15 | D | HoneyWire/http | 60.6 | 65.0 | unmeas | 100 | 70.0 |
| 10 | 53.25 | D | mailoney/smtp | 16.9 | 65.0 | unmeas | 100 | 75.6 |