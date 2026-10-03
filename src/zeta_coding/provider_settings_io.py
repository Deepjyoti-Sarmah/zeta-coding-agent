"""Persistence primitives for provider settings."""

from __future__ import annotations

from collections.abc import Callable
from os import replace
from pathlib import Path
from contextlib import suppress
from shutil import copy2
from typing import Any

from zeta_coding.paths import ZetaPaths


def settings_path(paths: ZetaPaths | None = None) -> Path:
    """Return the durable provider settings path."""
    return (paths or ZetaPaths()).home / "providers.json"


def atomic_write_text(path: Path, content: str) -> None:
    """Write text through a sibling temporary file and replace the target."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    replace(temporary, path)


def load_settings(
    path: Path,
    *,
    missing: Callable[[], Any],
    parse: Callable[[dict[str, Any]], Any],
    merge_builtins: Callable[[Any], Any],
    invalid_message: str,
) -> Any:
    """Load JSON settings while keeping provider-specific parsing outside this module."""
    if not path.exists():
        return missing()
    import json

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(invalid_message)
    return merge_builtins(parse(raw))


def save_settings(
    settings: Any,
    path: Path,
    *,
    persist_catalog: Callable[[], None],
    serialize: Callable[[Any], str],
) -> Path:
    """Persist settings with a backup and atomic replacement."""
    persist_catalog()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with suppress(OSError):
            copy2(path, path.with_suffix(path.suffix + ".bak"))
    atomic_write_text(path, serialize(settings))
    return path
