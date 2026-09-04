"""Shared AEP constants and offline-input guards."""

from __future__ import annotations

import re
from pathlib import Path

AEP_VERSION = "1.0.0"
ARMS = ("decoy", "reference", "evaluator_control")
FSV_LAYERS = ("network", "protocol", "system", "state")


def _read_uhbs_version() -> str:
    """Read SoT without importing ``uhbs_core`` (AEP isolation policy)."""
    version_path = Path(__file__).resolve().parents[2] / "uhbs_core" / "_version.py"
    text = version_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', text, re.M)
    if not match:
        raise RuntimeError(f"cannot parse __version__ from {version_path}")
    return match.group(1)


UHBS_VERSION = _read_uhbs_version()

__all__ = ["AEP_VERSION", "ARMS", "FSV_LAYERS", "UHBS_VERSION"]

_FORBIDDEN_ARG_PATTERNS = (
    re.compile(r"^https?://", re.I),
    re.compile(r"^ftp://", re.I),
    re.compile(r"^ssh://", re.I),
    re.compile(r"^s3://", re.I),
    re.compile(r"^gs://", re.I),
    re.compile(r"^\\\\"),  # UNC
)

_FORBIDDEN_FIELD_KEYS = frozenset(
    {
        "host",
        "hostname",
        "port",
        "url",
        "uri",
        "endpoint",
        "target_host",
        "target_port",
        "executable",
        "command",
        "script",
        "hook",
        "callback",
        "container",
        "docker",
        "kubernetes",
        "kubeconfig",
        "api_key",
        "password",
        "private_key",
        "ssh_key",
        "credential",
        "credentials",
        "agent",
        "plugin",
        "subprocess",
    }
)
