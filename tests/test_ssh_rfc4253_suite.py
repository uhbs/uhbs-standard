"""Unit tests for expanded SSH RFC 4253 basic probe suite (~20 checks)."""

from __future__ import annotations

import contextlib
import socket
import threading

import pytest

from uhbs_core.rfc_probes.ssh import probe_ssh_rfc4253


def _fake_ssh_server(banner: bytes = b"SSH-2.0-OpenSSH_9.2p1 Test\r\n"):
    """Minimal listener: send banner, then a tiny fake KEXINIT-shaped packet."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(20)
    port = srv.getsockname()[1]
    stop = threading.Event()

    def _serve() -> None:
        srv.settimeout(0.3)
        while not stop.is_set():
            try:
                conn, _addr = srv.accept()
            except TimeoutError:
                continue
            except OSError:
                break
            with conn:
                try:
                    conn.settimeout(1.0)
                    conn.sendall(banner)
                    with contextlib.suppress(OSError):
                        conn.recv(4096)
                    # packet_length=12, padding_length=0, msg_type=20 (KEXINIT)
                    pkt = (12).to_bytes(4, "big") + bytes([0, 20]) + b"\x00" * 10
                    conn.sendall(pkt)
                except OSError:
                    pass

    th = threading.Thread(target=_serve, daemon=True)
    th.start()
    return srv, port, stop, th


@pytest.fixture()
def ssh_endpoint():
    srv, port, stop, th = _fake_ssh_server()
    try:
        yield "127.0.0.1", port
    finally:
        stop.set()
        with contextlib.suppress(OSError):
            srv.close()
        th.join(timeout=2.0)


def test_ssh_rfc4253_suite_has_twenty_checks(ssh_endpoint) -> None:
    host, port = ssh_endpoint
    suite = probe_ssh_rfc4253(host, port)
    assert not suite.skipped
    assert len(suite.checks) == 20
    ids = [c.id for c in suite.checks]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("rfc4253.") for i in ids)
    for required in (
        "rfc4253.identification_crlf",
        "rfc4253.kexinit_after_id",
        "rfc4253.legacy_version_handling",
        "rfc4253.reject_null_in_id",
        "rfc4253.reject_oversized_client_id",
        "rfc4253.second_connection_independent",
    ):
        assert required in ids


def test_ssh_rfc4253_closed_port_skips() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    suite = probe_ssh_rfc4253("127.0.0.1", port)
    assert suite.skipped is True
    assert suite.checks == []
