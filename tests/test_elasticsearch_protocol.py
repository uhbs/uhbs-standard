"""Elasticsearch honeypot-fidelity probes — real-enough REST node vs canned-JSON stub."""

from __future__ import annotations

import contextlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.protocols import get_plugin
from uhbs_core.protocols.elasticsearch import (
    ElasticsearchPlugin,
    build_http_request,
    looks_like_cluster_health,
    looks_like_es_error,
    looks_like_es_root,
    parse_http_response,
)


def _by_id(checks: list[CheckResult], cid: str) -> CheckResult:
    for c in checks:
        if c.id == cid:
            return c
    raise AssertionError(f"missing check {cid}; have {[c.id for c in checks]}")


def test_elasticsearch_plugin_resolves_and_aliases() -> None:
    p = get_plugin("elasticsearch")
    assert isinstance(p, ElasticsearchPlugin)
    assert p.name == "elasticsearch"
    assert get_plugin("es").name == "elasticsearch"
    assert get_plugin("opensearch").name == "elasticsearch"
    assert get_plugin("elastic").name == "elasticsearch"


def test_es_http_helpers() -> None:
    req = build_http_request("GET", "/", host_header="localhost")
    assert req.startswith(b"GET / HTTP/1.1\r\n")
    status, headers, body = parse_http_response(
        b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
        b'{"tagline":"You Know, for Search","version":{"number":"8.0.0"}}'
    )
    assert status == 200
    assert headers.get("content-type") == "application/json"
    assert looks_like_es_root(body) is True
    assert (
        looks_like_cluster_health(
            b'{"cluster_name":"x","status":"green","number_of_nodes":1,"timed_out":false}'
        )
        is True
    )
    assert looks_like_es_error(
        b'{"error":{"type":"mapper_parsing_exception"},"status":400}'
    )


_STORE_LOCK = threading.Lock()
_INDICES: dict[str, dict[str, dict]] = {}


