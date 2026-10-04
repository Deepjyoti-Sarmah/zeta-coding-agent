"""Pure provider-selection helpers for the login flow."""

from __future__ import annotations

from collections.abc import Sequence

from zeta_coding.credentials import FileCredentialStore
from zeta_coding.oauth_registry import oauth_provider_ids
from zeta_coding.provider_catalog import ProviderCatalogEntry


def login_provider_label(provider: ProviderCatalogEntry) -> str:
    return f"{provider.display_name} — {provider.name}"


def subscription_login_providers(
    providers: Sequence[ProviderCatalogEntry],
) -> tuple[ProviderCatalogEntry, ...]:
    provider_ids = oauth_provider_ids()
    return tuple(provider for provider in providers if provider.name in provider_ids)


def api_key_login_providers(
    providers: Sequence[ProviderCatalogEntry],
) -> tuple[ProviderCatalogEntry, ...]:
    return tuple(provider for provider in providers if "api_key" in provider.auth_methods)


def stored_credential_providers(
    providers: Sequence[ProviderCatalogEntry],
) -> tuple[ProviderCatalogEntry, ...]:
    credential_store = FileCredentialStore()
    return tuple(
        provider
        for provider in providers
        if provider.credential_name is not None
        and credential_store_has_entry(credential_store, provider.credential_name)
    )


def credential_store_has_entry(
    credential_store: FileCredentialStore,
    credential_name: str,
) -> bool:
    return (
        credential_store.get(credential_name) is not None
        or credential_store.get_oauth(credential_name) is not None
    )


def filter_login_providers(
    providers: Sequence[ProviderCatalogEntry],
    query: str,
) -> tuple[ProviderCatalogEntry, ...]:
    normalized = query.strip().casefold()
    if not normalized:
        return tuple(providers)
    return tuple(
        provider
        for provider in providers
        if normalized in provider.name.casefold()
        or normalized in provider.display_name.casefold()
    )
