"""MQTT honeypot-fidelity probes — real-enough broker vs shallow CONNECT stub."""

from __future__ import annotations

import contextlib
import socket
import threading

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.protocols import get_plugin
from uhbs_core.protocols.mqtt import (
    MQTTPlugin,
    build_connect,
    build_pingreq,
    build_publish,
    build_subscribe,
    build_unsubscribe,
    is_connack,
    is_pingresp,
    is_publish,
    is_suback,
    is_unsuback,
)
from uhbs_core.tps import TPS


def _by_id(checks: list[CheckResult], cid: str) -> CheckResult:
    for c in checks:
        if c.id == cid:
            return c
    raise AssertionError(f"missing check {cid}; have {[c.id for c in checks]}")


def test_mqtt_plugin_resolves_and_aliases() -> None:
    p = get_plugin("mqtt")
    assert isinstance(p, MQTTPlugin)
    assert p.name == "mqtt"
    assert get_plugin("mqtts").name == "mqtt"


def test_build_connect_is_well_formed() -> None:
    req = build_connect("uhbs-probe")
    assert req[0] == 0x10
    assert b"MQTT" in req
    assert b"uhbs-probe" in req


def test_packet_helpers_roundtrip_shapes() -> None:
    assert is_connack(b"\x20\x02\x00\x00") is True
    assert is_connack(b"HTTP/1.1") is False
    assert is_suback(b"\x90\x03\x00\x01\x00") is True
    assert is_unsuback(b"\xb0\x02\x00\x02") is True
    assert is_pingresp(b"\xd0\x00") is True
    assert is_publish(build_publish("t", b"x")) is True
    assert build_pingreq() == b"\xc0\x00"
    assert build_subscribe("a")[0] == 0x82
    assert build_unsubscribe("a")[0] == 0xA2


def _start_tcp_stub(handler) -> tuple[socket.socket, str, int, threading.Event, threading.Thread]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)
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


# Shared in-memory fanout for the realistic multi-client stub
_ECHO_LOCK = threading.Lock()
_ECHO_SUBS: dict[str, list[socket.socket]] = {}


def _realistic_broker_with_echo(conn: socket.socket) -> None:
    data = conn.recv(512)
    if not data:
        return
    if data[0] != 0x10:
        return
    if len(data) >= 9 and data[2:4] == b"\x00\x04" and data[4:8] == b"MQTT" and data[8] != 4:
        conn.sendall(b"\x20\x02\x00\x01")
        return
    conn.sendall(b"\x20\x02\x00\x00")
    try:
        while True:
            more = conn.recv(1024)
            if not more:
                return
            if more[0] == 0x82:
                body = more[2:] if more[1] < 0x80 else more[3:]
                pkt_id = body[:2] if len(body) >= 2 else b"\x00\x01"
                if len(body) >= 4:
                    tlen = int.from_bytes(body[2:4], "big")
                    topic = body[4 : 4 + tlen].decode("utf-8", "replace")
                    with _ECHO_LOCK:
                        _ECHO_SUBS.setdefault(topic, []).append(conn)
                conn.sendall(b"\x90\x03" + pkt_id + b"\x00")
            elif more[0] == 0xA2:
                body = more[2:] if more[1] < 0x80 else more[3:]
                pkt_id = body[:2] if len(body) >= 2 else b"\x00\x02"
                if len(body) >= 4:
                    tlen = int.from_bytes(body[2:4], "big")
                    topic = body[4 : 4 + tlen].decode("utf-8", "replace")
                    with _ECHO_LOCK:
                        _ECHO_SUBS[topic] = [
                            s for s in _ECHO_SUBS.get(topic, []) if s is not conn
                        ]
                conn.sendall(b"\xb0\x02" + pkt_id)
            elif more[0] == 0xC0:
                conn.sendall(b"\xd0\x00")
            elif (more[0] & 0xF0) == 0x30:
                body = more[2:] if more[1] < 0x80 else more[3:]
                if len(body) >= 2:
                    tlen = int.from_bytes(body[0:2], "big")
                    topic = body[2 : 2 + tlen].decode("utf-8", "replace")
                    with _ECHO_LOCK:
                        targets = list(_ECHO_SUBS.get(topic, []))
                    for s in targets:
                        if s is conn:
                            continue
                        with contextlib.suppress(OSError):
                            s.sendall(more)
            elif more[0] == 0xE0:
                return
    finally:
        with _ECHO_LOCK:
            for topic in list(_ECHO_SUBS):
                _ECHO_SUBS[topic] = [s for s in _ECHO_SUBS[topic] if s is not conn]


