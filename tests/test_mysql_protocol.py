"""MySQL Module A handshake / FSM probes against a local greeting stub."""

from __future__ import annotations

import contextlib
import socket
import struct
import threading

from uhbs_core.models import TargetSpec
from uhbs_core.protocols.mysql import MySQLPlugin, _greeting_fields


def _mysql_greeting(
    *,
    version: str = "8.0.36",
    thread_id: int = 42,
    caps_low: int = 0xF7FF,
) -> bytes:
    """Minimal Initial Handshake Packet (protocol 10)."""
    payload = bytearray()
    payload.append(0x0A)
    payload.extend(version.encode("ascii") + b"\x00")
    payload.extend(struct.pack("<I", thread_id))
    payload.extend(b"\x01\x02\x03\x04\x05\x06\x07\x08")  # auth plugin data part 1
    payload.append(0x00)  # filler
    payload.extend(struct.pack("<H", caps_low))
    payload.append(0x21)  # charset
    payload.extend(struct.pack("<H", 0x0002))  # status
    payload.extend(struct.pack("<H", 0x8000))  # caps high
    payload.append(21)  # auth data len
    payload.extend(b"\x00" * 10)
    payload.extend(b"\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13")  # auth data part 2
    payload.extend(b"mysql_native_password\x00")
    hdr = struct.pack("<I", len(payload))[:3] + b"\x00"
    return hdr + bytes(payload)


def _serve_mysql_greeting() -> tuple[str, int, threading.Event, socket.socket]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)
    host, port = srv.getsockname()
    stop = threading.Event()
    greeting = _mysql_greeting()

    def _handle(conn: socket.socket) -> None:
        conn.settimeout(2.0)
        try:
            conn.sendall(greeting)
            with contextlib.suppress(TimeoutError):
                conn.recv(65535)
            # Auth deny ERR packet
            err = b"\xff\x15\x04#28000Access denied for user 'uhbs'"
            conn.sendall(struct.pack("<I", len(err))[:3] + b"\x02" + err)
        except OSError:
            pass
        finally:
            conn.close()

    def _loop() -> None:
        srv.settimeout(0.5)
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except TimeoutError:
                continue
            threading.Thread(target=_handle, args=(conn,), daemon=True).start()
        srv.close()

    threading.Thread(target=_loop, daemon=True).start()
    return host, port, stop, srv


def test_greeting_fields_parse() -> None:
    raw = _mysql_greeting(version="5.7.44-log", thread_id=7, caps_low=0xABCD)
    fields = _greeting_fields(raw)
    assert fields["ok"] is True
    assert fields["protocol"] == 0x0A
    assert fields["version"] == "5.7.44-log"
    assert fields["thread_id"] == 7
    assert fields["capability_low"] == 0xABCD
    assert fields.get("auth_plugin") is True


def test_mysql_module_a_against_greeting_stub() -> None:
    host, port, stop, srv = _serve_mysql_greeting()
    try:
        plugin = MySQLPlugin()
        target = TargetSpec(
            name="mysql-stub", host=host, port=port, protocol="mysql", protocols=["mysql"]
        )
        fsm = plugin.probe_fsm(host, port, target, None)
        assert len(fsm) == 5
        assert {c.id for c in fsm} == {
            "mysql.fsm.truncated_auth",
            "mysql.fsm.oversize_length",
            "mysql.fsm.zero_length_pkt",
            "mysql.fsm.reject_http_shape",
            "mysql.fsm.second_connection",
        }
        assert all(c.passed for c in fsm), [(c.id, c.detail) for c in fsm]

        nego = plugin.probe_negotiation(host, port, target, None)
        assert len(nego) == 5
        by_id = {c.id: c for c in nego}
        assert by_id["mysql.nego.handshake"].passed is True
        assert by_id["mysql.nego.protocol_version"].passed is True
        assert by_id["mysql.nego.version_string"].passed is True
        assert by_id["mysql.nego.thread_id"].passed is True
        assert by_id["mysql.nego.capability_flags"].passed is True

        state = plugin.probe_state(host, port, target, None)
        assert len(state) == 1
        assert state[0].id == "mysql.state.auth_deny"
        assert state[0].passed is True
    finally:
        stop.set()
        srv.close()
