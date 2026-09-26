#!/usr/bin/env python3
"""UHBS lab entry: MockSSH Cisco example on 0.0.0.0:2222 (testadmin/x)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import MockSSH
from twisted.python import log

EXAMPLE = Path(__file__).resolve().parent / "examples" / "mock_cisco.py"
spec = importlib.util.spec_from_file_location("mock_cisco", EXAMPLE)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {EXAMPLE}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main() -> None:
    log.startLogging(sys.stderr)
    MockSSH.runServer(
        mod.commands,
        prompt="hostname>",
        interface="0.0.0.0",
        port=2222,
        **{"testadmin": "x"},
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
