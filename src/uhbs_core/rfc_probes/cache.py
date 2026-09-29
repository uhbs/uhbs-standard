"""Short-lived cache so fsm/nego/state hooks share one RFC suite run."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import replace

from uhbs_core.models import CheckResult

from .types import RFCSuiteResult

_lock = threading.Lock()
_store: dict[tuple, tuple[float, RFCSuiteResult]] = {}
_DEFAULT_TTL_SEC = 60.0


def clear_suite_cache() -> None:
    """Drop all cached suites (tests / new grade runs)."""
    with _lock:
        _store.clear()


def _clone_suite(suite: RFCSuiteResult) -> RFCSuiteResult:
    """Return a defensive copy so callers can annotate checks safely."""
    checks: list[CheckResult] = []
    for c in suite.checks:
        checks.append(
            replace(
                c,
                evidence=list(c.evidence or []),
                evidence_refs=list(c.evidence_refs or []),
                evidence_hashes=list(c.evidence_hashes or []),
            )
        )
    return RFCSuiteResult(
        protocol=suite.protocol,
        rfc=suite.rfc,
        checks=checks,
        skipped=suite.skipped,
        skip_reason=suite.skip_reason,
    )


def cached_suite(
    key: tuple,
    factory: Callable[[], RFCSuiteResult],
    *,
    ttl_sec: float = _DEFAULT_TTL_SEC,
) -> RFCSuiteResult:
    """Return a cloned suite, computing ``factory`` at most once per TTL window."""
    now = time.monotonic()
    with _lock:
        hit = _store.get(key)
        if hit is not None and (now - hit[0]) < ttl_sec:
            return _clone_suite(hit[1])
    result = factory()
    with _lock:
        _store[key] = (now, result)
    return _clone_suite(result)
