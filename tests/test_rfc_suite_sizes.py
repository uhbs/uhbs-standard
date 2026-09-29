"""Assert named RFC Module A suites expose the expected check counts."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from uhbs_core.protocols.imap import probe_imap_rfc3501
from uhbs_core.rfc_probes import clear_suite_cache
from uhbs_core.rfc_probes.ftp import probe_ftp_rfc959
from uhbs_core.rfc_probes.http_probe import probe_http_rfc9110
from uhbs_core.rfc_probes.pop3 import probe_pop3_rfc1939
from uhbs_core.rfc_probes.smtp import probe_smtp_rfc5321
from uhbs_core.rfc_probes.ssh import probe_ssh_rfc4253
from uhbs_core.rfc_probes.telnet import probe_telnet_rfc854

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _clear_rfc_cache() -> None:
    clear_suite_cache()
    yield
    clear_suite_cache()


@pytest.mark.parametrize(
    ("name", "path", "expected", "pattern"),
    [
        # Capture check id; unique-count so try/except duplicate branches don't inflate.
        ("ssh", "src/uhbs_core/rfc_probes/ssh.py", 20, r'_chk\(\s*"(rfc4253\.[^"]+)"'),
        ("http", "src/uhbs_core/rfc_probes/http_probe.py", 10, r'id="(rfc911[02]\.[^"]+)"'),
        ("smtp", "src/uhbs_core/rfc_probes/smtp.py", 10, r'id="(rfc5321\.[^"]+)"'),
        ("pop3", "src/uhbs_core/rfc_probes/pop3.py", 10, r'id="(rfc1939\.[^"]+)"'),
        ("ftp", "src/uhbs_core/rfc_probes/ftp.py", 10, r'id="(ftp\.(?:fsm|nego)\.[^"]+)"'),
        (
            "telnet",
            "src/uhbs_core/rfc_probes/telnet.py",
            10,
            r'id="(telnet\.(?:fsm|nego|state)\.[^"]+)"',
        ),
        ("imap", "src/uhbs_core/protocols/imap.py", 10, r'id="(rfc3501\.[^"]+)"'),
        ("dns", "src/uhbs_core/protocols/dns.py", 10, r'id="(dns\.(?:fsm|nego)\.[^"]+)"'),
        ("redis", "src/uhbs_core/protocols/redis.py", 10, r'id="(redis\.(?:fsm|nego)\.[^"]+)"'),
        ("mysql", "src/uhbs_core/protocols/mysql.py", 10, r'id="(mysql\.(?:fsm|nego)\.[^"]+)"'),
        (
            "postgres",
            "src/uhbs_core/protocols/postgres.py",
            10,
            r'id="(postgres\.(?:fsm|nego)\.[^"]+)"',
        ),
    ],
)
def test_rfc_suite_static_check_count(
    name: str, path: str, expected: int, pattern: str
) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    ids = set(re.findall(pattern, text))
    assert len(ids) == expected, (
        f"{name}: expected {expected} unique checks, found {len(ids)}: {sorted(ids)}"
    )


def test_rfc_suite_closed_port_skips_without_raising() -> None:
    for probe in (
        probe_http_rfc9110,
        probe_smtp_rfc5321,
        probe_pop3_rfc1939,
        probe_ftp_rfc959,
        probe_imap_rfc3501,
        probe_ssh_rfc4253,
        probe_telnet_rfc854,
    ):
        suite = probe("127.0.0.1", 1)
        assert suite.skipped is True
        assert suite.checks == []


def test_telnet_suite_cached_across_calls() -> None:
    """fsm/nego/state must not re-open the full suite on every hook."""
    from uhbs_core.rfc_probes import cache as cache_mod

    clear_suite_cache()
    # Port 1 is closed — factory still runs once; second call hits cache.
    s1 = probe_telnet_rfc854("127.0.0.1", 1)
    assert s1.skipped is True
    with cache_mod._lock:
        keys = [k for k in cache_mod._store if k[0] == "telnet_rfc854"]
    assert len(keys) == 1
    s2 = probe_telnet_rfc854("127.0.0.1", 1)
    assert s2.skipped is True
    with cache_mod._lock:
        assert len([k for k in cache_mod._store if k[0] == "telnet_rfc854"]) == 1
