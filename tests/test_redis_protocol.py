"""Redis honeypot-fidelity probes — real-enough RESP server vs shallow always-OK stub."""

from __future__ import annotations

import contextlib
import socket
import threading

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.protocols import get_plugin
from uhbs_core.protocols.redis import (
    RedisPlugin,
    encode_command,
    is_ok,
    is_pong,
    is_resp_error,
    parse_bulk_string,
)


def _by_id(checks: list[CheckResult], cid: str) -> CheckResult:
    for c in checks:
        if c.id == cid:
            return c
    raise AssertionError(f"missing check {cid}; have {[c.id for c in checks]}")


def test_redis_plugin_resolves() -> None:
    p = get_plugin("redis")
    assert isinstance(p, RedisPlugin)
    assert p.name == "redis"


def test_resp_helpers() -> None:
    assert encode_command("PING").startswith(b"*1\r\n$4\r\nPING\r\n")
    assert is_pong(b"+PONG\r\n") is True
    assert is_ok(b"+OK\r\n") is True
    assert is_resp_error(b"-ERR unknown command\r\n") is True
    assert parse_bulk_string(b"$3\r\nabc\r\n") == "abc"


def _start_tcp_stub(
    handler,
) -> tuple[socket.socket, str, int, threading.Event, threading.Thread]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(32)
    host, port = srv.getsockname()
    stop = threading.Event()

    def _serve_one(conn: socket.socket) -> None:
        with conn:
            conn.settimeout(2.0)
            with contextlib.suppress(OSError):
                handler(conn)

    def _loop() -> None:
        srv.settimeout(0.5)
        workers: list[threading.Thread] = []
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except TimeoutError:
                continue
            th_one = threading.Thread(target=_serve_one, args=(conn,), daemon=True)
            th_one.start()
            workers.append(th_one)
        for w in workers:
            w.join(timeout=0.5)
        srv.close()

    th = threading.Thread(target=_loop, daemon=True)
    th.start()
    return srv, host, port, stop, th


_STORE_LOCK = threading.Lock()
_STORE: dict[str, str] = {}


def _realistic_redis(conn: socket.socket) -> None:
    """Minimal RESP server with real errors, INFO, and cross-conn key store."""
    buf = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            return
        buf += chunk
        while True:
            if not buf:
                break
            if not buf.startswith(b"*"):
                if b"\r\n" not in buf:
                    break
                line, _, buf = buf.partition(b"\r\n")
                verb = line.decode("utf-8", "replace").split(" ")[0].upper()
                if verb == "PING":
                    conn.sendall(b"+PONG\r\n")
                elif verb == "QUIT":
                    conn.sendall(b"+OK\r\n")
                    return
                else:
                    conn.sendall(b"-ERR unknown command\r\n")
                continue

            try:
                first_nl = buf.index(b"\r\n")
            except ValueError:
                break
            try:
                n = int(buf[1:first_nl])
            except ValueError:
                conn.sendall(b"-ERR protocol error\r\n")
                return
            parts: list[bytes] = []
            pos = first_nl + 2
            ok_parse = True
            for _ in range(n):
                if pos >= len(buf) or buf[pos : pos + 1] != b"$":
                    ok_parse = False
                    break
                try:
                    nl = buf.index(b"\r\n", pos)
                    length = int(buf[pos + 1 : nl])
                    start = nl + 2
                    end = start + length
                    if end + 2 > len(buf):
                        ok_parse = False
                        break
                    parts.append(buf[start:end])
                    pos = end + 2
                except ValueError:
                    ok_parse = False
                    break
            if not ok_parse:
                break
            buf = buf[pos:]
            if not parts:
                conn.sendall(b"-ERR empty command\r\n")
                continue
            cmd = parts[0].decode("utf-8", "replace").upper()
            args = [p.decode("utf-8", "replace") for p in parts[1:]]
            if cmd == "PING":
                conn.sendall(b"+PONG\r\n")
            elif cmd == "ECHO":
                if len(args) != 1:
                    conn.sendall(b"-ERR wrong number of arguments for 'echo'\r\n")
                else:
                    payload = args[0].encode()
                    conn.sendall(f"${len(payload)}\r\n".encode() + payload + b"\r\n")
            elif cmd == "INFO":
                body = b"# Server\r\nredis_version:7.2.0\r\ntcp_port:6379\r\n"
                conn.sendall(f"${len(body)}\r\n".encode() + body + b"\r\n")
            elif cmd == "SET":
                if len(args) < 2:
                    conn.sendall(b"-ERR wrong number of arguments for 'set'\r\n")
                else:
                    with _STORE_LOCK:
                        _STORE[args[0]] = args[1]
                    conn.sendall(b"+OK\r\n")
            elif cmd == "GET":
                if len(args) != 1:
                    conn.sendall(b"-ERR wrong number of arguments for 'get'\r\n")
                else:
                    with _STORE_LOCK:
                        val = _STORE.get(args[0])
                    if val is None:
                        conn.sendall(b"$-1\r\n")
                    else:
                        raw = val.encode()
                        conn.sendall(f"${len(raw)}\r\n".encode() + raw + b"\r\n")
            elif cmd == "INCR":
                if len(args) != 1:
                    conn.sendall(b"-ERR wrong number of arguments for 'incr'\r\n")
                else:
                    with _STORE_LOCK:
                        cur = int(_STORE.get(args[0], "0")) + 1
                        _STORE[args[0]] = str(cur)
                    conn.sendall(f":{cur}\r\n".encode())
            elif cmd == "DEL":
                if not args:
                    conn.sendall(b"-ERR wrong number of arguments for 'del'\r\n")
                else:
                    with _STORE_LOCK:
                        removed = sum(1 for k in args if _STORE.pop(k, None) is not None)
                    conn.sendall(f":{removed}\r\n".encode())
            elif cmd == "EXISTS":
                if not args:
                    conn.sendall(b"-ERR wrong number of arguments for 'exists'\r\n")
                else:
                    with _STORE_LOCK:
                        n_exist = sum(1 for k in args if k in _STORE)
                    conn.sendall(f":{n_exist}\r\n".encode())
            else:
                conn.sendall(f"-ERR unknown command '{cmd}'\r\n".encode())


