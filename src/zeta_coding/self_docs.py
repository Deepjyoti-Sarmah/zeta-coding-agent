"""Locations of Zeta's packaged self-documentation and examples."""

from __future__ import annotations

from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_DATA_ROOT = _PACKAGE_ROOT / "data"


def zeta_readme_path() -> Path:
    """Return the installed overview document for Zeta-aware tasks."""
    return _DATA_ROOT / "docs" / "README.md"


def zeta_docs_path() -> Path:
    """Return the installed Zeta self-documentation directory."""
    return _DATA_ROOT / "docs"


def zeta_examples_path() -> Path:
    """Return the installed Zeta example directory."""
    return _DATA_ROOT / "examples"
