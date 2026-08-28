"""Module F — Source Code & Static Security Audit (White-Box / D1+D4).

1. Static fingerprint & artifact scanning (keys, banners, seeds, MACs)
2. LLM prompt & guardrail boundary audit
3. SAST & supply chain (Bandit / Semgrep / Trivy when installed)
4. VFS / POSIX command coverage against simulated shell surface
"""
from __future__ import annotations

from .runner import main, run

__all__ = ["main", "run"]

if __name__ == "__main__":
    raise SystemExit(main())
