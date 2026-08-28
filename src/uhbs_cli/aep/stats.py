"""Statistical helpers for AEP metrics (offline)."""

from __future__ import annotations

import math
import random
import statistics
from typing import Any


def _percentile(sorted_vals: list[float], p: float) -> float | None:
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def bootstrap_ci(
    values: list[float],
    *,
    statistic: Any,
    n_samples: int,
    confidence: float,
    seed: int,
) -> tuple[float | None, float | None]:
    if not values or n_samples <= 0:
        return None, None
    rng = random.Random(seed)
    stats: list[float] = []
    n = len(values)
    for _ in range(n_samples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        try:
            stats.append(float(statistic(sample)))
        except (statistics.StatisticsError, ZeroDivisionError, ValueError):
            continue
    if not stats:
        return None, None
    stats.sort()
    alpha = 1.0 - confidence
    return _percentile(stats, alpha / 2), _percentile(stats, 1 - alpha / 2)


def kaplan_meier_median(durations: list[float], censored: list[bool]) -> float | None:
    """Estimate median duration with right-censoring via Kaplan–Meier."""
    if not durations:
        return None
    events = sorted(zip(durations, censored, strict=True), key=lambda x: x[0])
    n = len(events)
    survival = 1.0
    at_risk = n
    last_t = 0.0
    for t, is_censored in events:
        if at_risk <= 0:
            break
        if not is_censored:
            survival *= (at_risk - 1) / at_risk
            if survival <= 0.5:
                return float(t)
        at_risk -= 1
        last_t = float(t)
    # Median not reached — return None (inconclusive) rather than optimistic mean
    if survival > 0.5:
        return None
    return last_t

