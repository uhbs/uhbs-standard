"""Shared AEP constants and offline-input guards."""

from __future__ import annotations

import re

AEP_VERSION = "1.0.0"
UHBS_VERSION = "4.5.1"
ARMS = ("decoy", "reference", "evaluator_control")
FSV_LAYERS = ("network", "protocol", "system", "state")

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
