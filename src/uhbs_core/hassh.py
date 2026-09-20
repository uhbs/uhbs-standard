"""Minimal SSH server HASSH-like fingerprint from KEXINIT (RFC 4253)."""

from __future__ import annotations

import hashlib
import socket
import struct

# Legacy / weak algorithm name markers (substring match, case-sensitive SSH ids).
_WEAK_KEX = (
    "diffie-hellman-group1-sha1",
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group-exchange-sha1",
)
_WEAK_ENC = (
    "3des-cbc",
    "blowfish-cbc",
    "cast128-cbc",
    "arcfour",
    "arcfour128",
    "arcfour256",
)
_WEAK_MAC = (
    "hmac-md5",
    "hmac-md5-96",
    "hmac-sha1-96",
    "hmac-ripemd160",
)


def classify_ssh_algorithms(algo: str) -> dict[str, list[str]]:
    """Classify a HASSH algorithm string for weak KEX/cipher/MAC offers.

    ``algo`` uses the HASSH layout ``kex;enc_c2s;mac_c2s;comp_c2s`` (comma-
    separated name-lists inside each field).
    """
    parts = (algo or "").split(";")
    kex = parts[0].split(",") if parts else []
    enc = parts[1].split(",") if len(parts) > 1 else []
    mac = parts[2].split(",") if len(parts) > 2 else []
    weak: list[str] = []
    for name in kex:
        n = name.strip()
        if n and any(n == w or n.startswith(w) for w in _WEAK_KEX):
            weak.append(n)
    for name in enc:
        n = name.strip()
        if n and any(n == w or n.startswith(w) for w in _WEAK_ENC):
            weak.append(n)
    for name in mac:
        n = name.strip()
        if n and any(n == w or n.startswith(w) for w in _WEAK_MAC):
            weak.append(n)
    return {
        "weak": weak,
        "kex": [x for x in kex if x],
        "enc": [x for x in enc if x],
        "mac": [x for x in mac if x],
    }


def _read_name_list(buf: bytes, off: int) -> tuple[str, int]:
    if off + 4 > len(buf):
        return "", off
    (n,) = struct.unpack(">I", buf[off : off + 4])
    off += 4
    if off + n > len(buf):
        return "", off
    raw = buf[off : off + n].decode("ascii", errors="replace")
    return raw, off + n


def parse_server_hassh(host: str, port: int, timeout: float = 5.0) -> tuple[str, str, str]:
    """Return (hassh_md5, kex_algos, banner). Empty hassh on failure."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            banner = b""
            while b"\n" not in banner and len(banner) < 256:
                chunk = s.recv(64)
                if not chunk:
                    break
                banner += chunk
            # Client identification
            s.sendall(b"SSH-2.0-UHBS_HASSH_1.0\r\n")
            data = b""
            # Read until we likely have a full KEXINIT
            while len(data) < 1500:
                try:
                    chunk = s.recv(4096)
                except TimeoutError:
                    break
                if not chunk:
                    break
                data += chunk
                if len(data) > 64 and data[5:6] == b"\x14":
                    # may still need rest of packet
                    if len(data) >= 8:
                        plen = struct.unpack(">I", data[0:4])[0]
                        if len(data) >= 4 + plen:
                            break
    except OSError:
        return "", "", ""

    ban = banner.split(b"\n", 1)[0].decode("utf-8", "replace").strip()
    # Find SSH_MSG_KEXINIT (20) — may follow banner CR LF
    payload = data
    if b"\r\n" in data[:128]:
        payload = data.split(b"\r\n", 1)[1]
    # Walk binary packets for msg type 20
    off = 0
    body = b""
    while off + 6 <= len(payload):
        plen = struct.unpack(">I", payload[off : off + 4])[0]
        if plen < 2 or off + 4 + plen > len(payload) + 1024:
            # heuristic scan
            idx = payload.find(b"\x14", off)
            if idx < 0 or idx + 17 > len(payload):
                break
            body = payload[idx + 1 :]  # after msg type? actually msg at pad+1
            # Better: standard layout packet_len|pad_len|msg|...
            break
        pad = payload[off + 4]
        msg = payload[off + 5]
        if msg == 20:
            body = payload[off + 6 : off + 4 + plen]  # after msg type byte... wait
            # Structure: [4 plen][1 pad][1 msg=20][16 cookie][name-lists...]
            body = payload[off + 6 : off + 4 + plen]
            break
        off += 4 + plen

    if not body:
        # Fallback search for cookie+namelist pattern after 0x14
        idx = payload.find(b"\x14")
        if idx >= 0 and idx + 17 < len(payload):
            body = payload[idx + 1 :]
        else:
            return "", "", ban

    # body starts at cookie (16) if we stripped msg byte; if body includes cookie after msg
    # Our body = after msg type → cookie at [0:16]
    if len(body) < 20:
        return "", "", ban
    o = 16  # skip cookie
    kex, o = _read_name_list(body, o)
    _hostkey, o = _read_name_list(body, o)
    enc_c2s, o = _read_name_list(body, o)
    _enc_s2c, o = _read_name_list(body, o)
    mac_c2s, o = _read_name_list(body, o)
    _mac_s2c, o = _read_name_list(body, o)
    comp_c2s, o = _read_name_list(body, o)
    if not kex:
        return "", "", ban
    # Server HASSH set: kex;enc_c2s;mac_c2s;comp_c2s (common convention)
    algo = f"{kex};{enc_c2s};{mac_c2s};{comp_c2s}"
    # HASSH specifies MD5 as a wire-compatible identifier. It is not used
    # for signatures, passwords, integrity, or any other security decision.
    hassh = hashlib.md5(
        algo.encode("utf-8"), usedforsecurity=False
    ).hexdigest()  # NOSONAR
    return hassh, algo, ban
