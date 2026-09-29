"""PPTP protocol plugin + offline stub probes."""

from __future__ import annotations

import socket
import struct
import threading

from uhbs_core.models import TargetSpec
from uhbs_core.protocols import get_plugin
from uhbs_core.protocols.pptp import (
    PPTP_MAGIC,
    PPTP_MSG_CONTROL,
    PPTP_SCCRP,
    PPTPPlugin,
    build_outgoing_call_request,
    build_start_control_connection_request,
    is_pptp_control,
    is_sccrp,
)
from uhbs_core.protocols.registry import register


def _ensure_registered() -> None:
    register(PPTPPlugin())


def test_pptp_plugin_resolves() -> None:
    _ensure_registered()
    p = get_plugin("pptp")
    assert isinstance(p, PPTPPlugin)
    assert get_plugin("pptp-vpn").name == "pptp"


def test_sccrq_framing() -> None:
    pkt = build_start_control_connection_request(hostname="uhbs", vendor="UHBS")
    assert len(pkt) == 156
    length, msg, magic, ctrl = struct.unpack_from("!HHIH", pkt, 0)
    assert length == 156
    assert msg == PPTP_MSG_CONTROL
    assert magic == PPTP_MAGIC
    assert ctrl == 1
    assert b"uhbs" in pkt


def test_ocrq_and_parsers() -> None:
    ocrq = build_outgoing_call_request()
    assert len(ocrq) == 168
    assert is_pptp_control(ocrq, control_type=7)
    sccrp = struct.pack("!HHIHH", 156, 1, PPTP_MAGIC, PPTP_SCCRP, 0) + b"\x00" * 144
    assert is_sccrp(sccrp)
    assert not is_sccrp(b"\x00" * 12)


def test_pptp_unreachable_does_not_raise() -> None:
    _ensure_registered()
    plugin = get_plugin("pptp")
    target = TargetSpec(
        name="x",
        host="127.0.0.1",
        port=1,
        protocol="pptp",
        protocols=["pptp"],
    )
    for probe in (plugin.probe_fsm, plugin.probe_negotiation, plugin.probe_state):
        checks = probe("127.0.0.1", 1, target, None)
        assert isinstance(checks, list)
        assert checks


def _serve_pptp() -> tuple[str, int, threading.Event, socket.socket]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    host, port = srv.getsockname()
    stop = threading.Event()

    def _loop() -> None:
        srv.settimeout(0.5)
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except TimeoutError:
                continue
            with conn:
                conn.settimeout(2.0)
                try:
                    data = conn.recv(4096)
                except TimeoutError:
                    data = b""
                if len(data) >= 12:
                    _l, msg, magic, ctrl = struct.unpack_from("!HHIH", data, 0)
                    if magic == PPTP_MAGIC and ctrl == 1:
                        # Minimal SCCRP (156 octets) + tiny Outgoing-Call-Reply.
                        sccrp = (
                            struct.pack(
                                "!HHIHH",
                                156,
                                PPTP_MSG_CONTROL,
                                PPTP_MAGIC,
                                PPTP_SCCRP,
                                0,
                            )
                            + b"\x00" * 144
                        )
                        ocrp = struct.pack(
                            "!HHIHH", 32, PPTP_MSG_CONTROL, PPTP_MAGIC, 8, 0
                        ) + b"\x00" * 20
                        conn.sendall(sccrp + ocrp)
        srv.close()

    threading.Thread(target=_loop, daemon=True).start()
    return host, port, stop, srv


def test_pptp_live_stub() -> None:
    _ensure_registered()
    host, port, stop, srv = _serve_pptp()
    try:
        plugin = PPTPPlugin()
        target = TargetSpec(
            name="stub",
            host=host,
            port=port,
            protocol="pptp",
            protocols=["pptp"],
        )
        nego = plugin.probe_negotiation(host, port, target, None)
        assert nego[0].passed
        assert nego[0].score == 100.0
        state = plugin.probe_state(host, port, target, None)
        assert state[0].score >= 70.0
    finally:
        stop.set()
        srv.close()
