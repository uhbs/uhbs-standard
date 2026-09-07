"""MQTT honeypot grading plugin — Module A/B fidelity beyond CONNECT stubs.

Focus: discriminate shallow decoys (always-CONNACK) from brokers that look
real enough to engage (FSM refusals, PING, unsubscribe, pub/sub delivery).
MQTT 3.1.1 over TCP; ``mqtts`` is an alias for the same plugin.
"""

from __future__ import annotations

import socket
import struct
import time

from uhbs_core.models import CheckResult, TargetSpec
from uhbs_core.protocols.base import ProtocolPlugin
from uhbs_core.tps import TPS


def _ot_timeout(tps: TPS | None, default: float = 3.0) -> float:
    if tps and isinstance(tps.raw, dict):
        for block in (tps.raw.get("performance_baseline"), tps.raw.get("experimental"), tps.raw):
            if isinstance(block, dict) and "probe_timeout_sec" in block:
                try:
                    return float(block["probe_timeout_sec"])
                except (TypeError, ValueError):
                    pass
    return default


def _encode_remaining_length(n: int) -> bytes:
    out = bytearray()
    while True:
        digit = n % 128
        n //= 128
        if n > 0:
            digit |= 0x80
        out.append(digit)
        if n == 0:
            break
    return bytes(out)


def build_connect(
    client_id: str = "uhbs",
    *,
    protocol_name: bytes = b"MQTT",
    protocol_level: int = 4,
    clean_session: bool = True,
    keepalive: int = 60,
) -> bytes:
    """MQTT CONNECT (default 3.1.1 / protocol level 4)."""
    flags = 0x02 if clean_session else 0x00
    proto = (
        struct.pack("!H", len(protocol_name))
        + protocol_name
        + bytes([protocol_level & 0xFF, flags])
        + struct.pack("!H", keepalive)
    )
    cid = client_id.encode("utf-8")
    payload = proto + struct.pack("!H", len(cid)) + cid
    return b"\x10" + _encode_remaining_length(len(payload)) + payload


def build_subscribe(topic: str = "uhbs/test", packet_id: int = 1, qos: int = 0) -> bytes:
    topic_b = topic.encode("utf-8")
    payload = (
        struct.pack("!H", packet_id)
        + struct.pack("!H", len(topic_b))
        + topic_b
        + bytes([qos & 0x03])
    )
    return b"\x82" + _encode_remaining_length(len(payload)) + payload


def build_unsubscribe(topic: str = "uhbs/test", packet_id: int = 2) -> bytes:
    topic_b = topic.encode("utf-8")
    payload = struct.pack("!H", packet_id) + struct.pack("!H", len(topic_b)) + topic_b
    return b"\xa2" + _encode_remaining_length(len(payload)) + payload


def build_publish(
    topic: str,
    payload: bytes = b"uhbs",
    *,
    qos: int = 0,
    retain: bool = False,
    dup: bool = False,
) -> bytes:
    flags = (qos & 0x03) << 1
    if retain:
        flags |= 0x01
    if dup:
        flags |= 0x08
    topic_b = topic.encode("utf-8")
    body = struct.pack("!H", len(topic_b)) + topic_b
    if qos > 0:
        body += b"\x00\x01"
    body += payload
    return bytes([0x30 | flags]) + _encode_remaining_length(len(body)) + body


def build_pingreq() -> bytes:
    return b"\xc0\x00"


def build_disconnect() -> bytes:
    return b"\xe0\x00"


def is_connack(raw: bytes) -> bool:
    return len(raw) >= 4 and raw[0] == 0x20 and raw[3] == 0x00


def connack_return_code(raw: bytes) -> int | None:
    if len(raw) >= 4 and raw[0] == 0x20:
        return raw[3]
    return None


def is_suback(raw: bytes) -> bool:
    return len(raw) >= 4 and raw[0] == 0x90


def is_unsuback(raw: bytes) -> bool:
    return len(raw) >= 4 and raw[0] == 0xB0


def is_pingresp(raw: bytes) -> bool:
    return len(raw) >= 2 and raw[0] == 0xD0


def is_publish(raw: bytes) -> bool:
    return len(raw) >= 4 and (raw[0] & 0xF0) == 0x30


def _recv_some(sock: socket.socket, max_bytes: int = 4096) -> bytes:
    try:
        return sock.recv(max_bytes)
    except TimeoutError:
        return b""


def _close(sock: socket.socket | None) -> None:
    if sock is None:
        return
    try:
        sock.close()
    except OSError:
        pass


def _open(host: str, port: int, timeout: float) -> socket.socket:
    sock = socket.create_connection((host, port), timeout=timeout)
    sock.settimeout(timeout)
    return sock


