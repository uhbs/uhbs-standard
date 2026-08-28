"""AEP analysis orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from uhbs_cli import __version__

from .constants import AEP_VERSION, ARMS, UHBS_VERSION
from .errors import AepError
from .metrics import compute_dtdr, compute_eer, compute_fsv, compute_vod


@dataclass
class AnalyzeConfig:
    bootstrap_samples: int = 1000
    confidence: float = 0.95
    seed: int = 42
    experiment_path: str | None = None
    trials_path: str | None = None
    scorecard_ref: str | None = None


def _control_status(
    trials: list[dict[str, Any]], experiment: dict[str, Any]
) -> tuple[str, list[str]]:
    warnings: list[str] = []
    controls = [t for t in trials if t.get("arm") == "evaluator_control"]
    primary = experiment.get("primary_outcome")
    needs_control = primary in ("vod", "eer", "fsv")
    if not controls:
        if needs_control:
            warnings.append(
                "evaluator_control arm missing; capability-dependent claims are weakened"
            )
            return "missing", warnings
        return "not_required", warnings
    failed = [t for t in controls if t.get("evaluator_control_passed") is False]
    if failed:
        warnings.append(
            f"evaluator_control failed on {len(failed)}/{len(controls)} trials"
        )
        return "failed", warnings
    unknown = [t for t in controls if "evaluator_control_passed" not in t]
    if unknown:
        warnings.append("evaluator_control trials lack evaluator_control_passed")
        return "missing", warnings
    return "passed", warnings


def analyze(
    experiment: dict[str, Any],
    trials: list[dict[str, Any]],
    *,
    config: AnalyzeConfig | None = None,
) -> dict[str, Any]:
    cfg = config or AnalyzeConfig()
    warnings: list[str] = []
    arms_present = {t.get("arm") for t in trials}
    if "decoy" not in arms_present or "reference" not in arms_present:
        raise AepError("Analysis refused: both decoy and reference arms are required")

    control_status, ctrl_warnings = _control_status(trials, experiment)
    warnings.extend(ctrl_warnings)

    min_n = int((experiment.get("repetitions") or {}).get("minimum_per_arm", 1))
    per_arm: dict[str, dict[str, int]] = {}
    for arm in ARMS:
        arm_trials = [t for t in trials if t.get("arm") == arm]
        cens = sum(1 for t in arm_trials if t.get("censored"))
        per_arm[arm] = {"n": len(arm_trials), "censored": cens}
        if arm in ("decoy", "reference") and len(arm_trials) < min_n:
            warnings.append(f"low sample size for {arm}: n={len(arm_trials)} < {min_n}")

    total = sum(v["n"] for v in per_arm.values())
    cens_total = sum(v["censored"] for v in per_arm.values())
    censoring_rate = (cens_total / total) if total else 0.0
    if censoring_rate >= 0.5:
        warnings.append(f"high censoring rate: {censoring_rate:.2f}")

    bs = cfg.bootstrap_samples
    conf = cfg.confidence
    seed = cfg.seed

    metrics: dict[str, Any] = {
        "vod": compute_vod(
            trials, experiment, bootstrap_samples=bs, confidence=conf, seed=seed
        ),
        "dtdr": compute_dtdr(
            trials, bootstrap_samples=bs, confidence=conf, seed=seed + 1
        ),
        "eer": compute_eer(
            trials, experiment, bootstrap_samples=bs, confidence=conf, seed=seed + 2
        ),
        "fsv": compute_fsv(
            trials, bootstrap_samples=bs, confidence=conf, seed=seed + 3
        ),
    }

    if control_status == "failed":
        status = "control_failed"
        for key in ("vod", "dtdr", "eer"):
            if metrics[key].get("status") == "valid":
                metrics[key]["status"] = "control_failed"
        for layer in metrics["fsv"]["layers"].values():
            if layer.get("status") == "valid":
                layer["status"] = "control_failed"
    else:
        primary = experiment.get("primary_outcome", "dtdr")
        primary_status = "valid"
        if primary == "fsv":
            layer_statuses = [
                layer.get("status") for layer in metrics["fsv"]["layers"].values()
            ]
            if any(s == "valid" for s in layer_statuses):
                primary_status = "valid"
            elif any(s == "inconclusive" for s in layer_statuses):
                primary_status = "inconclusive"
            else:
                primary_status = "not_computed"
        else:
            primary_status = metrics.get(primary, {}).get("status", "inconclusive")
        status = "valid" if primary_status == "valid" else "inconclusive"
        if primary_status == "not_computed":
            status = "inconclusive"
            warnings.append(f"primary outcome {primary} was not computed")

    if per_arm["decoy"]["n"] < 5 or per_arm["reference"]["n"] < 5:
        warnings.append("n < 5 per arm — treat results as exploratory")

    # Only record scorecard_ref when the CLI validated it via --scorecard.
    # Do not promote an unverified experiment.scorecard_ref into provenance.
    scorecard_ref = cfg.scorecard_ref
    declared_ref = experiment.get("scorecard_ref")
    if scorecard_ref is None and declared_ref:
        warnings.append(
            "experiment.scorecard_ref is declared but was not validated; "
            "pass --scorecard <path> to link and verify the scorecard JSON"
        )

    interpretation = (
        "AEP evidence observed under the declared controlled conditions. "
        "This addendum does not change UHQS, δ_C, or letter grade."
    )
    limitations = [
        "Informative research metrics only — not a UHBS grade or certification.",
        "Results apply to the declared task, budget, timeout, and evaluator tier.",
        "Never equate delta_uhqs with Value of Deception (VoD).",
    ]

    result = {
        "aep_version": AEP_VERSION,
        "uhbs_version": UHBS_VERSION,
        "experiment_id": experiment["experiment_id"],
        "status": status,
        "control_status": control_status,
        "metrics": metrics,
        "sample": {
            "per_arm": per_arm,
            "censoring_rate": censoring_rate,
            "exclusions": [],
        },
        "provenance": {
            "tool": "uhbs aep",
            "tool_version": __version__,
            "analysis_seed": seed,
            "generated_at": datetime.now(UTC)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "experiment_path": cfg.experiment_path,
            "trials_path": cfg.trials_path,
            "scorecard_ref": scorecard_ref,
            "bootstrap_samples": bs,
            "confidence": conf,
        },
        "uhqs_unchanged": True,
        "interpretation": interpretation,
        "limitations": limitations,
        "warnings": warnings,
    }
    return result

