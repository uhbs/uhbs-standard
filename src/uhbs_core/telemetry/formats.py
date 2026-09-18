"""Declared-format structural validators for Module C (C1).

Validate only formats the TPS declares. Do not require every decoy to emit STIX.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_STIX_ID = re.compile(r"^[a-z0-9-]+--[0-9a-fA-F-]{36}$")
_STIX_TYPES = frozenset(
    {
        "indicator",
        "malware",
        "attack-pattern",
        "identity",
        "observed-data",
        "bundle",
        "relationship",
        "sighting",
        "tool",
        "campaign",
        "intrusion-set",
        "threat-actor",
        "vulnerability",
        "file",
        "ipv4-addr",
        "domain-name",
        "url",
        "network-traffic",
        "process",
        "software",
        "user-account",
        "directory",
        "windows-registry-key",
        "x509-certificate",
        "artifact",
        "email-addr",
        "mutex",
        "autonomous-system",
        "mac-addr",
        "ipv6-addr",
    }
)

SUPPORTED_FORMATS = frozenset(
    {"native_json", "jsonl", "ecs", "ocsf", "otlp", "stix21", "stix", "otel"}
)


@dataclass(frozen=True)
class FormatValidation:
    format_id: str
    ok: bool
    checked: int
    passed: int
    schema_uri: str
    schema_version: str
    validator_version: str
    errors: list[str]


def normalize_format(name: str | None) -> str | None:
    if not name:
        return None
    key = str(name).strip().lower().replace("-", "_").replace(".", "")
    aliases = {
        "stix": "stix21",
        "stix2": "stix21",
        "stix21": "stix21",
        "stix_21": "stix21",
        "stix_2_1": "stix21",
        "otel": "otlp",
        "opentelemetry": "otlp",
        "otlp_json": "otlp",
        "otlp": "otlp",
        "ecs": "ecs",
        "elastic_common_schema": "ecs",
        "ocsf": "ocsf",
        "native": "native_json",
        "native_json": "native_json",
        "json": "native_json",
        "jsonl": "jsonl",
    }
    return aliases.get(key, key if key in SUPPORTED_FORMATS else key)


def validate_stix21(obj: dict[str, Any]) -> tuple[bool, str]:
    """Standards-aware minimal STIX 2.1 structural check.

    Rejects non-empty unknown types (v4 bug: any non-empty type passed).
    """
    t = str(obj.get("type", "")).strip()
    if not t:
        return False, "missing type"
    if t == "bundle":
        if "objects" not in obj or not isinstance(obj["objects"], list):
            return False, "bundle missing objects"
        return True, "bundle"
    if t not in _STIX_TYPES:
        return False, f"unknown STIX type: {t}"
    oid = obj.get("id")
    if oid is not None and not _STIX_ID.match(str(oid)) and "--" not in str(oid):
        return False, f"id not STIX-shaped: {oid}"
    spec = str(obj.get("spec_version", obj.get("specVersion", ""))).strip()
    if not spec:
        return False, "missing spec_version"
    if not spec.startswith("2."):
        return False, f"spec_version={spec}"
    return True, t


def validate_otlp(obj: dict[str, Any]) -> tuple[bool, str]:
    keys = set(obj.keys())
    if keys & {"resourceSpans", "resourceMetrics", "resourceLogs"}:
        return True, "otlp-export"
    if "attributes" in obj and ("traceId" in obj or "spanId" in obj or "name" in obj):
        return True, "otlp-span-like"
    return False, "not OTLP JSON shape"


def validate_ecs(obj: dict[str, Any]) -> tuple[bool, str]:
    if "@timestamp" in obj and ("event" in obj or "ecs" in obj or "message" in obj):
        return True, "ecs"
    if "ecs" in obj and isinstance(obj.get("ecs"), dict):
        return True, "ecs-versioned"
    return False, "not ECS shape"


def validate_ocsf(obj: dict[str, Any]) -> tuple[bool, str]:
    # OCSF events typically carry class_uid / activity_id / metadata
    if ("class_uid" in obj or "class_name" in obj) and (
        "metadata" in obj or "activity_id" in obj or "time" in obj
    ):
        return True, "ocsf"
    return False, "not OCSF shape"


def validate_native_json(obj: dict[str, Any]) -> tuple[bool, str]:
    if not obj:
        return False, "empty object"
    if "__malformed__" in obj:
        return False, "malformed"
    return True, "native"


def validate_object(fmt: str, obj: dict[str, Any]) -> tuple[bool, str]:
    fmt_n = normalize_format(fmt) or fmt
    if fmt_n == "stix21":
        return validate_stix21(obj)
    if fmt_n == "otlp":
        return validate_otlp(obj)
    if fmt_n == "ecs":
        return validate_ecs(obj)
    if fmt_n == "ocsf":
        return validate_ocsf(obj)
    if fmt_n in {"native_json", "jsonl"}:
        return validate_native_json(obj)
    return False, f"unsupported declared format: {fmt}"


def validate_records(
    fmt: str,
    records: list[dict[str, Any]],
    *,
    schema_uri: str = "",
    schema_version: str = "",
) -> FormatValidation:
    fmt_n = normalize_format(fmt) or fmt
    errors: list[str] = []
    passed = 0
    checked = 0
    for obj in records:
        if not isinstance(obj, dict):
            continue
        checked += 1
        ok, detail = validate_object(fmt_n, obj)
        if ok:
            passed += 1
        else:
            if len(errors) < 8:
                errors.append(detail)
    return FormatValidation(
        format_id=fmt_n,
        ok=checked > 0 and passed == checked,
        checked=checked,
        passed=passed,
        schema_uri=schema_uri or f"uhbs:format/{fmt_n}",
        schema_version=schema_version or "uhbs-v5",
        validator_version="uhbs-telemetry-c1-1.0",
        errors=errors,
    )


def looks_like_stix_candidate(obj: dict[str, Any]) -> bool:
    """True only when the object claims STIX fields — not merely any 'type'."""
    return bool(
        obj.get("spec_version")
        or obj.get("specVersion")
        or (obj.get("type") == "bundle" and "objects" in obj)
        or (
            isinstance(obj.get("type"), str)
            and str(obj.get("type")) in _STIX_TYPES
            and ("id" in obj or "spec_version" in obj or "specVersion" in obj)
        )
    )
