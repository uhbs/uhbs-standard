"""Static fingerprint & artifact scanning (keys, banners, seeds, MACs)."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from uhbs_core.models import CheckResult

from .fs import (
    MAC_RE,
    PRIVATE_KEY_RE,
    RANDOM_SEED_RE,
    SSH_BANNER_RE,
    _iter_files,
    _read,
)

def _scan_artifacts(root: Path) -> Tuple[CheckResult, CheckResult, CheckResult, CheckResult]:
    key_hits: List[str] = []
    banner_hits: List[str] = []
    seed_hits: List[str] = []
    mac_hits: List[str] = []
    for fp in _iter_files(root):
        # Filename heuristics for committed host keys
        name = fp.name.lower()
        if name in {"ssh_host_rsa_key", "ssh_host_ed25519_key", "id_rsa", "id_ed25519"} or (
            name.endswith("_key") and "host" in name and not name.endswith(".pub")
        ):
            key_hits.append(str(fp.relative_to(root)))
            continue
        text = _read(fp)
        if not text:
            continue
        rel = str(fp.relative_to(root))
        if PRIVATE_KEY_RE.search(text):
            # allow test fixtures under *test* paths at reduced severity later
            key_hits.append(rel)
        if SSH_BANNER_RE.search(text):
            banner_hits.append(rel)
        if RANDOM_SEED_RE.search(text):
            seed_hits.append(rel)
        if MAC_RE.search(text):
            mac_hits.append(rel)

    def _score_clean(hits: List[str], cid: str, label: str, points: float) -> CheckResult:
        # Deduplicate; ignore obvious test-only paths for pass/fail but list them
        real = [h for h in hits if "test" not in h.lower() and "fixture" not in h.lower()]
        ok = len(real) == 0
        return CheckResult(
            id=cid,
            team="white",
            passed=ok,
            detail=(
                f"0 {label}"
                if ok
                else f"{len(real)} {label}: " + ", ".join(real[:5])
            ),
            score=points if ok else max(0.0, points - 5.0 * min(len(real), 4)),
            evidence=(real or hits)[:12],
        )

    return (
        _score_clean(key_hits, "white.static_private_keys", "static private keys", 10.0),
        _score_clean(banner_hits, "white.hardcoded_ssh_banners", "hardcoded SSH banners", 5.0),
        _score_clean(seed_hits, "white.predictable_seeds", "predictable PRNG seeds", 5.0),
        _score_clean(mac_hits, "white.hardcoded_macs", "hardcoded MAC addresses", 5.0),
    )
