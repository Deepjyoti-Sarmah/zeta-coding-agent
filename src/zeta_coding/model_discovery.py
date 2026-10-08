"""Explicit provider model discovery with static and cached fallbacks."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from os import environ
from typing import Any
from urllib.parse import urljoin

import httpx

from zeta_coding.credentials import FileCredentialStore
from zeta_coding.model_catalog_cache import (
    ModelCatalogCache,
    ProviderModelCatalog,
    live_catalog,
)
from zeta_coding.provider_config import (
    AnthropicProviderConfig,
    OpenAICodexProviderConfig,
    OpenAICompatibleProviderConfig,
    ProviderConfig,
)

_DISCOVERY_TIMEOUT_SECONDS = 8.0
_LOCAL_PROVIDER_NAMES = frozenset({"ollama", "lm-studio"})


@dataclass(frozen=True, slots=True)
class DiscoverySummary:
    """Result of refreshing all configured providers."""

    catalogs: tuple[ProviderModelCatalog, ...]
    cache_path: str

    @property
    def ready_count(self) -> int:
        return sum(catalog.status == "ready" for catalog in self.catalogs)

    @property
    def offline_count(self) -> int:
        return sum(catalog.status == "offline" for catalog in self.catalogs)

    @property
    def login_required_count(self) -> int:
        return sum(catalog.status == "login_required" for catalog in self.catalogs)

    def format_message(self) -> str:
        lines = ["Model catalogs refreshed:"]
        for catalog in self.catalogs:
            details = f"{len(catalog.models)} models"
            if catalog.source != "live":
                details += f", using {catalog.source} data"
            if catalog.message:
                details += f" ({catalog.message})"
            lines.append(f"- {catalog.provider}: {catalog.status}, {details}")
        return "\n".join(lines)


class ModelDiscoveryService:
    """Refresh provider model lists on explicit request."""

    def __init__(
        self,
        *,
        cache: ModelCatalogCache | None = None,
        credentials: FileCredentialStore | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.cache = cache or ModelCatalogCache()
        self.credentials = credentials or FileCredentialStore()
        self._client = client

    async def refresh(self, providers: tuple[ProviderConfig, ...]) -> DiscoverySummary:
        """Refresh all providers concurrently and persist live, fallback, and status data.

        Providers are independent, so they are queried concurrently. Doing this
        sequentially multiplied the slowest timeout by the provider count, which
        is what made an explicit refresh take seconds.
        """
        previous = self.cache.load()
        owned_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=_DISCOVERY_TIMEOUT_SECONDS)
        try:
            catalogs = list(
                await asyncio.gather(
                    *(
                        self._refresh_provider(provider, previous.get(provider.name), client)
                        for provider in providers
                    )
                )
            )
        finally:
            if owned_client:
                await client.aclose()
        updated = {catalog.provider: catalog for catalog in catalogs}
        self.cache.save(updated)
        return DiscoverySummary(tuple(catalogs), str(self.cache.path))

    async def _refresh_provider(
        self,
        provider: ProviderConfig,
        previous: ProviderModelCatalog | None,
        client: httpx.AsyncClient,
    ) -> ProviderModelCatalog:
        static_models = tuple(provider.models)
        if isinstance(provider, (AnthropicProviderConfig, OpenAICodexProviderConfig)):
            return _fallback_catalog(
                provider.name,
                static_models,
                previous,
                message="live discovery is not configured for this protocol",
            )

        credential = self.credentials.get(provider.credential_name or "")
        if not credential:
            credential = environ.get(provider.api_key_env)
        is_local = provider.name in _LOCAL_PROVIDER_NAMES
        if not credential and not is_local:
            return _status_catalog(
                provider.name,
                static_models,
                previous,
                status="login_required",
                message=f"set {provider.api_key_env} or run /login {provider.name}",
            )

        headers = {"Accept": "application/json"}
        if credential:
            headers["Authorization"] = f"Bearer {credential}"
        try:
            response = await client.get(_models_url(provider.base_url), headers=headers)
            response.raise_for_status()
            models = _model_ids(response.json())
            if not models:
                raise ValueError("provider returned no model IDs")
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            status = "offline" if is_local else "error"
            return _status_catalog(
                provider.name,
                static_models,
                previous,
                status=status,
                message=_safe_error_message(exc),
            )

        return live_catalog(provider.name, models)


def _models_url(base_url: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", "models")


def _model_ids(payload: Any) -> tuple[str, ...]:
    if not isinstance(payload, Mapping):
        raise ValueError("provider response must be an object")
    data = payload.get("data")
    if not isinstance(data, list):
        raise ValueError("provider response has no data list")
    models = {
        item["id"].strip()
        for item in data
        if isinstance(item, Mapping)
        and isinstance(item.get("id"), str)
        and item["id"].strip()
    }
    return tuple(sorted(models, key=str.casefold))


def _fallback_catalog(
    provider: str,
    static_models: tuple[str, ...],
    previous: ProviderModelCatalog | None,
    *,
    message: str,
) -> ProviderModelCatalog:
    if previous is not None and previous.models:
        return ProviderModelCatalog(
            provider=provider,
            models=previous.models,
            status="ready",
            source="cached",
            refreshed_at=previous.refreshed_at,
            message=message,
        )
    return ProviderModelCatalog(
        provider=provider,
        models=static_models,
        status="ready" if static_models else "error",
        source="static",
        message=message,
    )


def _status_catalog(
    provider: str,
    static_models: tuple[str, ...],
    previous: ProviderModelCatalog | None,
    *,
    status: str,
    message: str,
) -> ProviderModelCatalog:
    if previous is not None and previous.models:
        models = previous.models
        source = "cached"
        refreshed_at = previous.refreshed_at
    else:
        models = static_models
        source = "static"
        refreshed_at = None
    return ProviderModelCatalog(
        provider=provider,
        models=models,
        status=status,  # type: ignore[arg-type]
        source=source,  # type: ignore[arg-type]
        refreshed_at=refreshed_at,
        message=message,
    )


def _safe_error_message(error: Exception) -> str:
    """Return a discovery error without echoing credentials or response bodies."""
    if isinstance(error, httpx.HTTPStatusError):
        return f"HTTP {error.response.status_code}"
    if isinstance(error, httpx.ConnectError):
        return "connection failed"
    if isinstance(error, httpx.TimeoutException):
        return "request timed out"
    return str(error)[:160]