def _shallow_always_ok(conn: socket.socket) -> None:
    """Shallow honeypot: every inbound frame gets +OK (or +PONG for PING)."""
    while True:
        data = conn.recv(4096)
        if not data:
            return
        if b"PING" in data.upper():
            conn.sendall(b"+PONG\r\n")
        else:
            conn.sendall(b"+OK\r\n")


def test_redis_realistic_stub_passes_fidelity_suite() -> None:
    with _STORE_LOCK:
        _STORE.clear()
    _srv, host, port, stop, th = _start_tcp_stub(_realistic_redis)
    try:
        target = TargetSpec(
            name="redis-real", host=host, port=port, protocol="redis", protocols=["redis"]
        )
        plugin = RedisPlugin()
        fsm = plugin.probe_fsm(host, port, target, None)
        assert _by_id(fsm, "redis.fsm.invalid_verb").passed is True
        assert _by_id(fsm, "redis.fsm.wrong_arity").passed is True
        assert _by_id(fsm, "redis.fsm.truncated_array").passed is True

        nego = plugin.probe_negotiation(host, port, target, None)
        assert _by_id(nego, "redis.nego.ping").passed is True
        assert _by_id(nego, "redis.nego.echo").passed is True
        assert _by_id(nego, "redis.nego.info_server").passed is True

        state = plugin.probe_state(host, port, target, None)
        assert _by_id(state, "redis.state.set_get").passed is True
        assert _by_id(state, "redis.state.incr").passed is True
        assert _by_id(state, "redis.state.del_exists").passed is True

        payload = plugin.probe_payload(host, port, target, None)
        assert _by_id(payload, "redis.payload.cross_conn_get").passed is True
    finally:
        stop.set()
        th.join(timeout=2.0)


def test_redis_shallow_stub_fails_realism_checks() -> None:
    _srv, host, port, stop, th = _start_tcp_stub(_shallow_always_ok)
    try:
        target = TargetSpec(
            name="redis-shallow",
            host=host,
            port=port,
            protocol="redis",
            protocols=["redis"],
        )
        plugin = RedisPlugin()
        fsm = plugin.probe_fsm(host, port, target, None)
        assert _by_id(fsm, "redis.fsm.invalid_verb").passed is False
        assert _by_id(fsm, "redis.fsm.wrong_arity").passed is False

        state = plugin.probe_state(host, port, target, None)
        assert _by_id(state, "redis.state.set_get").passed is False

        payload = plugin.probe_payload(host, port, target, None)
        assert _by_id(payload, "redis.payload.cross_conn_get").passed is False
    finally:
        stop.set()
        th.join(timeout=2.0)
