"""Harness wiring for measured-module renormalization (2026-09-28 fix).

The math in uhqs_math.compute_uhqs always excluded unmeasured modules, but
run_benchmark never passed measured_modules — so complete=False modules
(skipped SAST, unrun telemetry sinks) were scored as product zeros with full
weight. These tests pin the harness-side derivation so that cannot regress.
"""

from __future__ import annotations

from uhbs_core.models import ModuleResult
from uhbs_core.run_benchmark import MIN_MEASURED_COMPOSITE, composite_measured_flags


def _mod(letter: str, status: str, complete: bool) -> ModuleResult:
    return ModuleResult(
        module=letter, dimension="x", score=0.0, status=status, complete=complete
    )


def test_guard_constant_is_four_of_five() -> None:
    assert MIN_MEASURED_COMPOSITE == 4


def test_unmeasured_module_is_flagged_excluded() -> None:
    flags = composite_measured_flags([
        _mod("A", "PASSED", True),
        _mod("B", "PASSED", True),
        _mod("C", "INCOMPLETE", False),  # harness gap: sink never ran
        _mod("E", "PASSED", True),
        _mod("F", "PASSED", True),
    ])
    assert flags == {"A": True, "B": True, "C": False, "E": True, "F": True}


def test_measured_zero_stays_counted() -> None:
    # FAILED with complete=True is a *measured* zero (format mismatch), not a gap.
    flags = composite_measured_flags([_mod("C", "FAILED", True)])
    assert flags["C"] is True


def test_skipped_sast_is_a_gap() -> None:
    flags = composite_measured_flags([_mod("F", "INCOMPLETE", False)])
    assert flags["F"] is False


def test_quick_profile_trips_comparability_guard() -> None:
    # quick runs: C unmeasured (no sink) + F unmeasured (skip-sast) -> 3 of 5.
    flags = composite_measured_flags([
        _mod("A", "PASSED", True),
        _mod("B", "PASSED", True),
        _mod("C", "INCOMPLETE", False),
        _mod("E", "PASSED", True),
        _mod("F", "INCOMPLETE", False),
    ])
    assert sum(flags.values()) < MIN_MEASURED_COMPOSITE


def test_full_profile_with_one_gap_does_not_trip_guard() -> None:
    # The shiva-shape case: only C unmeasured -> 4 of 5 -> comparable, but C
    # must be excluded from the composite (not counted as a product zero).
    flags = composite_measured_flags([
        _mod("A", "PASSED", True),
        _mod("B", "PASSED", True),
        _mod("C", "INCOMPLETE", False),
        _mod("E", "PASSED", True),
        _mod("F", "PASSED", True),
    ])
    assert sum(flags.values()) >= MIN_MEASURED_COMPOSITE
    assert flags["C"] is False


def test_module_d_is_ignored() -> None:
    flags = composite_measured_flags([
        _mod("A", "PASSED", True),
        _mod("D", "FAILED", False),
    ])
    assert "D" not in flags
