"""Contract validation for UHBS check / module results (v5 outcome contract).

Hard rules used by scoring:

- ``has_passed_score_disagreement`` — integrity gate for score_checks
- ``NOT_TESTED`` / ``ERROR`` / ``NOT_APPLICABLE`` must have ``score == 0``
- ``NOT_APPLICABLE`` requires ``applicability_rationale``
- Mandatory applicable ``NOT_TESTED`` / ``ERROR`` → module incomplete
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from uhbs_core.models import CheckOutcome

# Sane bounds for the CheckResult.score contract (see uhbs_core.models).
SCORE_MIN = 0.0
SCORE_MAX = 100.0

DEFAULT_PASS_SCORE_FLOOR = 15.0
DEFAULT_FAIL_SCORE_CEILING = 85.0

_VALID_TEAMS = {"blue", "red", "white"}
_VALID_OUTCOMES = {o.value for o in CheckOutcome}


def has_passed_score_disagreement(
    result: Any,
    *,
    pass_score_floor: float = DEFAULT_PASS_SCORE_FLOOR,
    fail_score_ceiling: float = DEFAULT_FAIL_SCORE_CEILING,
) -> bool:
    """True iff boolean ``passed`` / outcome PASS and numeric ``score`` disagree."""
    outcome = _get(result, "outcome", _MISSING)
    passed = _get(result, "passed", _MISSING)

    is_pass = False
    is_fail = False
    if outcome is not _MISSING and outcome is not None:
        val = outcome.value if isinstance(outcome, CheckOutcome) else str(outcome)
        is_pass = val == CheckOutcome.PASS.value
        is_fail = val == CheckOutcome.FAIL.value
    elif passed is not _MISSING and isinstance(passed, bool):
        is_pass = passed
        is_fail = not passed
    else:
        return False

    score = _get(result, "score", _MISSING)
    if score is _MISSING or not isinstance(score, (int, float)) or isinstance(score, bool):
        return False
    score = float(score)
    if not (SCORE_MIN <= score <= SCORE_MAX):
        return False
    if is_pass:
        return score < pass_score_floor
    if is_fail:
        return score > fail_score_ceiling
    return False


def validate_check_result(
    result: Any,
    *,
    pass_score_floor: float = DEFAULT_PASS_SCORE_FLOOR,
    fail_score_ceiling: float = DEFAULT_FAIL_SCORE_CEILING,
) -> list[str]:
    """Return human-readable contract violations for one check-like object."""
    violations: list[str] = []

    check_id = _get(result, "id")
    if not isinstance(check_id, str) or not check_id.strip():
        violations.append("missing required field: id (must be a non-empty string)")

    team = _get(result, "team")
    if not isinstance(team, str) or team.lower() not in _VALID_TEAMS:
        allowed = sorted(_VALID_TEAMS)
        violations.append(
            f"invalid/missing required field: team={team!r} (expected one of {allowed})"
        )

    outcome_raw = _get(result, "outcome", _MISSING)
    outcome_val: str | None = None
    if outcome_raw is _MISSING or outcome_raw is None:
        # Legacy: require passed bool
        passed = _get(result, "passed", _MISSING)
        if passed is _MISSING or not isinstance(passed, bool):
            violations.append(
                "missing required field: outcome (PASS|FAIL|NOT_APPLICABLE|NOT_TESTED|ERROR) "
                "or legacy passed bool"
            )
        else:
            outcome_val = CheckOutcome.PASS.value if passed else CheckOutcome.FAIL.value
    else:
        outcome_val = (
            outcome_raw.value if isinstance(outcome_raw, CheckOutcome) else str(outcome_raw)
        )
        if outcome_val not in _VALID_OUTCOMES:
            violations.append(
                f"invalid outcome={outcome_val!r} (expected one of {sorted(_VALID_OUTCOMES)})"
            )

    score = _get(result, "score", _MISSING)
    if score is _MISSING or not isinstance(score, (int, float)) or isinstance(score, bool):
        violations.append("missing required field: score (must be numeric)")
        score = None
    elif not (SCORE_MIN <= float(score) <= SCORE_MAX):
        violations.append(
            f"score={score!r} out of range [{SCORE_MIN}, {SCORE_MAX}] for check id={check_id!r}"
        )

    critical = _get(result, "critical", False)
    if not isinstance(critical, bool):
        violations.append(f"invalid field: critical={critical!r} (must be a bool)")

    if outcome_val in {
        CheckOutcome.NOT_APPLICABLE.value,
        CheckOutcome.NOT_TESTED.value,
        CheckOutcome.ERROR.value,
    } and score is not None and float(score) > 0:
        violations.append(
            f"outcome={outcome_val} must have score==0 (got {score!r}) for check id={check_id!r}"
        )

    if outcome_val == CheckOutcome.NOT_APPLICABLE.value:
        rationale = _get(result, "applicability_rationale", None)
        if not isinstance(rationale, str) or not rationale.strip():
            violations.append(
                f"NOT_APPLICABLE requires applicability_rationale for check id={check_id!r}"
            )

    if (
        outcome_val in {CheckOutcome.PASS.value, CheckOutcome.FAIL.value}
        and score is not None
        and SCORE_MIN <= float(score) <= SCORE_MAX
        and has_passed_score_disagreement(
            result, pass_score_floor=pass_score_floor, fail_score_ceiling=fail_score_ceiling
        )
    ):
        if outcome_val == CheckOutcome.PASS.value:
            violations.append(
                f"outcome=PASS but score={score!r} is below the sane pass floor "
                f"({pass_score_floor}) for check id={check_id!r}"
            )
        else:
            violations.append(
                f"outcome=FAIL but score={score!r} is above the sane fail ceiling "
                f"({fail_score_ceiling}) for check id={check_id!r}"
            )

    return violations


def validate_module_result(
    module: Any,
    *,
    pass_score_floor: float = DEFAULT_PASS_SCORE_FLOOR,
    fail_score_ceiling: float = DEFAULT_FAIL_SCORE_CEILING,
) -> list[str]:
    """Return violations for a ``ModuleResult``-like object and its checks."""
    violations: list[str] = []

    module_score = _get(module, "score", _MISSING)
    if module_score is _MISSING or not isinstance(module_score, (int, float)) or isinstance(
        module_score, bool
    ):
        violations.append("missing required field: score (must be numeric) on ModuleResult")
    elif not (SCORE_MIN <= float(module_score) <= SCORE_MAX):
        violations.append(f"module score={module_score!r} out of range [{SCORE_MIN}, {SCORE_MAX}]")

    checks = _get(module, "checks", []) or []
    for idx, check in enumerate(checks):
        check_id = _get(check, "id", f"#{idx}")
        for v in validate_check_result(
            check, pass_score_floor=pass_score_floor, fail_score_ceiling=fail_score_ceiling
        ):
            violations.append(f"[check {check_id}] {v}")

    return violations


def module_is_complete(module: Any) -> bool:
    """True iff no mandatory applicable check is NOT_TESTED or ERROR."""
    checks = _get(module, "checks", []) or []
    for check in checks:
        mandatory = _get(check, "mandatory", True)
        if mandatory is False:
            continue
        outcome = _get(check, "outcome", None)
        if outcome is None:
            continue
        val = outcome.value if isinstance(outcome, CheckOutcome) else str(outcome)
        if val in {CheckOutcome.NOT_TESTED.value, CheckOutcome.ERROR.value}:
            return False
    complete = _get(module, "complete", True)
    return bool(complete)


class _Missing:
    def __repr__(self) -> str:  # pragma: no cover — debugging aid only
        return "<missing>"


_MISSING = _Missing()


def _get(obj: Any, name: str, default: Any = _MISSING) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


@runtime_checkable
class UHBSProtocolPlugin(Protocol):
    """Structural contract for a third-party UHBS protocol plugin."""

    name: str

    def probe_fsm(self, host: str, port: int, target: Any, tps: Any) -> list[Any]:
        """A1 — out-of-order / invalid verbs vs mandated status codes."""
        ...

    def probe_negotiation(self, host: str, port: int, target: Any, tps: Any) -> list[Any]:
        """A2 — capability / banner / cipher negotiation parity."""
        ...

    def probe_state(self, host: str, port: int, target: Any, tps: Any) -> list[Any]:
        """B — state-machine / stateful realism probe."""
        ...
