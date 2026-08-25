"""Constants for the alpha AEP SLM evaluator."""

from __future__ import annotations

AEP_SLM_VERSION = "0.1.0-alpha"
UNLOCK_PHRASE = "I_ENABLE_AEP_SLM_ALPHA"
SCHEMA_NAME = "aep-slm.schema.json"
MAX_MODEL_RESPONSE_BYTES = 256 * 1024

_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