def _shallow_always_connack(conn: socket.socket) -> None:
    """Shallow honeypot: every inbound frame gets a success CONNACK."""
    while True:
        data = conn.recv(512)
        if not data:
            return
        conn.sendall(b"\x20\x02\x00\x00")


def test_mqtt_realistic_stub_passes_fidelity_suite() -> None:
    srv, host, port, stop, th = _start_tcp_stub(_realistic_broker_with_echo)
    try:
        target = TargetSpec(
            name="mqtt-real", host=host, port=port, protocol="mqtt", protocols=["mqtt"]
        )
        tps = TPS(
            name="mqtt-real",
            profile_class="Low-Interaction",
            protocol="mqtt",
            protocols=["mqtt"],
            strict_rfc_enforcement=True,
        )
        plugin = MQTTPlugin()
        fsm = plugin.probe_fsm(host, port, target, tps)
        assert _by_id(fsm, "mqtt.fsm.illegal_type").passed is True
        assert _by_id(fsm, "mqtt.fsm.publish_before_connect").passed is True
        assert _by_id(fsm, "mqtt.fsm.bad_protocol_level").passed is True
        assert _by_id(fsm, "mqtt.fsm.truncated_connect").passed is True

        nego = plugin.probe_negotiation(host, port, target, tps)
        assert _by_id(nego, "mqtt.nego.connack").passed is True
        assert _by_id(nego, "mqtt.nego.connack_framing").passed is True

        state = plugin.probe_state(host, port, target, tps)
        assert _by_id(state, "mqtt.state.subscribe").passed is True
        assert _by_id(state, "mqtt.state.ping").passed is True
        assert _by_id(state, "mqtt.state.unsubscribe").passed is True

        payload = plugin.probe_payload(host, port, target, tps)
        assert _by_id(payload, "mqtt.payload.pubsub_echo").passed is True
    finally:
        stop.set()
        th.join(timeout=2.0)


def test_mqtt_shallow_stub_fails_realism_checks() -> None:
    srv, host, port, stop, th = _start_tcp_stub(_shallow_always_connack)
    try:
        target = TargetSpec(
            name="mqtt-shallow", host=host, port=port, protocol="mqtt", protocols=["mqtt"]
        )
        plugin = MQTTPlugin()
        fsm = plugin.probe_fsm(host, port, target, None)
        # Always-CONNACK on pre-auth PUBLISH / bad level = stub smell
        assert _by_id(fsm, "mqtt.fsm.publish_before_connect").passed is False
        assert _by_id(fsm, "mqtt.fsm.bad_protocol_level").passed is False

        state = plugin.probe_state(host, port, target, None)
        assert _by_id(state, "mqtt.state.ping").passed is False
        assert _by_id(state, "mqtt.state.unsubscribe").passed is False

        payload = plugin.probe_payload(host, port, target, None)
        assert _by_id(payload, "mqtt.payload.pubsub_echo").passed is False
    finally:
        stop.set()
        th.join(timeout=2.0)


def test_mqtt_probe_negotiation_fails_without_connack() -> None:
    def handler(conn: socket.socket) -> None:
        conn.recv(256)
        conn.sendall(b"\x00\x00\x00\x00")

    srv, host, port, stop, th = _start_tcp_stub(handler)
    try:
        target = TargetSpec(
            name="mqtt-stub", host=host, port=port, protocol="mqtt", protocols=["mqtt"]
        )
        plugin = MQTTPlugin()
        checks = plugin.probe_negotiation(host, port, target, None)
        assert _by_id(checks, "mqtt.nego.connack").passed is False
    finally:
        stop.set()
        th.join(timeout=2.0)
