# UHBS v5 synthetic golden scorecards

These fixtures exercise the **UHQS v5** critical-control gate under the normative
always-grade scoring model (`scoring_model_id=uhqs-v5.2-measured-renorm`): every
assessment publishes a UHQS composite and letter grade; the Safety Gate acts as
the δ_C containment factor rather than suppressing the composite.

| File | Meaning |
| --- | --- |
| `gate-passed-graded.scorecard.json` | GATE_PASSED → graded UHQS (δ_C = 1.0; 90.0 / A) |
| `gate-failed-ungraded.scorecard.json` | GATE_FAILED → still graded; δ_C = 0.5 multiplies the composite (50.0 / D) |
| `incomplete-ungraded.scorecard.json` | INCOMPLETE → measured modules renormalized and graded (76.0 / C) |

Historical note: the two `-ungraded` filenames date from the earlier fail-closed
diagnostic model (`uhqs-v5.0-critical-gate-diagnostic`), which left `uhqs`/`grade`
null on gate failure or incomplete assessments. They are kept for continuity;
under the current model these scorecards always carry a grade.

Product lab fixtures remain in the parent `fixtures/` directory.
