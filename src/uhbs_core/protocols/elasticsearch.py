"""Elasticsearch honeypot grading plugin — Module A/B fidelity beyond canned JSON.

Focus: discriminate shallow ES decoys (always-200 cluster JSON) from nodes that
look real enough to engage (HTTP/JSON error shapes, cluster health, index +
document round-trips). Elasticsearch REST API over HTTP (default :9200);
aliases: ``es``, ``opensearch``.
"""

from __future__ import annotations

import json
import socket
import time

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.tps import TPS

_INDEX = "uhbs-probe"
_DOC_ID = "uhbs-1"


def _ot_timeout(tps: TPS | None, default: float = 4.0) -> float:
    if tps and isinstance(tps.raw, dict):
        for block in (
            tps.raw.get("performance_baseline"),
            tps.raw.get("experimental"),
            tps.raw,
        ):
            if isinstance(block, dict) and "probe_timeout_sec" in block:
                try:
                    return float(block["probe_timeout_sec"])
                except (TypeError, ValueError):
                    pass
    return default


def build_http_request(
    method: str,
    path: str,
    *,
    host_header: str = "uhbs-es",
    body: bytes | None = None,
    content_type: str = "application/json",
) -> bytes:
    """Build a minimal HTTP/1.1 request (Connection: close)."""
    if not path.startswith("/"):
        path = "/" + path
    headers = [
        f"{method.upper()} {path} HTTP/1.1",
        f"Host: {host_header}",
        "Accept: application/json",
        "Connection: close",
        "User-Agent: uhbs-es-probe/4.6",
    ]
    if body is not None:
        headers.append(f"Content-Type: {content_type}")
        headers.append(f"Content-Length: {len(body)}")
    else:
        headers.append("Content-Length: 0")
    head = ("\r\n".join(headers) + "\r\n\r\n").encode("ascii", "replace")
    return head if body is None else head + body


def parse_http_response(raw: bytes) -> tuple[int | None, dict[str, str], bytes]:
    """Return (status_code, headers_lower, body)."""
    if not raw:
        return None, {}, b""
    header_blob, _, body = raw.partition(b"\r\n\r\n")
    lines = header_blob.split(b"\r\n")
    if not lines:
        return None, {}, body
    status_line = lines[0].decode("utf-8", "replace")
    status: int | None = None
    parts = status_line.split()
    if len(parts) >= 2 and parts[1].isdigit():
        status = int(parts[1])
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if b":" not in line:
            continue
        key, _, value = line.partition(b":")
        headers[key.decode("utf-8", "replace").strip().lower()] = value.decode(
            "utf-8", "replace"
        ).strip()
    return status, headers, body


def looks_like_es_root(body: bytes) -> bool:
    lower = body.lower()
    if b"you know, for search" in lower:
        return True
    if b"tagline" in lower and (b"version" in lower or b"cluster_name" in lower):
        return True
    if b'"version"' in lower and (b"lucene_version" in lower or b"number" in lower):
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        return isinstance(data, dict) and "version" in data
    return False


def looks_like_cluster_health(body: bytes) -> bool:
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    status = str(data.get("status", "")).lower()
    return status in {"green", "yellow", "red"} and (
        "cluster_name" in data or "number_of_nodes" in data or "timed_out" in data
    )


def looks_like_es_error(body: bytes) -> bool:
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return b"error" in body.lower()
    if not isinstance(data, dict):
        return False
    if "error" in data:
        return True
    status = data.get("status")
    return isinstance(status, int) and status >= 400


def _http(
    host: str,
    port: int,
    method: str,
    path: str,
    *,
    body: bytes | None = None,
    timeout: float,
) -> tuple[int | None, bytes, str]:
    req = build_http_request(method, path, host_header=host, body=body)
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(req)
            chunks: list[bytes] = []
            while True:
                try:
                    chunk = sock.recv(65535)
                except TimeoutError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
                if sum(len(c) for c in chunks) >= 262144:
                    break
            raw = b"".join(chunks)
    except OSError as exc:
        return None, b"", str(exc)
    status, _, resp_body = parse_http_response(raw)
    return status, resp_body, ""


