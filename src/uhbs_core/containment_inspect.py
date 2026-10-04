"""Host-side container inspect rules for Module D (UHBS v5.0.1 Tier-1).

Critical isolation surface evaluated from ``docker inspect`` JSON — protocol-agnostic.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from uhbs_core.models import CheckResult
from uhbs_core.outcomes import CheckOutcome

_RUNTIME_SOCKET_SUFFIXES = (
    "docker.sock",
    "containerd.sock",
    "podman.sock",
    "cri-o.sock",
    "crio.sock",
    "kubelet.sock",
    "system_bus_socket",
)

_DANGEROUS_CAPS = frozenset(
    {
        "SYS_ADMIN",
        "SYS_PTRACE",
        "SYS_RAWIO",
        "NET_ADMIN",
        "NET_RAW",
        "SYS_MODULE",
        "DAC_READ_SEARCH",
        "CAP_SYS_ADMIN",
        "CAP_SYS_PTRACE",
        "CAP_SYS_RAWIO",
        "CAP_NET_ADMIN",
        "CAP_NET_RAW",
        "CAP_SYS_MODULE",
        "CAP_DAC_READ_SEARCH",
    }
)

_DEVICE_FAIL_RE = re.compile(
    r"^/dev/(mem|kmem|port|sd[a-z]|nvme\d)",
    re.IGNORECASE,
)


def _norm_cap(name: str) -> str:
    raw = str(name).strip().upper()
    if raw.startswith("CAP_"):
        return raw
    return f"CAP_{raw}" if raw else raw


def load_container_inspect() -> tuple[dict[str, Any] | None, str | None]:
    """Load inspect JSON from UHBS_CONTAINER_INSPECT_JSON (path or inline).

    Returns (data, error_detail). error_detail set when evidence missing/invalid.
    """
    raw = os.environ.get("UHBS_CONTAINER_INSPECT_JSON", "").strip()
    if not raw:
        return None, "UHBS_CONTAINER_INSPECT_JSON unset — host inspect evidence not attached"
    path = Path(raw)
    try:
        if path.is_file():
            blob = path.read_bytes()
            expected = os.environ.get("UHBS_CONTAINER_INSPECT_SHA256", "").strip()
            if expected:
                import hashlib

                digest = hashlib.sha256(blob).hexdigest()
                if digest.lower() != expected.lower().removeprefix("sha256:"):
                    return None, f"inspect digest mismatch: got {digest}"
            data = json.loads(blob.decode("utf-8"))
        else:
            data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"inspect evidence unreadable/invalid: {exc}"

    # docker inspect returns a list; accept dict or single-element list
    if isinstance(data, list):
        if not data:
            return None, "inspect JSON is an empty list"
        data = data[0]
    if not isinstance(data, dict):
        return None, "inspect JSON must be an object or non-empty list"
    if "HostConfig" not in data and "State" not in data and "Config" not in data:
        return None, "inspect JSON missing HostConfig/Config/State — structural validation failed"
    return data, None


def _bind_paths(host_config: dict[str, Any], mounts: list[Any]) -> list[str]:
    paths: list[str] = []
    for bind in host_config.get("Binds") or []:
        if isinstance(bind, str) and bind:
            paths.append(bind.split(":", 1)[0])
    for m in mounts or []:
        if not isinstance(m, dict):
            continue
        src = m.get("Source") or m.get("source") or ""
        if src:
            paths.append(str(src))
    return paths


def _sensitive_bind(path: str) -> bool:
    p = path.rstrip("/") or "/"
    if p == "/":
        return True
    for prefix in ("/proc", "/sys", "/dev", "/etc", "/var/run", "/run"):
        if p == prefix or p.startswith(prefix + "/"):
            return True
    lower = p.lower()
    return any(lower.endswith(suf) or f"/{suf}" in lower for suf in _RUNTIME_SOCKET_SUFFIXES)


def allowed_capabilities_from_env() -> set[str] | None:
    """None = undeclared (only empty CapAdd allowed); set = explicit whitelist."""
    raw = os.environ.get("UHBS_ALLOWED_CAPABILITIES", "").strip()
    if not raw:
        return None
    return {_norm_cap(x) for x in raw.split(",") if x.strip()}


def evaluate_container_inspect(
    data: dict[str, Any],
    *,
    allowed_capabilities: set[str] | None = None,
    readonly_rootfs_required: bool = False,
    expected_image_digest: str | None = None,
) -> list[CheckResult]:
    """Return D2 critical + DiD checks from one inspect object."""
    checks: list[CheckResult] = []
    hc = data.get("HostConfig") or {}
    cfg = data.get("Config") or {}
    mounts = data.get("Mounts") or []

    # --- Privileged ---
    privileged = bool(hc.get("Privileged"))
    checks.append(
        CheckResult.make(
            id="d2.container_privileged",
            team="blue",
            outcome=CheckOutcome.FAIL if privileged else CheckOutcome.PASS,
            detail="HostConfig.Privileged=true" if privileged else "not privileged",
            score=0.0 if privileged else 100.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )

    # --- Network / PID / IPC ---
    net_mode = str(hc.get("NetworkMode") or "")
    net_bad = net_mode == "host" or net_mode.startswith("container:")
    checks.append(
        CheckResult.make(
            id="d2.network_mode",
            team="blue",
            outcome=CheckOutcome.FAIL if net_bad else CheckOutcome.PASS,
            detail=f"NetworkMode={net_mode or 'default'}",
            score=0.0 if net_bad else 100.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )
    for mode_key, cid in (
        ("PidMode", "d2.pid_mode"),
        ("IpcMode", "d2.ipc_mode"),
    ):
        mode_val = str(hc.get(mode_key) or "")
        bad = mode_val == "host"
        checks.append(
            CheckResult.make(
                id=cid,
                team="blue",
                outcome=CheckOutcome.FAIL if bad else CheckOutcome.PASS,
                detail=f"{mode_key}={mode_val or 'default'}",
                score=0.0 if bad else 100.0,
                critical=True,
                mandatory=True,
                catalog_id="D2.critical",
            )
        )

    # --- Capabilities whitelist ---
    cap_add = [_norm_cap(c) for c in (hc.get("CapAdd") or []) if c]
    cap_drop = {_norm_cap(c) for c in (hc.get("CapDrop") or []) if c}
    allowed = allowed_capabilities
    if allowed is None:
        cap_fail = bool(cap_add)
        cap_detail = (
            "undeclared CapAdd="
            f"{cap_add} (declare UHBS_ALLOWED_CAPABILITIES or CapDrop ALL "
            "with empty CapAdd)"
            if cap_fail
            else "CapAdd empty (whitelist default)"
        )
    else:
        extra = [c for c in cap_add if c not in allowed]
        cap_fail = bool(extra)
        cap_detail = (
            f"CapAdd extras not allowlisted: {extra}"
            if cap_fail
            else "CapAdd within allowlist"
        )
    # Prefer CapDrop ALL as positive signal (DiD note in detail when present)
    if "CAP_ALL" in cap_drop or "ALL" in {str(c).upper() for c in (hc.get("CapDrop") or [])}:
        cap_detail = f"{cap_detail}; CapDrop includes ALL"
    # Dangerous caps always fail even if somehow allowlisted empty path
    dangerous_norm = {_norm_cap(x) for x in _DANGEROUS_CAPS}
    dangerous_hit = [
        c for c in cap_add if c in dangerous_norm or c in _DANGEROUS_CAPS
    ]
    if dangerous_hit:
        cap_fail = True
        cap_detail = f"dangerous CapAdd={dangerous_hit}"
    checks.append(
        CheckResult.make(
            id="d2.capability_whitelist",
            team="blue",
            outcome=CheckOutcome.FAIL if cap_fail else CheckOutcome.PASS,
            detail=cap_detail,
            score=0.0 if cap_fail else 100.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )

    # --- Non-root / userns ---
    user = str(cfg.get("User") or "").strip()
    userns = str(hc.get("UsernsMode") or "").strip()
    uid0 = (not user) or user in {"0", "root", "root:root"} or user.startswith("0:")
    userns_host = userns.lower() in {"", "host"}
    # PASS if non-root OR userns remapped (not host)
    root_fail = uid0 and userns_host
    checks.append(
        CheckResult.make(
            id="d2.non_root_userns",
            team="blue",
            outcome=CheckOutcome.FAIL if root_fail else CheckOutcome.PASS,
            detail=f"User={user or '(empty→root)'} UsernsMode={userns or '(empty)'}",
            score=0.0 if root_fail else 100.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )

    # --- SecurityOpt ---
    sec_opts = [str(x).lower() for x in (hc.get("SecurityOpt") or [])]
    unconfined = any(
        x in sec_opts or x.startswith("seccomp=unconfined") or x.startswith("apparmor=unconfined")
        or x == "label=disable" or x.startswith("label=disable")
        for x in sec_opts
    )
    checks.append(
        CheckResult.make(
            id="d2.security_profiles",
            team="blue",
            outcome=CheckOutcome.FAIL if unconfined else CheckOutcome.PASS,
            detail=f"SecurityOpt={sec_opts or ['(default)']}",
            score=0.0 if unconfined else 100.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )

    # --- Binds / mounts ---
    bad_binds = [p for p in _bind_paths(hc, mounts) if _sensitive_bind(p)]
    checks.append(
        CheckResult.make(
            id="d2.sensitive_binds",
            team="blue",
            outcome=CheckOutcome.FAIL if bad_binds else CheckOutcome.PASS,
            detail=f"sensitive binds={bad_binds[:8]}" if bad_binds else "no sensitive host binds",
            score=0.0 if bad_binds else 100.0,
            evidence=bad_binds[:12],
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )

    # --- Devices ---
    devices = hc.get("Devices") or []
    bad_devs: list[str] = []
    for d in devices:
        path = (
            str(d.get("PathOnHost") or d.get("path") or "")
            if isinstance(d, dict)
            else str(d)
        )
        if path and _DEVICE_FAIL_RE.search(path):
            bad_devs.append(path)
    checks.append(
        CheckResult.make(
            id="d2.device_exposure",
            team="blue",
            outcome=CheckOutcome.FAIL if bad_devs else CheckOutcome.PASS,
            detail=f"dangerous devices={bad_devs}" if bad_devs else "no raw host devices",
            score=0.0 if bad_devs else 100.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
    )

    # --- DiD: resource limits ---
    memory = hc.get("Memory") or 0
    nano = hc.get("NanoCpus") or 0
    pids = hc.get("PidsLimit") or 0
    limits_ok = bool(memory) or bool(nano) or bool(pids)
    checks.append(
        CheckResult.make(
            id="d2.resource_limits",
            team="blue",
            outcome=CheckOutcome.PASS if limits_ok else CheckOutcome.FAIL,
            detail=f"Memory={memory} NanoCpus={nano} PidsLimit={pids}",
            score=100.0 if limits_ok else 0.0,
            critical=False,
            mandatory=False,
            catalog_id="D2.did",
        )
    )

    # --- DiD / optional critical: ReadonlyRootfs ---
    ro = bool(hc.get("ReadonlyRootfs"))
    if readonly_rootfs_required:
        checks.append(
            CheckResult.make(
                id="d2.readonly_rootfs",
                team="blue",
                outcome=CheckOutcome.PASS if ro else CheckOutcome.FAIL,
                detail=f"ReadonlyRootfs={ro} (required)",
                score=100.0 if ro else 0.0,
                critical=True,
                mandatory=True,
                catalog_id="D2.critical",
            )
        )
    else:
        checks.append(
            CheckResult.make(
                id="d2.readonly_rootfs",
                team="blue",
                outcome=CheckOutcome.PASS if ro else CheckOutcome.FAIL,
                detail=f"ReadonlyRootfs={ro} (DiD)",
                score=100.0 if ro else 0.0,
                critical=False,
                mandatory=False,
                catalog_id="D2.did",
            )
        )

    # --- DiD: image digest ---
    if expected_image_digest:
        digests = data.get("RepoDigests") or []
        want = expected_image_digest.lower().removeprefix("sha256:")
        found = any(want in str(d).lower() for d in digests)
        checks.append(
            CheckResult.make(
                id="d2.image_digest",
                team="blue",
                outcome=CheckOutcome.PASS if found else CheckOutcome.FAIL,
                detail=f"expected={expected_image_digest} repo={digests[:3]}",
                score=100.0 if found else 0.0,
                critical=False,
                mandatory=False,
                catalog_id="D2.did",
            )
        )

    return checks


def missing_inspect_checks(detail: str) -> list[CheckResult]:
    """Critical D2 placeholders when inspect evidence is absent (INCOMPLETE path)."""
    ids = (
        "d2.container_privileged",
        "d2.network_mode",
        "d2.pid_mode",
        "d2.ipc_mode",
        "d2.capability_whitelist",
        "d2.non_root_userns",
        "d2.security_profiles",
        "d2.sensitive_binds",
        "d2.device_exposure",
    )
    return [
        CheckResult.make(
            id=cid,
            team="blue",
            outcome=CheckOutcome.NOT_TESTED,
            detail=detail,
            score=0.0,
            critical=True,
            mandatory=True,
            catalog_id="D2.critical",
        )
        for cid in ids
    ]
