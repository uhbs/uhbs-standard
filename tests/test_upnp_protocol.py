"""UPnP / SSDP protocol plugin + offline stub probes."""

from __future__ import annotations

import socket
import threading

from uhbs_core.models import TargetSpec
from uhbs_core.protocols import get_plugin
from uhbs_core.protocols.registry import register
from uhbs_core.protocols.upnp import (
    UPnPPlugin,
    build_msearch,
    is_ssdp_ok_reply,
)


def _ensure_registered() -> None:
    register(UPnPPlugin())


def test_upnp_plugin_resolves() -> None:
    _ensure_registered()
    p = get_plugin("upnp")
    assert isinstance(p, UPnPPlugin)
    assert get_plugin("ssdp").name == "upnp"


def test_msearch_and_reply_parsers() -> None:
    pkt = build_msearch(st="upnp:rootdevice")
    assert pkt.startswith(b"M-SEARCH * HTTP/1.1\r\n")
    assert b"ST: upnp:rootdevice\r\n" in pkt
    assert is_ssdp_ok_reply(
        b"HTTP/1.1 200 OK\r\n"
        b"CACHE-CONTROL: max-age=120\r\n"
        b"ST: upnp:rootdevice\r\n"
        b"SERVER: Linux/2.6 UPnP/1.0\r\n"
        b"\r\n"
    )
    assert not is_ssdp_ok_reply(b"HTTP/1.1 400 Bad Request\r\n\r\n")
    assert not is_ssdp_ok_reply(b"")


def test_upnp_unreachable_does_not_raise() -> None:
    _ensure_registered()
    plugin = get_plugin("upnp")
    target = TargetSpec(
        name="x",
        host="127.0.0.1",
        port=1,
        protocol="upnp",
        protocols=["upnp"],
    )
    for probe in (plugin.probe_fsm, plugin.probe_negotiation, plugin.probe_state):
        checks = probe("127.0.0.1", 1, target, None)
        assert isinstance(checks, list)
        assert checks


def _serve_ssdp() -> tuple[str, int, threading.Event, socket.socket]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.bind(("127.0.0.1", 0))
    host, port = srv.getsockname()
    stop = threading.Event()

    def _loop() -> None:
        srv.settimeout(0.5)
        while not stop.is_set():
            try:
                data, addr = srv.recvfrom(65535)
            except TimeoutError:
                continue
            if data.upper().startswith(b"M-SEARCH"):
                resp = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"CACHE-CONTROL: max-age=120\r\n"
                    b"ST: upnp:rootdevice\r\n"
                    b"USN: uuid:uhbs-test::upnp:rootdevice\r\n"
                    b"SERVER: UHBS-Test/1.0 UPnP/1.0\r\n"
                    b"LOCATION: http://127.0.0.1:49152/desc.xml\r\n"
                    b"\r\n"
                )
                srv.sendto(resp, addr)
        srv.close()

    threading.Thread(target=_loop, daemon=True).start()
    return host, port, stop, srv


def test_upnp_live_stub() -> None:
    _ensure_registered()
    host, port, stop, srv = _serve_ssdp()
    try:
        plugin = UPnPPlugin()
        target = TargetSpec(
            name="stub",
            host=host,
            port=port,
            protocol="upnp",
            protocols=["upnp"],
        )
        nego = plugin.probe_negotiation(host, port, target, None)
        assert nego[0].score == 100.0
        state = plugin.probe_state(host, port, target, None)
        assert state[0].score == 100.0
        fsm = plugin.probe_fsm(host, port, target, None)
        assert fsm[0].score >= 70.0
    finally:
        stop.set()
        srv.close()
