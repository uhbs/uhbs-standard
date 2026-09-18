"""Shared check-list aggregation for UHBS modules (v5 outcome contract).

Only ``NOT_APPLICABLE`` checks leave the scoring denominator. ``NOT_TESTED``
and ``ERROR`` remain in the denominator at zero earned credit and block
module completeness when ``mandatory=True``.

Gates:

1. **Circuit breaker.** Any ``critical=True`` check that is not PASS
   (FAIL / ERROR / NOT_TESTED) hard-caps the aggregate to ``0.0``.
2. **Integrity gate.** Self-contradictory PASS/score pairs zero the list
   (see ``contract_validation.has_passed_score_disagreement``).
3. **Geometric mean** over checks that remain in the denominator.
4. **Completeness** is reported separately via ``module_completeness`` —
   callers must not publish a graded module score when incomplete.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from uhbs_core.contract_validation import has_passed_score_disagreement
from uhbs_core.models import CheckOutcome, CheckResult, module_completeness

# Floor used in place of a literal 0.0 before taking log() — keeps a single
# exact-zero score from making the *entire* geometric mean collapse to zero
# via a math domain error, while still contributing an extremely low value.
_LOG_FLOOR = 0.5


def _denominator_checks(checks: Sequence[CheckResult]) -> list[CheckResult]:
    return [c for c in checks if c.outcome is not CheckOutcome.NOT_APPLICABLE]


def score_checks(checks: Sequence[CheckResult]) -> float:
    """Aggregate a check list into one 0-100 score (v5 denominator rules)."""
    if not checks:
        return 0.0

    scored = _denominator_checks(checks)
    if not scored:
        # All NOT_APPLICABLE — no earned credit; caller should mark NA/incomplete.
        return 0.0

    # 1) Circuit breaker — critical non-PASS zeroes the whole list.
    if any(
        c.critical and c.outcome is not CheckOutcome.PASS
        for c in scored
    ):
        return 0.0

    # 2) Integrity gate — contradictory PASS/score zeroes the list.
    if any(
        c.outcome is CheckOutcome.PASS and has_passed_score_disagreement(c)
        for c in scored
    ):
        return 0.0
    if any(
        c.outcome is CheckOutcome.FAIL
        and has_passed_score_disagreement(c)
        for c in scored
    ):
        return 0.0

    # 3) Geometric mean over denominator members (NOT_TESTED/ERROR contribute ~0).
    if any(c.score > 0 for c in scored):
        vals = [max(float(c.score), _LOG_FLOOR) for c in scored]
        log_mean = sum(math.log(v) for v in vals) / len(vals)
        return round(min(100.0, math.exp(log_mean)), 4)

    # 4) Boolean-only fallback among denominator checks.
    return 100.0 * sum(1 for c in scored if c.outcome is CheckOutcome.PASS) / len(scored)


def score_checks_with_completeness(
    checks: Sequence[CheckResult],
) -> tuple[float, dict[str, Any]]:
    """Return (score, completeness dict). Score is diagnostic even if incomplete."""
    completeness = module_completeness(list(checks))
    return score_checks(checks), completeness


def earned_over_available(checks: Sequence[CheckResult]) -> float:
    """Linear earned/available among denominator checks (0–100).

    Prefer geometric ``score_checks`` for Modules A/B; use this for modules
    that historically summed point weights (C/D/E/F) so removing a check
    cannot silently shrink the ceiling.
    """
    scored = _denominator_checks(checks)
    if not scored:
        return 0.0
    # Each check's nominal max is inferred as max(score, 100) for PASS,
    # else treat weight as the check's declared score when PASS would have
    # earned it — plugins should set score to the weight on PASS and 0 otherwise.
    # For equal-weight checks, use count-based ratio of PASS.
    # When scores are point-weights, sum earned / sum of max weights among
    # measured outcomes. We approximate max weight as max(c.score, 1.0) for
    # PASS else look at a conventional weight from detail — simpler: equal weight.
    earned = sum(1.0 for c in scored if c.outcome is CheckOutcome.PASS)
    return round(100.0 * earned / len(scored), 2)


def point_weight_score(checks: Sequence[CheckResult]) -> float:
    """Sum of earned scores / sum of potential weights among denominator checks.

    Potential weight for each check is the score it would award on PASS. Plugins
    encode that as ``score`` when PASS, and should still record the potential
    via a positive score only on PASS; for FAIL/NOT_TESTED/ERROR the potential
    is recovered from ``metrics`` or assumed equal. Here we use equal potential
    per check when all non-PASS have score 0: fall back to earned_over_available.
    When some PASS scores exist, potential = max(pass scores) per check id group
    is unavailable; use sum(pass scores) / max(sum(all absolute weights), eps).

    Practical rule used by Modules C/D/E/F: each check declares its weight in
    ``score`` on PASS and 0 otherwise; potential total is supplied by the caller
    OR inferred as sum of scores on PASS plus a registered weight on failures
    stored in ``CheckResult`` — for v5 we store weight in score only on PASS and
    use equal-weight fallback when potentials are unknown.
    """
    scored = _denominator_checks(checks)
    if not scored:
        return 0.0
    earned = sum(float(c.score) for c in scored if c.outcome is CheckOutcome.PASS)
    # Potential: if any check has a positive score on PASS, estimate available
    # as earned + 0 for failures... that shrinks the ceiling. Instead require
    # plugins to put the weight on every outcome via a convention: use
    # max(score, 0) for PASS as weight, and for non-PASS look at a default
    # equal share.
    pass_weights = [float(c.score) for c in scored if c.outcome is CheckOutcome.PASS and c.score > 0]
    if not pass_weights:
        return earned_over_available(checks)
    # Assume remaining checks share the median PASS weight as potential.
    typical = sorted(pass_weights)[len(pass_weights) // 2]
    available = 0.0
    for c in scored:
        if c.outcome is CheckOutcome.PASS and c.score > 0:
            available += float(c.score)
        else:
            available += typical
    if available <= 0:
        return 0.0
    return round(min(100.0, 100.0 * earned / available), 2)
