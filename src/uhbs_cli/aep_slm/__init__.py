"""UHBS AEP Small Language Model evaluator (alpha) — opt-in only.

Generates local AEP trial JSONL from an explicitly unlocked config. Disabled by
default: templates ship with ``enabled: false`` and incomplete activation
attestations. Does not change UHQS.

Trust boundary:
- No honeypot / production probing
- No tool/function calling
- openai_compatible uses loopback-only HTTP, no redirects, size-capped reads
- Default / packaged configs never run model calls until the user edits files
"""

from __future__ import annotations

from .config import (
    activation_blockers,
    default_config_template,
    load_config,
    validate_config,
    write_init_config,
)
from .constants import (
    AEP_SLM_VERSION,
    MAX_MODEL_RESPONSE_BYTES,
    SCHEMA_NAME,
    UNLOCK_PHRASE,
)
from .errors import AepSlmError
from .generate import _trial_from_response, generate_trials, status_report
from .http_client import _call_openai_compatible, _read_limited
from .providers import _render_user_prompt

__all__ = [
    "AEP_SLM_VERSION",
    "AepSlmError",
    "MAX_MODEL_RESPONSE_BYTES",
    "SCHEMA_NAME",
    "UNLOCK_PHRASE",
    "_call_openai_compatible",
    "_read_limited",
    "_render_user_prompt",
    "_trial_from_response",
    "activation_blockers",
    "default_config_template",
    "generate_trials",
    "load_config",
    "status_report",
    "validate_config",
    "write_init_config",
]
