"""Universal Honeypot Benchmarking Standard CLI.

Public entry points used by the ``uhbs`` console script and tests:

- ``main`` — Click application group
- ``_schema_dir`` — schema path resolution (also used by uhbs_mcp)
"""

from __future__ import annotations

# Register command groups (side-effect imports)
from . import aep_cmds as aep_cmds  # noqa: F401
from . import aep_slm_cmds as aep_slm_cmds  # noqa: F401
from . import genai_bench_cmds as genai_bench_cmds  # noqa: F401
from . import matrix_cmds as matrix_cmds  # noqa: F401
from . import provenance_cmds as provenance_cmds  # noqa: F401
from .core import main
from .paths import ROOT, SCHEMA_DIR, _load_json, _load_schema, _load_yaml, _repo_root, _schema_dir

__all__ = [
    "ROOT",
    "SCHEMA_DIR",
    "_load_json",
    "_load_schema",
    "_load_yaml",
    "_repo_root",
    "_schema_dir",
    "main",
]
