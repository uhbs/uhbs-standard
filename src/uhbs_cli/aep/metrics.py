"""AEP informative metrics: DTDR, EER, VoD, FSV."""

from __future__ import annotations

import random
import statistics
from typing import Any

from .constants import FSV_LAYERS
from .errors import AepError
from .stats import _percentile, bootstrap_ci, kaplan_meier_median


def _arm_durations(
    trials: list[dict[str, Any]], arm: str
) -> tuple[list[float], list[bool]]:
    durs: list[float] = []
    cens: list[bool] = []
    for t in trials:
        if t.get("arm") != arm:
            continue
        durs.append(float(t.get("session_duration_seconds", 0)))
        cens.append(bool(t.get("censored", False)))
    return durs, cens


def compute_dtdr(
    trials: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    confidence: float,
    seed: int,
) -> dict[str, Any]:
    decoy_d, decoy_c = _arm_durations(trials, "decoy")
    ref_d, ref_c = _arm_durations(trials, "reference")
    details: dict[str, Any] = {
        "decoy_n": len(decoy_d),
        "reference_n": len(ref_d),
        "decoy_censoring_rate": (sum(decoy_c) / len(decoy_c)) if decoy_c else 0.0,
        "reference_censoring_rate": (sum(ref_c) / len(ref_c)) if ref_c else 0.0,
        "estimator": "kaplan_meier_median_ratio",
    }
    if len(decoy_d) < 2 or len(ref_d) < 2:
        return {
            "value": None,
            "unit": "ratio",
            "n": len(decoy_d) + len(ref_d),
            "interval": {"low": None, "high": None, "confidence": confidence},
            "status": "inconclusive",
            "details": details,
            "notes": "Need at least 2 trials per arm for DTDR",
        }

    any_censored = any(decoy_c) or any(ref_c)
    if any_censored:
        decoy_med = kaplan_meier_median(decoy_d, decoy_c)
        ref_med = kaplan_meier_median(ref_d, ref_c)
        details["decoy_median_seconds"] = decoy_med
        details["reference_median_seconds"] = ref_med
        if decoy_med is None or ref_med is None or ref_med == 0:
            return {
                "value": None,
                "unit": "ratio",
                "n": len(decoy_d) + len(ref_d),
                "interval": {"low": None, "high": None, "confidence": confidence},
                "status": "inconclusive",
                "details": details,
                "notes": "Censoring-aware median undefined (survival never crossed 0.5)",
            }
        value = decoy_med / ref_med
    else:
        decoy_med = statistics.median(decoy_d)
        ref_med = statistics.median(ref_d)
        details["decoy_median_seconds"] = decoy_med
        details["reference_median_seconds"] = ref_med
        details["estimator"] = "median_ratio"
        if ref_med == 0:
            return {
                "value": None,
                "unit": "ratio",
                "n": len(decoy_d) + len(ref_d),
                "interval": {"low": None, "high": None, "confidence": confidence},
                "status": "inconclusive",
                "details": details,
                "notes": "Reference median duration is zero",
            }
        value = decoy_med / ref_med

    # Bootstrap on uncensored medians when no censoring; otherwise skip parametric CI
    low = high = None
    if not any_censored:
        rng = random.Random(seed)
        ratios: list[float] = []
        for _ in range(bootstrap_samples):
            d_s = [decoy_d[rng.randrange(len(decoy_d))] for _ in range(len(decoy_d))]
            r_s = [ref_d[rng.randrange(len(ref_d))] for _ in range(len(ref_d))]
            rm = statistics.median(r_s)
            if rm == 0:
                continue
            ratios.append(statistics.median(d_s) / rm)
        ratios.sort()
        if ratios:
            alpha = 1.0 - confidence
            low = _percentile(ratios, alpha / 2)
            high = _percentile(ratios, 1 - alpha / 2)
    else:
        details["interval_note"] = (
            "Bootstrap CI omitted when right-censoring is present; "
            "report KM medians and sample sizes."
        )

    return {
        "value": float(value),
        "unit": "ratio",
        "n": len(decoy_d) + len(ref_d),
        "interval": {"low": low, "high": high, "confidence": confidence},
        "status": "valid",
        "details": details,
        "notes": "DTDR > 1 means longer dwell on decoy than matched reference",
    }


def _unique_capability_count(trial: dict[str, Any]) -> int:
    bags = (
        trial.get("unique_tools") or [],
        trial.get("unique_credentials") or [],
        trial.get("unique_payload_families") or [],
        trial.get("attack_technique_ids") or [],
    )
    return len({str(x) for bag in bags for x in bag})


