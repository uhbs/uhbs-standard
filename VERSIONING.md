# Versioning Policy

UHBS uses [Semantic Versioning](https://semver.org/) for the **specification** and
the **Python package** (`uhbs` / `uhbs_core`), which share version **4.5.2** until
a future split is RFCd.

| Change type | Version bump | Examples |
| --- | --- | --- |
| Breaking normative change | MAJOR | UHQS formula change; remove profile class; weaken δ_C |
| Backward-compatible normative add | MINOR | New optional TPS field; new protocol plugin API |
| Clarifications, fixtures, docs, bugfixes | PATCH | Typo, schema description, harness bug that restores documented behavior |

## Rules

1. Spec docs, schemas, and `uhbs_core` math **MUST** ship in the same tagged release.
2. Accepted RFCs that change normative text **MUST** bump the version accordingly.
3. GitHub Releases **SHOULD** list normative vs informative changes separately.
4. Signed tags (`git tag -s`) are **RECOMMENDED** for MAJOR/MINOR cuts.

## Single source of truth

The canonical version string is ``src/uhbs_core/_version.py`` (``__version__``).

- ``pyproject.toml`` reads it via setuptools ``dynamic`` version.
- ``uhbs_cli`` / ``uhbs_mcp`` import ``uhbs_core.__version__`` (do not assign a second literal).
- Schemas, fixtures, docs, Docker tags, and discovery files are **mirrors** — update them with::

      python scripts/bump_version.py X.Y.Z
      python scripts/bump_version.py --check

