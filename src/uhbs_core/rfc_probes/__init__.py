"""RFC-aligned protocol probes for UHBS lab grading (SSH / SMTP / POP3 / HTTP).

Package layout keeps each protocol suite in its own module while preserving the
historical ``uhbs_core.rfc_probes`` import path.
"""
from __future__ import annotations

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
from .types import ProtoPorts, RFCSuiteResult

__all__ = [
    "ProtoPorts",
    "RFCSuiteResult",
    "aggregate_rfc_score",
    "probe_http_rfc9110",
    "probe_pop3_rfc1939",
    "probe_smtp_rfc5321",
    "probe_ssh_rfc4253",
    "run_rfc_suites",
]