class ElasticsearchPlugin(ProtocolPlugin):
    name = "elasticsearch"
    families = ("it", "database", "search")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        checks: list[CheckResult] = []

        status, body, err = _http(
            host,
            port,
            "PUT",
            f"/{_INDEX}/_doc/{_DOC_ID}",
            body=b"{not-json",
            timeout=timeout,
        )
        ok = status is not None and status >= 400 and (
            looks_like_es_error(body) or status in {400, 406}
        )
        stub = status == 200 and looks_like_es_root(body)
        if ok:
            score, detail = 100.0, f"status={status} error-shaped body"
        elif stub:
            score, detail = 15.0, "200 root/canned JSON on malformed PUT (stub-like)"
        elif status is None:
            score, detail = 40.0, err or "no HTTP response"
        else:
            score, detail = 30.0, f"status={status} body={body[:60]!r}"
        checks.append(
            CheckResult(
                id="elasticsearch.fsm.malformed_json",
                team="red",
                passed=ok,
                detail=detail,
                score=score,
            )
        )

        status, body, err = _http(host, port, "FOOBAR", "/", timeout=timeout)
        ok = status is not None and status >= 400
        stub = status == 200
        if ok:
            score, detail = 100.0, f"status={status} for FOOBAR /"
        elif stub:
            score, detail = 15.0, "200 on FOOBAR / (stub-like)"
        else:
            score, detail = 35.0, err or f"status={status}"
        checks.append(
            CheckResult(
                id="elasticsearch.fsm.bad_method",
                team="red",
                passed=ok,
                detail=detail,
                score=score,
            )
        )

        missing = f"/uhbs-missing-{int(time.time())}"
        status, body, err = _http(host, port, "GET", missing, timeout=timeout)
        ok = status == 404 or (
            status is not None and status >= 400 and looks_like_es_error(body)
        )
        stub = status == 200 and looks_like_es_root(body)
        if ok:
            score, detail = 100.0, f"status={status} missing-index"
        elif stub:
            score, detail = 15.0, "200 root JSON for missing index (stub-like)"
        else:
            score, detail = 30.0, err or f"status={status} body={body[:60]!r}"
        checks.append(
            CheckResult(
                id="elasticsearch.fsm.missing_index",
                team="red",
                passed=ok,
                detail=detail,
                score=score,
            )
        )
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        strict = bool(tps and tps.strict_rfc_enforcement)
        checks: list[CheckResult] = []

        status, body, err = _http(host, port, "GET", "/", timeout=timeout)
        ok = status == 200 and looks_like_es_root(body)
        checks.append(
            CheckResult(
                id="elasticsearch.nego.root_info",
                team="blue",
                passed=ok,
                detail=(
                    body[:120].decode("utf-8", "replace")
                    if body
                    else (err or f"status={status}")
                ),
                score=100.0 if ok else 0.0,
                critical=strict,
            )
        )

        status, body, err = _http(host, port, "GET", "/_cluster/health", timeout=timeout)
        ok = status == 200 and looks_like_cluster_health(body)
        checks.append(
            CheckResult(
                id="elasticsearch.nego.cluster_health",
                team="blue",
                passed=ok,
                detail=(
                    body[:120].decode("utf-8", "replace")
                    if body
                    else (err or f"status={status}")
                ),
                score=100.0 if ok else 20.0,
            )
        )
        return checks

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        idx = f"{_INDEX}-{int(time.time()) % 100000}"

        put_status, put_body, put_err = _http(
            host,
            port,
            "PUT",
            f"/{idx}",
            body=b'{"settings":{"number_of_shards":1,"number_of_replicas":0}}',
            timeout=timeout,
        )
        # Require an ES-shaped create ack — not merely HTTP 200 (shallow decoys
        # often return a canned cluster root for every verb/path).
        put_ok = put_status in {200, 201} and (
            b"acknowledged" in put_body.lower()
            or (b'"index"' in put_body.lower() and b"error" not in put_body.lower())
        )

        head_status, head_body, head_err = _http(
            host, port, "HEAD", f"/{idx}", timeout=timeout
        )
        # Real ES HEAD /{index} is 200 with empty body; canned JSON roots are stubby.
        head_ok = head_status == 200 and not looks_like_es_root(head_body)

        del_status, del_body, del_err = _http(
            host, port, "DELETE", f"/{idx}", timeout=timeout
        )
        del_ok = del_status in {200, 201} and (
            b"acknowledged" in del_body.lower() or b"true" in del_body.lower()
        )

        # After DELETE, HEAD must be 404 — always-200 stubs fail here.
        gone_status, _, gone_err = _http(host, port, "HEAD", f"/{idx}", timeout=timeout)
        gone_ok = gone_status == 404

        ok = put_ok and head_ok and del_ok and gone_ok
        detail_parts = [
            f"PUT={put_status}",
            f"HEAD={head_status}",
            f"DELETE={del_status}",
            f"HEAD_after={gone_status}",
        ]
        if not put_ok and put_err:
            detail_parts.append(put_err)
        if not head_ok and head_err:
            detail_parts.append(head_err)
        if not del_ok and del_err:
            detail_parts.append(del_err)
        if not gone_ok and gone_err:
            detail_parts.append(gone_err)
        return [
            CheckResult(
                id="elasticsearch.state.index_lifecycle",
                team="blue",
                passed=ok,
                detail=" ".join(detail_parts),
                score=100.0 if ok else (50.0 if put_ok else 20.0),
                critical=True,
                evidence=[put_body[:40].hex()] if put_body else [],
            )
        ]

    def probe_payload(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        """Index a document then GET it back — strongest shallow-stub discriminator."""
        timeout = _ot_timeout(tps)
        idx = f"{_INDEX}-doc-{int(time.time()) % 100000}"
        marker = f"uhbs-es-{int(time.time())}"
        doc = json.dumps({"uhbs": marker, "probe": True}).encode("utf-8")

        _http(
            host,
            port,
            "PUT",
            f"/{idx}",
            body=b'{"settings":{"number_of_shards":1,"number_of_replicas":0}}',
            timeout=timeout,
        )

        put_status, put_body, put_err = _http(
            host,
            port,
            "PUT",
            f"/{idx}/_doc/{_DOC_ID}",
            body=doc,
            timeout=timeout,
        )
        put_ok = put_status in {200, 201}
        if not put_ok:
            return [
                CheckResult(
                    id="elasticsearch.payload.doc_roundtrip",
                    team="red",
                    passed=False,
                    detail=(
                        put_body[:100].decode("utf-8", "replace")
                        if put_body
                        else (put_err or f"doc PUT status={put_status}")
                    ),
                    score=10.0,
                    critical=True,
                )
            ]

        _http(host, port, "POST", f"/{idx}/_refresh", timeout=timeout)

        get_status, get_body, get_err = _http(
            host, port, "GET", f"/{idx}/_doc/{_DOC_ID}", timeout=timeout
        )
        ok = (
            get_status == 200
            and marker.encode() in get_body
            and (b'"_source"' in get_body or b"uhbs" in get_body)
        )
        _http(host, port, "DELETE", f"/{idx}", timeout=timeout)

        return [
            CheckResult(
                id="elasticsearch.payload.doc_roundtrip",
                team="red",
                passed=ok,
                detail=(
                    f"GET status={get_status} marker_found={marker.encode() in get_body}"
                    if get_body or get_status is not None
                    else (get_err or "doc GET failed")
                ),
                score=100.0 if ok else 10.0,
                critical=True,
                evidence=[get_body[:60].hex()] if get_body else [],
            )
        ]
