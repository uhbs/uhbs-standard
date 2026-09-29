"""Telnet RFC 854 suite — scoring contract and independence checks."""

from __future__ import annotations

import contextlib
import socket
import threading

from uhbs_core.contract_validation import validate_check_result
from uhbs_core.models import TargetSpec
from uhbs_core.protocols.telnet import TelnetPlugin
from uhbs_core.rfc_probes import clear_suite_cache
from uhbs_core.rfc_probes.telnet import DO, IAC, WILL, probe_telnet_rfc854


def _serve_telnet(*, with_iac: bool = True, login: bool = True) -> tuple[str, int, threading.Event]:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)
    host, port = srv.getsockname()
    stop = threading.Event()

    def _banner() -> bytes:
        out = bytearray()
        if with_iac:
            out += bytes([IAC, WILL, 1, IAC, DO, 3])
        if login:
            out += b"\r\nlogin: "
        elif with_iac:
            out += b"\r\n"
        else:
            out += b"Hello from echo\r\n"
        return bytes(out)

    def _handle(conn: socket.socket) -> None:
        conn.settimeout(2.0)
        try:
            conn.sendall(_banner())
            with contextlib.suppress(TimeoutError):
                conn.recv(1024)
            # Optional post-nego text
            if login:
                conn.sendall(b"password: ")
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
    return host, port, stop


def test_telnet_suite_against_iac_login_stub() -> None:
    clear_suite_cache()
    host, port, stop = _serve_telnet(with_iac=True, login=True)
    try:
        suite = probe_telnet_rfc854(host, port)
        assert suite.skipped is False
        assert len(suite.checks) == 10
        by_id = {c.id: c for c in suite.checks}
        assert by_id["telnet.fsm.iac_negotiation"].passed is True
        assert by_id["telnet.fsm.option_verb"].passed is True
        assert by_id["telnet.nego.second_connection_independent"].passed is True
        assert by_id["telnet.state.login_prompt"].passed is True
        assert by_id["telnet.nego.connect_recv"].passed is True
        for c in suite.checks:
            assert validate_check_result(c) == [], (c.id, c.passed, c.score, c.detail)

        plugin = TelnetPlugin()
        target = TargetSpec(
            name="tn", host=host, port=port, protocol="telnet", protocols=["telnet"]
        )
        fsm = plugin.probe_fsm(host, port, target, None)
        nego = plugin.probe_negotiation(host, port, target, None)
        state = plugin.probe_state(host, port, target, None)
        assert all(c.id.startswith("telnet.fsm.") for c in fsm)
        assert all(c.id.startswith("telnet.nego.") for c in nego)
        assert [c.id for c in state] == ["telnet.state.login_prompt"]
        # No double-count of login_prompt in A2
        assert not any("login_prompt" in c.id for c in nego)
    finally:
        stop.set()


def test_telnet_no_iac_fails_option_verb_without_pass_at_zero() -> None:
    clear_suite_cache()
    host, port, stop = _serve_telnet(with_iac=False, login=False)
    try:
        suite = probe_telnet_rfc854(host, port)
        by_id = {c.id: c for c in suite.checks}
        iac = by_id["telnet.fsm.iac_negotiation"]
        opt = by_id["telnet.fsm.option_verb"]
        assert iac.passed is False
        assert opt.passed is False
        assert opt.score == 0.0
        for c in suite.checks:
            assert validate_check_result(c) == [], (c.id, c.passed, c.score)
    finally:
        stop.set()
