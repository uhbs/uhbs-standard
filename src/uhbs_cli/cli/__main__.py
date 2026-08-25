"""Allow ``python -m uhbs_cli.cli`` (same entry as the ``uhbs`` console script)."""

from __future__ import annotations

from uhbs_cli.cli import main

if __name__ == "__main__":
    main()
