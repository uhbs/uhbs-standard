"""Loopback-only HTTP client for openai_compatible provider."""

from __future__ import annotations

import contextlib
import json
from typing import Any

from .constants import _LOOPBACK_HOSTS, MAX_MODEL_RESPONSE_BYTES
from .errors import AepSlmError


def _assert_loopback_url(url: str) -> None:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise AepSlmError(
            f"endpoint.base_url: only http/https loopback URLs allowed, got {url!r}"
        )
    host = (parsed.hostname or "").lower()
    if host not in _LOOPBACK_HOSTS:
        raise AepSlmError(
            f"endpoint.base_url: host must be loopback "
            f"(127.0.0.1 / localhost / ::1), got {host!r}"
        )

def _read_limited(resp: Any, *, max_bytes: int = MAX_MODEL_RESPONSE_BYTES) -> bytes:
    # Prefer Content-Length so we refuse before streaming a multi-MiB body
    # (avoids peer ConnectionResetError races when the client aborts mid-read).
    headers = getattr(resp, "headers", None)
    declared: int | None = None
    if headers is not None:
        raw_len = headers.get("Content-Length")
        if raw_len is not None:
            try:
                declared = int(raw_len)
            except (TypeError, ValueError):
                declared = -1
            if declared > max_bytes:
                close = getattr(resp, "close", None)
                if callable(close):
                    with contextlib.suppress(OSError):
                        close()
                raise AepSlmError(
                    f"local model response exceeds {max_bytes} bytes "
                    "(refusing unbounded body)"
                )
    chunks: list[bytes] = []
    total = 0
    while True:
        try:
            chunk = resp.read(65536)
        except (ConnectionResetError, BrokenPipeError, TimeoutError) as exc:
            # Closing early after a size-cap abort can reset the peer mid-read
            # (especially chunked responses). Treat a large partial body as oversize.
            if total > max_bytes or (
                declared is None and total >= min(max_bytes, 65536)
            ):
                raise AepSlmError(
                    f"local model response exceeds {max_bytes} bytes "
                    "(refusing unbounded body)"
                ) from exc
            raise AepSlmError(
                f"local model connection failed while reading body: {exc}"
            ) from exc
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise AepSlmError(
                f"local model response exceeds {max_bytes} bytes "
                "(refusing unbounded body)"
            )
        chunks.append(chunk)
    return b"".join(chunks)


def _build_no_redirect_opener() -> Any:
    """HTTP opener that never follows redirects (SSRF guard)."""
    from urllib.error import HTTPError
    from urllib.request import (
        HTTPDefaultErrorHandler,
        HTTPErrorProcessor,
        HTTPHandler,
        HTTPRedirectHandler,
        HTTPSHandler,
        OpenerDirector,
        ProxyHandler,
        UnknownHandler,
    )

    class _RefuseRedirects(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
            raise AepSlmError(
                f"refusing HTTP redirect from local model endpoint "
                f"({code} -> {newurl})"
            )

        def http_error_302(self, req, fp, code, msg, headers):  # type: ignore[no-untyped-def]
            location = headers.get("Location", "")
            raise HTTPError(
                req.full_url,
                code,
                f"redirect refused -> {location}",
                headers,
                fp,
            )

        http_error_301 = http_error_302
        http_error_303 = http_error_302
        http_error_307 = http_error_302
        http_error_308 = http_error_302

    opener = OpenerDirector()
    # No ProxyHandler entries that could send loopback traffic elsewhere;
    # empty ProxyHandler disables env proxies for this opener.
    for handler in (
        ProxyHandler({}),
        UnknownHandler(),
        HTTPDefaultErrorHandler(),
        HTTPHandler(),
        HTTPSHandler(),
        HTTPErrorProcessor(),
        _RefuseRedirects(),
    ):
        opener.add_handler(handler)
    return opener


def _call_openai_compatible(
    config: dict[str, Any],
    *,
    system_prompt: str,
    user_prompt: str,
) -> str:
    # Lazy import keeps mock/status/validate free of HTTP stack at module import.
    from urllib.error import HTTPError, URLError
    from urllib.request import Request

    endpoint = config.get("endpoint") or {}
    base = str(endpoint.get("base_url") or "").rstrip("/")
    _assert_loopback_url(base)
    api_path = str(endpoint.get("api_path") or "/v1/chat/completions")
    if not api_path.startswith("/"):
        api_path = "/" + api_path
    if "://" in api_path:
        raise AepSlmError(
            "endpoint.api_path must be a path (e.g. /v1/chat/completions), "
            "not an absolute URL"
        )
    url = base + api_path
    # Re-check final URL host after concatenation.
    _assert_loopback_url(url)
    timeout = float(endpoint.get("timeout_seconds") or 60)
    model_name = (config.get("model") or {}).get("name") or "local-model"
    gen = config.get("generation") or {}
    body = {
        "model": model_name,
        "temperature": float(gen.get("temperature") or 0),
        "max_tokens": int(gen.get("max_tokens") or 256),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    payload = json.dumps(body).encode("utf-8")
    req = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    opener = _build_no_redirect_opener()
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw_bytes = _read_limited(resp)
            raw = raw_bytes.decode("utf-8")
    except AepSlmError:
        raise
    except HTTPError as exc:
        # Redirect refusals surface as HTTPError from our handler.
        if 300 <= int(exc.code) < 400:
            location = exc.headers.get("Location", "") if exc.headers else ""
            raise AepSlmError(
                f"refusing HTTP redirect from local model endpoint "
                f"({exc.code} -> {location})"
            ) from exc
        raise AepSlmError(f"local model HTTP error: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise AepSlmError(f"local model connection failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise AepSlmError(f"local model timed out after {timeout}s") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AepSlmError(f"local model returned non-JSON: {exc}") from exc
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise AepSlmError(
            "local model response missing choices[0].message.content"
        ) from exc

