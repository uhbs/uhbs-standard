# UHBS v5 synthetic golden scorecards

These fixtures exercise the **UHQS v5** fail-closed critical-control gate
(`scoring_model_id=uhqs-v5.0-critical-gate-diagnostic`):

| File | Meaning |
| --- | --- |
| `gate-passed-graded.scorecard.json` | GATE_PASSED → graded UHQS |
| `gate-failed-ungraded.scorecard.json` | GATE_FAILED → `uhqs`/`grade` null |
| `incomplete-ungraded.scorecard.json` | INCOMPLETE → `uhqs`/`grade` null |

Product lab fixtures remain in the parent `fixtures/` directory.
