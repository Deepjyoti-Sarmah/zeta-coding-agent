"""Persistent cache for explicitly refreshed provider model catalogs."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps, loads
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time
from typing import Literal

from zeta_coding.paths import ZetaPaths

CACHE_SCHEMA_VERSION = 1
ProviderStatus = Literal["ready", "login_required", "offline", "error"]
CatalogSource = Literal["live", "cached", "static"]


@dataclass(frozen=True, slots=True)
class ProviderModelCatalog:
    """The latest known model list and availability state for one provider."""

    provider: str
    models: tuple[str, ...] = ()
    status: ProviderStatus = "error"
    source: CatalogSource = "static"
    refreshed_at: float | None = None
    message: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "models": list(self.models),
            "status": self.status,
            "source": self.source,
            "refreshed_at": self.refreshed_at,
            "message": self.message,
        }


class ModelCatalogCacheError(ValueError):
    """Raised when the persisted model catalog cache is invalid."""


class ModelCatalogCache:
    """Atomically read and write model catalogs under the Zeta home directory."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or model_catalog_cache_path()

    def load(self) -> dict[str, ProviderModelCatalog]:
        if not self.path.exists():
            return {}
        try:
            raw = loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ModelCatalogCacheError(f"Could not read model catalog cache: {exc}") from exc
        if not isinstance(raw, dict) or raw.get("schema_version") != CACHE_SCHEMA_VERSION:
            raise ModelCatalogCacheError("Unsupported model catalog cache format")
        providers = raw.get("providers")
        if not isinstance(providers, dict):
            raise ModelCatalogCacheError("Model catalog cache providers must be an object")
        return {
            name: _catalog_from_json(name, value)
            for name, value in providers.items()
            if isinstance(name, str)
        }

    def save(self, catalogs: dict[str, ProviderModelCatalog]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = dumps(
            {
                "schema_version": CACHE_SCHEMA_VERSION,
                "providers": {name: catalog.to_json() for name, catalog in catalogs.items()},
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                temporary_path.chmod(0o600)
                handle.write(content)
                handle.flush()
            temporary_path.replace(self.path)
            self.path.chmod(0o600)
        except OSError as exc:
            raise ModelCatalogCacheError(f"Could not write model catalog cache: {exc}") from exc
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
        return self.path


def model_catalog_cache_path(paths: ZetaPaths | None = None) -> Path:
    """Return the persistent model discovery cache path."""
    return (paths or ZetaPaths()).home / "model-catalog.json"


def live_catalog(
    provider: str,
    models: tuple[str, ...],
    *,
    status: ProviderStatus = "ready",
    message: str | None = None,
) -> ProviderModelCatalog:
    """Build a catalog entry produced by a successful explicit refresh."""
    return ProviderModelCatalog(
        provider=provider,
        models=tuple(dict.fromkeys(models)),
        status=status,
        source="live",
        refreshed_at=time(),
        message=message,
    )


def _catalog_from_json(name: str, value: object) -> ProviderModelCatalog:
    if not isinstance(value, dict):
        raise ModelCatalogCacheError(f"Invalid model catalog entry: {name}")
    models = value.get("models", [])
    status = value.get("status", "error")
    source = value.get("source", "cached")
    refreshed_at = value.get("refreshed_at")
    message = value.get("message")
    if (
        not isinstance(models, list)
        or not all(isinstance(model, str) and model for model in models)
        or status not in {"ready", "login_required", "offline", "error"}
        or source not in {"live", "cached", "static"}
        or (refreshed_at is not None and not isinstance(refreshed_at, (int, float)))
        or (message is not None and not isinstance(message, str))
    ):
        raise ModelCatalogCacheError(f"Invalid model catalog entry: {name}")
    return ProviderModelCatalog(
        provider=name,
        models=tuple(dict.fromkeys(models)),
        status=status,
        source=source,
        refreshed_at=float(refreshed_at) if refreshed_at is not None else None,
        message=message,
    )
