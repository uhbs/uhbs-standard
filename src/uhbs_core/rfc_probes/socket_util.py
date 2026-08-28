"""Low-level TCP helpers for RFC protocol probes."""
from __future__ import annotations

import socket
import time


def _recv_some(sock: socket.socket, timeout: float = 3.0, max_bytes: int = 65535) -> bytes:
    sock.settimeout(timeout)
    chunks: list[bytes] = []
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
            if sum(len(c) for c in chunks) >= max_bytes:
                break
            # short linger for pipelined banners
            sock.settimeout(0.35)
    except TimeoutError:
        pass
    return b"".join(chunks)


def _transact(
    host: str,
    port: int,
    payload: bytes,
    *,
    timeout: float = 4.0,
    recv_first: bool = False,
) -> tuple[bytes, float, str]:
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            banner = b""
            if recv_first:
                banner = _recv_some(s, timeout=timeout)
            if payload:
                s.sendall(payload)
            body = _recv_some(s, timeout=timeout)
            return banner + body, (time.perf_counter() - t0) * 1000.0, ""
    except OSError as exc:
        return b"", (time.perf_counter() - t0) * 1000.0, str(exc)


def _port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