def _connect_session(
    host: str, port: int, timeout: float, client_id: str
) -> tuple[socket.socket | None, bytes, str]:
    """Open TCP, send CONNECT, return (sock|None, connack_raw, error)."""
    try:
        sock = _open(host, port, timeout)
    except OSError as exc:
        return None, b"", str(exc)
    try:
        sock.sendall(build_connect(client_id))
        raw = _recv_some(sock)
        if not is_connack(raw):
            _close(sock)
            return None, raw, f"no CONNACK (recv={raw[:12].hex() or 'empty'})"
        return sock, raw, ""
    except OSError as exc:
        _close(sock)
        return None, b"", str(exc)


class MQTTPlugin(ProtocolPlugin):
    name = "mqtt"
    families = ("iot", "ot", "messaging")

    def probe_fsm(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        checks: list[CheckResult] = []

        # 1) Illegal control packet type — must not hang the harness.
        ok = False
        detail = "no response"
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(b"\xff\x00")
                data = _recv_some(sock, 64)
                ok = True
                detail = f"illegal type response len={len(data)}"
        except TimeoutError:
            ok = True
            detail = "illegal type ignored/closed"
        except OSError as exc:
            ok = True
            detail = str(exc)
        checks.append(
            CheckResult(
                id="mqtt.fsm.illegal_type",
                team="red",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 20.0,
            )
        )

        # 2) PUBLISH before CONNECT — real brokers close/refuse; stubs often
        # return a fake CONNACK (shallow honeypot smell).
        ok = False
        detail = "unexpected accept"
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(build_publish("uhbs/preauth", b"x"))
                raw = _recv_some(sock, 64)
                if is_connack(raw):
                    detail = "CONNACK without CONNECT (stub-like)"
                    ok = False
                elif is_publish(raw):
                    detail = "PUBLISH echoed before session"
                    ok = False
                else:
                    ok = True
                    detail = (
                        f"pre-CONNECT PUBLISH rejected/closed "
                        f"recv={raw[:8].hex() or 'empty'}"
                    )
        except OSError as exc:
            ok = True
            detail = f"closed on pre-CONNECT PUBLISH ({exc})"
        checks.append(
            CheckResult(
                id="mqtt.fsm.publish_before_connect",
                team="red",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 25.0,
            )
        )

        # 3) Unacceptable protocol level — refuse (rc≠0) or close, not accept.
        ok = False
        detail = "accepted bad protocol level"
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(build_connect("uhbs-badver", protocol_level=99))
                raw = _recv_some(sock, 64)
                rc = connack_return_code(raw)
                if rc is None:
                    ok = True
                    detail = (
                        f"closed/no CONNACK for level=99 "
                        f"recv={raw[:8].hex() or 'empty'}"
                    )
                elif rc != 0:
                    ok = True
                    detail = f"CONNACK refused rc={rc}"
                else:
                    ok = False
                    detail = "CONNACK accepted protocol level 99"
        except OSError as exc:
            ok = True
            detail = f"closed on bad level ({exc})"
        checks.append(
            CheckResult(
                id="mqtt.fsm.bad_protocol_level",
                team="red",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 20.0,
            )
        )

        # 4) Truncated CONNECT — must not hang.
        ok = False
        detail = "hang/timeout"
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(b"\x10\x20\x00\x04MQTT")
                raw = _recv_some(sock, 64)
                ok = True
                detail = f"truncated CONNECT handled recv={raw[:8].hex() or 'empty'}"
        except OSError as exc:
            ok = True
            detail = str(exc)
        checks.append(
            CheckResult(
                id="mqtt.fsm.truncated_connect",
                team="red",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 20.0,
            )
        )
        return checks

    def probe_negotiation(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        strict = bool(tps and tps.strict_rfc_enforcement)
        checks: list[CheckResult] = []

        ok = False
        detail = "no CONNACK"
        raw = b""
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(build_connect("uhbs-nego"))
                raw = _recv_some(sock, 64)
                ok = is_connack(raw)
                detail = f"recv={raw[:8].hex()} ok={ok}"
        except OSError as exc:
            detail = str(exc)
        checks.append(
            CheckResult(
                id="mqtt.nego.connack",
                team="blue",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 0.0,
                critical=strict,
            )
        )

        framed = len(raw) >= 4 and raw[0] == 0x20 and raw[1] == 0x02
        checks.append(
            CheckResult(
                id="mqtt.nego.connack_framing",
                team="blue",
                passed=framed,
                detail=(
                    "CONNACK RL=2"
                    if framed
                    else f"unexpected framing {raw[:6].hex() or 'empty'}"
                ),
                score=100.0 if framed else 30.0,
            )
        )

        ok = False
        detail = "empty client-id mishandled"
        try:
            with _open(host, port, timeout) as sock:
                sock.sendall(build_connect("", clean_session=True))
                raw2 = _recv_some(sock, 64)
                rc = connack_return_code(raw2)
                if rc is None:
                    ok = True
                    detail = "closed/no CONNACK on empty client-id"
                else:
                    ok = True
                    detail = f"empty client-id CONNACK rc={rc}"
        except OSError as exc:
            ok = True
            detail = str(exc)
        checks.append(
            CheckResult(
                id="mqtt.nego.empty_client_id",
                team="blue",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 40.0,
            )
        )
        return checks

    def probe_state(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        timeout = _ot_timeout(tps)
        checks: list[CheckResult] = []

        ok = False
        detail = "session failed"
        sock, _, err = _connect_session(host, port, timeout, "uhbs-sub")
        if sock is None:
            detail = err or "CONNECT failed"
        else:
            try:
                sock.sendall(build_subscribe("uhbs/test", packet_id=1))
                suback = _recv_some(sock)
                ok = is_suback(suback)
                detail = f"suback={suback[:6].hex()} ok={ok}"
                sock.sendall(build_disconnect())
            except OSError as exc:
                detail = str(exc)
            finally:
                _close(sock)
        checks.append(
            CheckResult(
                id="mqtt.state.subscribe",
                team="blue",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 0.0,
                critical=True,
            )
        )

        ok = False
        detail = "no PINGRESP"
        sock, _, err = _connect_session(host, port, timeout, "uhbs-ping")
        if sock is None:
            detail = err or "CONNECT failed"
        else:
            try:
                sock.sendall(build_pingreq())
                resp = _recv_some(sock)
                ok = is_pingresp(resp)
                detail = f"pingresp={resp[:4].hex() or 'empty'} ok={ok}"
                sock.sendall(build_disconnect())
            except OSError as exc:
                detail = str(exc)
            finally:
                _close(sock)
        checks.append(
            CheckResult(
                id="mqtt.state.ping",
                team="blue",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 15.0,
            )
        )

        ok = False
        detail = "no UNSUBACK"
        sock, _, err = _connect_session(host, port, timeout, "uhbs-unsub")
        if sock is None:
            detail = err or "CONNECT failed"
        else:
            try:
                sock.sendall(build_subscribe("uhbs/unsub", packet_id=3))
                _recv_some(sock)
                sock.sendall(build_unsubscribe("uhbs/unsub", packet_id=4))
                resp = _recv_some(sock)
                ok = is_unsuback(resp)
                detail = f"unsuback={resp[:6].hex() or 'empty'} ok={ok}"
                sock.sendall(build_disconnect())
            except OSError as exc:
                detail = str(exc)
            finally:
                _close(sock)
        checks.append(
            CheckResult(
                id="mqtt.state.unsubscribe",
                team="blue",
                passed=ok,
                detail=detail,
                score=100.0 if ok else 20.0,
            )
        )
        return checks

    def probe_payload(
        self, host: str, port: int, target: TargetSpec, tps: TPS | None
    ) -> list[CheckResult]:
        """Pub/sub delivery across two clients — strongest shallow-stub discriminator."""
        timeout = _ot_timeout(tps)
        topic = "uhbs/echo"
        marker = b"uhbs-echo-marker"

        sub, _, err = _connect_session(host, port, timeout, "uhbs-echo-sub")
        if sub is None:
            return [
                CheckResult(
                    id="mqtt.payload.pubsub_echo",
                    team="red",
                    passed=False,
                    detail=err or "subscriber CONNECT failed",
                    score=0.0,
                    critical=True,
                )
            ]
        try:
            sub.sendall(build_subscribe(topic, packet_id=7))
            suback = _recv_some(sub)
            if not is_suback(suback):
                return [
                    CheckResult(
                        id="mqtt.payload.pubsub_echo",
                        team="red",
                        passed=False,
                        detail=(
                            "subscribe failed before publish "
                            f"suback={suback[:6].hex() or 'empty'}"
                        ),
                        score=10.0,
                        critical=True,
                    )
                ]

            pub, _, err2 = _connect_session(host, port, timeout, "uhbs-echo-pub")
            if pub is None:
                return [
                    CheckResult(
                        id="mqtt.payload.pubsub_echo",
                        team="red",
                        passed=False,
                        detail=err2 or "publisher CONNECT failed",
                        score=0.0,
                        critical=True,
                    )
                ]
            try:
                pub.sendall(build_publish(topic, marker, qos=0))
                time.sleep(0.05)
                deadline = time.time() + timeout
                got = b""
                while time.time() < deadline:
                    chunk = _recv_some(sub, 1024)
                    if chunk:
                        got += chunk
                        if is_publish(got) or marker in got:
                            break
                    else:
                        time.sleep(0.05)
                ok = is_publish(got) or marker in got
                return [
                    CheckResult(
                        id="mqtt.payload.pubsub_echo",
                        team="red",
                        passed=ok,
                        detail=(
                            f"delivered pub/sub echo ({len(got)}B)"
                            if ok
                            else "no PUBLISH delivered to subscriber (shallow stub?)"
                        ),
                        score=100.0 if ok else 10.0,
                        critical=True,
                        evidence=[got[:40].hex()],
                    )
                ]
            finally:
                try:
                    pub.sendall(build_disconnect())
                except OSError:
                    pass
                _close(pub)
        finally:
            try:
                sub.sendall(build_disconnect())
            except OSError:
                pass
            _close(sub)
