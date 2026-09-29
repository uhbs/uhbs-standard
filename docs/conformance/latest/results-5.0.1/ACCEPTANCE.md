# Unit acceptance — results-5.0.1 (Gate A+)

Machine-checkable checklist for “unit finished.” Agents and operators use
[`scripts/validate_unit.py`](https://github.com/uhbs/uhbs-standard/blob/main/scripts/validate_unit.py) — exit **0** =
`ACCEPT`, non-zero = `REJECT` with missing paths printed.

Schema: [`schemas/results-unit-acceptance.schema.json`](https://github.com/uhbs/uhbs-standard/blob/main/schemas/results-unit-acceptance.schema.json)

## Product hub (`results-5.0.1/<product>/`)

| Path | Rule |
| --- | --- |
| `index.md` | exists, non-empty |
| `TUTORIAL.md` | exists, non-empty (how users reproduce) |
| `METHODOLOGY.md` | exists, non-empty (dual-vantage + Spot notes) |

## Unit root (`…/<product>/` or `…/<product>/<protocol>/`)

| Path | Rule |
| --- | --- |
| `EXECUTION-STEPS.md` | exists, non-empty |
| `Dockerfile` | exists, non-empty (build recipe used for the graded target) |
| `Dockerfile.pin` | exists, non-empty (`FROM sha256:…` exact image pin) |
| `quick/` | directory present |
| `full/` | directory present |

## Each of `quick/` and `full/`

| Path | Rule |
| --- | --- |
| `README.md` | non-empty |
| `SCORECARD.txt` | non-empty |
| `REPORT.txt` | non-empty |
| `report.json` | valid JSON; UHQS + modules A–F |
| `MANIFEST.json` | valid JSON; sha256 entries match on-disk files |
| `run-meta.json` | valid JSON; includes `uhbs_version`; optional `vantage` / `vantage_onbox` / `vantage_remote` / `raw_s3_uri` |
| `uhbs-run.log` | non-empty |

Optional when grader emits: `evidence-pack.json`, `static/`

## `full/` only

| Path / check | Rule |
| --- | --- |
| `proof/full-run.cast` | exists, size > 0 |
| `static/` | directory present |
| SQLite `run_executions` (full) | success status; `cast_path` set |
| Module C | when `telemetry_required`, Module C measured (not empty sink) |

## Tracker / ledger (wave-level)

| Check | Rule |
| --- | --- |
| Unit row in `results-5.0.1.sqlite3` | `upstream_commit`, `fixture_path`, latest paths |
| `benchmark-manifest.yaml` | entry matches unit |
| After batches | `RUN-LEDGER.md` + `ALWAYS-GRADE-REGRADE.md` regenerated |

Status vocabulary: **ACCEPT** / **REJECT**.
