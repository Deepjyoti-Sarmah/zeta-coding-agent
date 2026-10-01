"""Model availability and fallback decisions for coding sessions."""

from __future__ import annotations

from collections.abc import Mapping
from zeta_coding.model_catalog_cache import ProviderModelCatalog
from zeta_coding.provider_config import (
    CredentialReader,
    ProviderConfig,
    provider_has_usable_credentials,
)

LOCAL_PROVIDERS = frozenset({"ollama", "lm-studio"})


def provider_can_run(
    provider: ProviderConfig,
    *,
    catalogs: Mapping[str, ProviderModelCatalog],
    credentials: CredentialReader,
) -> bool:
    """Return whether a provider can be selected for the next request."""
    if provider.name in LOCAL_PROVIDERS:
        catalog = catalogs.get(provider.name)
        return catalog is not None and catalog.status == "ready"
    return provider_has_usable_credentials(provider, credential_reader=credentials)


def models_for_provider(
    provider: ProviderConfig,
    *,
    catalogs: Mapping[str, ProviderModelCatalog],
) -> tuple[str, ...]:
    """Return live or cached models, falling back to the static catalog."""
    catalog = catalogs.get(provider.name)
    if catalog is not None and catalog.status == "ready" and catalog.models:
        return catalog.models
    return provider.models


def unavailable_provider_statuses(
    providers: tuple[ProviderConfig, ...],
    *,
    catalogs: Mapping[str, ProviderModelCatalog],
    credentials: CredentialReader,
) -> tuple[tuple[str, str, str], ...]:
    """Return providers that need login, refresh, or a local server."""
    statuses: list[tuple[str, str, str]] = []
    for provider in providers:
        catalog = catalogs.get(provider.name)
        if catalog is not None:
            if catalog.status != "ready":
                statuses.append((provider.name, catalog.status, catalog.message or ""))
            continue
        if provider.name in LOCAL_PROVIDERS:
            statuses.append((provider.name, "offline", "run /models to check the local server"))
        elif not provider_can_run(provider, catalogs=catalogs, credentials=credentials):
            statuses.append(
                (provider.name, "login_required", f"run /login to configure {provider.name}")
            )
    return tuple(statuses)
