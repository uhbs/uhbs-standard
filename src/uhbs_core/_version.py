"""UHBS package / spec version — single source of truth.

Bump with::

    python scripts/bump_version.py X.Y.Z

Do not duplicate this string in Python packages; import ``__version__`` instead.
Static mirrors (schemas, docs, Docker tags, fixtures) are updated by the bump
script — never edit ``web/package-lock.json`` as part of a version bump.
"""

from __future__ import annotations

__version__ = "4.5.2"