def compute_eer(
    trials: list[dict[str, Any]],
    experiment: dict[str, Any],
    *,
    bootstrap_samples: int,
    confidence: float,
    seed: int,
) -> dict[str, Any]:
    budget = int((experiment.get("budget") or {}).get("max_unique_capabilities", 1))
    decoy_trials = [t for t in trials if t.get("arm") == "decoy"]
    if len(decoy_trials) < 2:
        return {
            "value": None,
            "unit": "fraction_of_budget",
            "n": len(decoy_trials),
            "interval": {"low": None, "high": None, "confidence": confidence},
            "status": "inconclusive",
            "details": {"budget_max_unique_capabilities": budget},
            "notes": "Need at least 2 decoy trials for EER",
        }
    per_session = [_unique_capability_count(t) for t in decoy_trials]
    fractions = [c / budget for c in per_session]
    mean_frac = statistics.fmean(fractions)
    low, high = bootstrap_ci(
        fractions,
        statistic=statistics.fmean,
        n_samples=bootstrap_samples,
        confidence=confidence,
        seed=seed,
    )
    # Category tallies
    tools: set[str] = set()
    creds: set[str] = set()
    payloads: set[str] = set()
    techniques: set[str] = set()
    for t in decoy_trials:
        tools.update(str(x) for x in (t.get("unique_tools") or []))
        creds.update(str(x) for x in (t.get("unique_credentials") or []))
        payloads.update(str(x) for x in (t.get("unique_payload_families") or []))
        techniques.update(str(x) for x in (t.get("attack_technique_ids") or []))
    return {
        "value": float(mean_frac),
        "unit": "fraction_of_budget",
        "n": len(decoy_trials),
        "interval": {"low": low, "high": high, "confidence": confidence},
        "status": "valid",
        "details": {
            "budget_max_unique_capabilities": budget,
            "mean_unique_capabilities_per_session": statistics.fmean(per_session),
            "category_counts": {
                "tools": len(tools),
                "credentials": len(creds),
                "payload_families": len(payloads),
                "attack_technique_ids": len(techniques),
            },
            "per_session_unique_capabilities": per_session,
        },
        "notes": "EER uses the declared experiment budget; not universal attacker cost",
    }


def _utility_value(trial: dict[str, Any], weights: dict[str, float]) -> float:
    outcomes = trial.get("defender_outcomes") or {}
    costs = trial.get("costs") or {}
    mapping = {
        "prevented_compromise": 1.0 if outcomes.get("prevented_compromise") else 0.0,
        "detection": 1.0 if outcomes.get("detection") else 0.0,
        "intelligence_yield": float(outcomes.get("intelligence_yield") or 0.0),
        "attacker_time_seconds": float(costs.get("attacker_time_seconds") or 0.0),
        "defender_time_seconds": float(costs.get("defender_time_seconds") or 0.0),
        "attacker_token_cost": float(costs.get("attacker_token_cost") or 0.0),
        "defender_infra_cost": float(costs.get("defender_infra_cost") or 0.0),
        "session_duration_seconds": float(trial.get("session_duration_seconds") or 0.0),
        "exchanges": float(trial.get("exchanges") or 0.0),
    }
    total = 0.0
    for key, weight in weights.items():
        if key not in mapping:
            raise AepError(
                f"utility.weights key {key!r} is not an observed trial field. "
                "Declare outcomes/costs in trials or adjust the utility model. "
                "Never substitute UHQS or delta_uhqs for VoD."
            )
        total += float(weight) * mapping[key]
    return total


