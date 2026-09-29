"""RFC-aligned protocol probes for UHBS lab grading.

Named suites target ~10 checks each (SSH is the deep outlier at 20).

Included: SSH (RFC 4253), SMTP (5321), POP3 (1939), HTTP (9110/9112),
FTP (959), Telnet (854). IMAP's suite lives on the IMAP plugin module.
DNS / Redis / MySQL / Postgres expand Module A on their protocol plugins
(not separate rfc_probes modules).

Skipped / unique (thin plugin checks only — ICS, proprietary, or non-IETF):
modbus, s7comm, bacnet, bluetooth, pjl, mcp, kafka, elasticsearch, oracle,
mssql, socks5, rdp, vnc, smb, generic.
"""
from __future__ import annotations

from .cache import clear_suite_cache
from .ftp import probe_ftp_rfc959
from .http_probe import probe_http_rfc9110
from .pop3 import _pop3_status as _pop3_status
from .pop3 import probe_pop3_rfc1939
from .smtp import _smtp_codes as _smtp_codes
from .smtp import probe_smtp_rfc5321
from .socket_util import _port_open as _port_open
from .socket_util import _recv_some as _recv_some
from .socket_util import _transact as _transact
from .ssh import probe_ssh_rfc4253
from .suite import aggregate_rfc_score, run_rfc_suites
from .telnet import probe_telnet_rfc854
from .types import ProtoPorts, RFCSuiteResult

__all__ = [
    "ProtoPorts",
    "RFCSuiteResult",
    "aggregate_rfc_score",
    "clear_suite_cache",
    "probe_ftp_rfc959",
    "probe_http_rfc9110",
    "probe_pop3_rfc1939",
    "probe_smtp_rfc5321",
    "probe_ssh_rfc4253",
    "probe_telnet_rfc854",
    "run_rfc_suites",
]
