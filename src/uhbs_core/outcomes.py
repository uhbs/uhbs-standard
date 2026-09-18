"""UHBS v5 check outcomes and assessment-status vocabulary.

Normative contract from RFC 0003 / UHQS v5:

- ``PASS`` / ``FAIL`` — executed successfully; enter the scoring denominator.
- ``NOT_APPLICABLE`` — outside declared capabilities; leaves the denominator
  (requires machine-valid applicability rationale).
- ``NOT_TESTED`` / ``ERROR`` — applicable but unmeasured; never earn credit and
  make a mandatory assessment ``INCOMPLETE`` (Ungraded).
"""

from __future__ import annotations

from enum import StrEnum

from uhbs_core.uhqs_math import (
    AssessmentStatus,
    CriticalControlVerdict,
)

# Re-export for callers that import assessment vocabulary from outcomes.
__all__ = [
    "APPLICABLE_OUTCOMES",
    "AssuranceLevel",
    "AssessmentStatus",
    "CheckOutcome",
    "ContainmentVerdict",
    "CriticalControlVerdict",
    "SCORED_OUTCOMES",
    "ZERO_CREDIT_OUTCOMES",
    "outcome_from_passed",
    "parse_outcome",
]


class CheckOutcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_TESTED = "NOT_TESTED"
    ERROR = "ERROR"


SCORED_OUTCOMES = frozenset({CheckOutcome.PASS, CheckOutcome.FAIL})
APPLICABLE_OUTCOMES = frozenset(
    {CheckOutcome.PASS, CheckOutcome.FAIL, CheckOutcome.NOT_TESTED, CheckOutcome.ERROR}
)
ZERO_CREDIT_OUTCOMES = frozenset(
    {CheckOutcome.NOT_APPLICABLE, CheckOutcome.NOT_TESTED, CheckOutcome.ERROR, CheckOutcome.FAIL}
)

ContainmentVerdict = CriticalControlVerdict


class AssuranceLevel(StrEnum):
    SELF_ASSESSED = "SELF_ASSESSED"
    REPRODUCIBLE_LAB = "REPRODUCIBLE_LAB"
    INDEPENDENTLY_REPRODUCED = "INDEPENDENTLY_REPRODUCED"


def parse_outcome(value: object) -> CheckOutcome | None:
    if isinstance(value, CheckOutcome):
        return value
    if isinstance(value, str):
        key = value.strip().upper().replace("-", "_").replace(" ", "_")
        try:
            return CheckOutcome[key]
        except KeyError:
            return None
    return None


def outcome_from_passed(passed: bool) -> CheckOutcome:
    return CheckOutcome.PASS if passed else CheckOutcome.FAIL