def compute_vod(
    trials: list[dict[str, Any]],
    experiment: dict[str, Any],
    *,
    bootstrap_samples: int,
    confidence: float,
    seed: int,
) -> dict[str, Any]:
    utility = experiment.get("utility") or {}
    weights = utility.get("weights") or {}
    if not weights:
        return {
            "value": None,
            "unit": "utility_delta",
            "n": 0,
            "interval": {"low": None, "high": None, "confidence": confidence},
            "status": "not_computed",
            "details": {},
            "notes": "Missing utility.weights — refuse VoD (never use delta_uhqs)",
        }
    decoy_u = [_utility_value(t, weights) for t in trials if t.get("arm") == "decoy"]
    ref_u = [_utility_value(t, weights) for t in trials if t.get("arm") == "reference"]
    details = {
        "utility_name": utility.get("name"),
        "formula": utility.get("formula"),
        "weights": weights,
        "mean_u_decoy": statistics.fmean(decoy_u) if decoy_u else None,
        "mean_u_reference": statistics.fmean(ref_u) if ref_u else None,
        "delta_uhqs_forbidden": True,
    }
    if len(decoy_u) < 2 or len(ref_u) < 2:
        return {
            "value": None,
            "unit": "utility_delta",
            "n": len(decoy_u) + len(ref_u),
            "interval": {"low": None, "high": None, "confidence": confidence},
            "status": "inconclusive",
            "details": details,
            "notes": "Need at least 2 trials per arm for VoD",
        }
    value = statistics.fmean(decoy_u) - statistics.fmean(ref_u)
    # Bootstrap difference of means
    rng = random.Random(seed)
    diffs: list[float] = []
    for _ in range(bootstrap_samples):
        d_s = [decoy_u[rng.randrange(len(decoy_u))] for _ in range(len(decoy_u))]
        r_s = [ref_u[rng.randrange(len(ref_u))] for _ in range(len(ref_u))]
        diffs.append(statistics.fmean(d_s) - statistics.fmean(r_s))
    diffs.sort()
    alpha = 1.0 - confidence
    low = _percentile(diffs, alpha / 2) if diffs else None
    high = _percentile(diffs, 1 - alpha / 2) if diffs else None
    return {
        "value": float(value),
        "unit": "utility_delta",
        "n": len(decoy_u) + len(ref_u),
        "interval": {"low": low, "high": high, "confidence": confidence},
        "status": "valid",
        "details": details,
        "notes": "VoD = mean U_D(decoy) - mean U_D(reference); not delta_uhqs",
    }


def compute_fsv(
    trials: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    confidence: float,
    seed: int,
) -> dict[str, Any]:
    layers: dict[str, Any] = {}
    for layer in FSV_LAYERS:
        rows = [
            t
            for t in trials
            if (t.get("detector") or {}).get("layer") == layer
            and t.get("arm") in ("decoy", "reference")
            and (t.get("detector") or {}).get("predicted_decoy") is not None
            and (t.get("detector") or {}).get("actual_is_decoy") is not None
        ]
        tp = fp = tn = fn = 0
        for t in rows:
            pred = bool(t["detector"]["predicted_decoy"])
            actual = bool(t["detector"]["actual_is_decoy"])
            if pred and actual:
                tp += 1
            elif pred and not actual:
                fp += 1
            elif (not pred) and (not actual):
                tn += 1
            else:
                fn += 1
        n = tp + fp + tn + fn
        if n < 4 or (tp + fn) == 0 or (tn + fp) == 0:
            layers[layer] = {
                "n": n,
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "tpr": None,
                "fpr": None,
                "balanced_accuracy": None,
                "interval_tpr": {"low": None, "high": None, "confidence": confidence},
                "interval_fpr": {"low": None, "high": None, "confidence": confidence},
                "status": "inconclusive" if n else "not_computed",
            }
            continue
        tpr = tp / (tp + fn)
        fpr = fp / (fp + tn)
        bal = 0.5 * (tpr + (tn / (tn + fp)))
        # Bootstrap TPR/FPR by resampling rows
        rng = random.Random(seed + sum(ord(c) for c in layer))
        tprs: list[float] = []
        fprs: list[float] = []
        for _ in range(bootstrap_samples):
            sample = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
            stp = sfp = stn = sfn = 0
            for t in sample:
                pred = bool(t["detector"]["predicted_decoy"])
                actual = bool(t["detector"]["actual_is_decoy"])
                if pred and actual:
                    stp += 1
                elif pred and not actual:
                    sfp += 1
                elif (not pred) and (not actual):
                    stn += 1
                else:
                    sfn += 1
            if stp + sfn and stn + sfp:
                tprs.append(stp / (stp + sfn))
                fprs.append(sfp / (sfp + stn))
        tprs.sort()
        fprs.sort()
        alpha = 1.0 - confidence
        layers[layer] = {
            "n": n,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "tpr": tpr,
            "fpr": fpr,
            "balanced_accuracy": bal,
            "interval_tpr": {
                "low": _percentile(tprs, alpha / 2) if tprs else None,
                "high": _percentile(tprs, 1 - alpha / 2) if tprs else None,
                "confidence": confidence,
            },
            "interval_fpr": {
                "low": _percentile(fprs, alpha / 2) if fprs else None,
                "high": _percentile(fprs, 1 - alpha / 2) if fprs else None,
                "confidence": confidence,
            },
            "status": "valid",
        }
    return {
        "layers": layers,
        "global_scalar_emitted": False,
        "notes": "FSV is reported per layer; no global scalar",
    }