class _RealisticESHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send(self, code: int, payload: dict | bytes | None = None) -> None:
        if isinstance(payload, (dict, list)):
            body = json.dumps(payload).encode()
            ctype = "application/json"
        elif isinstance(payload, bytes):
            body = payload
            ctype = "application/json"
        else:
            body = b""
            ctype = "text/plain"
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0") or 0)
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(
                200,
                {
                    "name": "uhbs-node",
                    "cluster_name": "uhbs-es",
                    "tagline": "You Know, for Search",
                    "version": {"number": "8.11.0", "lucene_version": "9.8.0"},
                },
            )
            return
        if path == "/_cluster/health":
            self._send(
                200,
                {
                    "cluster_name": "uhbs-es",
                    "status": "yellow",
                    "number_of_nodes": 1,
                    "timed_out": False,
                },
            )
            return
        if "/_doc/" in path:
            parts = path.strip("/").split("/")
            if len(parts) >= 3 and parts[1] == "_doc":
                idx, doc_id = parts[0], parts[2]
                with _STORE_LOCK:
                    doc = _INDICES.get(idx, {}).get(doc_id)
                if doc is None:
                    self._send(
                        404,
                        {
                            "error": {
                                "type": "document_missing_exception",
                                "reason": "not found",
                            },
                            "status": 404,
                        },
                    )
                else:
                    self._send(
                        200,
                        {"_index": idx, "_id": doc_id, "found": True, "_source": doc},
                    )
                return
        self._send(
            404,
            {
                "error": {"type": "index_not_found_exception", "reason": path},
                "status": 404,
            },
        )

    def do_HEAD(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0].strip("/")
        with _STORE_LOCK:
            exists = path in _INDICES
        self.send_response(200 if exists else 404)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def do_PUT(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        body = self._read_body()
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[1] == "_doc":
            try:
                doc = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send(
                    400,
                    {
                        "error": {
                            "type": "mapper_parsing_exception",
                            "reason": "failed to parse",
                        },
                        "status": 400,
                    },
                )
                return
            idx, doc_id = parts[0], parts[2]
            with _STORE_LOCK:
                _INDICES.setdefault(idx, {})[doc_id] = doc
            self._send(
                201,
                {
                    "_index": idx,
                    "_id": doc_id,
                    "result": "created",
                    "_shards": {"total": 1, "successful": 1, "failed": 0},
                },
            )
            return
        idx = parts[0] if parts else ""
        if not idx:
            self._send(400, {"error": {"type": "invalid"}, "status": 400})
            return
        with _STORE_LOCK:
            _INDICES.setdefault(idx, {})
        self._send(200, {"acknowledged": True, "shards_acknowledged": True, "index": idx})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        _ = self._read_body()
        if path.endswith("/_refresh"):
            self._send(200, {"_shards": {"total": 1, "successful": 1, "failed": 0}})
            return
        self._send(400, {"error": {"type": "illegal_argument"}, "status": 400})

    def do_DELETE(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0].strip("/")
        idx = path.split("/", 1)[0]
        with _STORE_LOCK:
            existed = _INDICES.pop(idx, None) is not None
        if existed:
            self._send(200, {"acknowledged": True})
        else:
            self._send(
                404,
                {
                    "error": {"type": "index_not_found_exception", "reason": idx},
                    "status": 404,
                },
            )

    def do_FOOBAR(self) -> None:  # noqa: N802
        self._send(405, {"error": {"type": "method_not_allowed"}, "status": 405})


class _ShallowESHandler(BaseHTTPRequestHandler):
    """Always return a canned 200 cluster root — classic shallow ES decoy."""

    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _canned(self) -> None:
        body = json.dumps(
            {
                "name": "decoy",
                "cluster_name": "decoy",
                "tagline": "You Know, for Search",
                "version": {"number": "1.4.0"},
            }
        ).encode()
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length:
            with contextlib.suppress(OSError):
                self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        self._canned()

    def do_PUT(self) -> None:  # noqa: N802
        self._canned()

    def do_POST(self) -> None:  # noqa: N802
        self._canned()

    def do_DELETE(self) -> None:  # noqa: N802
        self._canned()

    def do_HEAD(self) -> None:  # noqa: N802
        self._canned()

    def do_FOOBAR(self) -> None:  # noqa: N802
        self._canned()


def _start_http(handler_cls) -> tuple[ThreadingHTTPServer, str, int, threading.Thread]:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    host, port = srv.server_address
    th = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
    th.start()
    return srv, str(host), int(port), th


def test_elasticsearch_realistic_stub_passes_fidelity_suite() -> None:
    with _STORE_LOCK:
        _INDICES.clear()
    srv, host, port, th = _start_http(_RealisticESHandler)
    try:
        target = TargetSpec(
            name="es-real",
            host=host,
            port=port,
            protocol="elasticsearch",
            protocols=["elasticsearch"],
        )
        plugin = ElasticsearchPlugin()
        fsm = plugin.probe_fsm(host, port, target, None)
        assert _by_id(fsm, "elasticsearch.fsm.malformed_json").passed is True
        assert _by_id(fsm, "elasticsearch.fsm.bad_method").passed is True
        assert _by_id(fsm, "elasticsearch.fsm.missing_index").passed is True

        nego = plugin.probe_negotiation(host, port, target, None)
        assert _by_id(nego, "elasticsearch.nego.root_info").passed is True
        assert _by_id(nego, "elasticsearch.nego.cluster_health").passed is True

        state = plugin.probe_state(host, port, target, None)
        assert _by_id(state, "elasticsearch.state.index_lifecycle").passed is True

        payload = plugin.probe_payload(host, port, target, None)
        assert _by_id(payload, "elasticsearch.payload.doc_roundtrip").passed is True
    finally:
        srv.shutdown()
        th.join(timeout=2.0)
        srv.server_close()


def test_elasticsearch_shallow_stub_fails_realism_checks() -> None:
    srv, host, port, th = _start_http(_ShallowESHandler)
    try:
        target = TargetSpec(
            name="es-shallow",
            host=host,
            port=port,
            protocol="elasticsearch",
            protocols=["elasticsearch"],
        )
        plugin = ElasticsearchPlugin()
        fsm = plugin.probe_fsm(host, port, target, None)
        assert _by_id(fsm, "elasticsearch.fsm.malformed_json").passed is False
        assert _by_id(fsm, "elasticsearch.fsm.bad_method").passed is False
        assert _by_id(fsm, "elasticsearch.fsm.missing_index").passed is False

        state = plugin.probe_state(host, port, target, None)
        assert _by_id(state, "elasticsearch.state.index_lifecycle").passed is False

        payload = plugin.probe_payload(host, port, target, None)
        assert _by_id(payload, "elasticsearch.payload.doc_roundtrip").passed is False
    finally:
        srv.shutdown()
        th.join(timeout=2.0)
        srv.server_close()
