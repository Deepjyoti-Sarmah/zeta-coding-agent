"""Credential lookup for configured providers."""

from __future__ import annotations

from os import environ
from typing import Protocol

from zeta_coding.oauth_registry import get_oauth_provider


class CredentialProvider(Protocol):
    name: str
    credential_name: str | None
    api_key_env: str


class CredentialReader(Protocol):
    def get(self, name: str) -> str | None: ...


def has_usable_credentials(
    provider: CredentialProvider,
    *,
    credential_reader: CredentialReader | None = None,
) -> bool:
    """Return whether a provider can be called without setup."""
    if provider.credential_name and credential_reader is not None:
        get_oauth = getattr(credential_reader, "get_oauth", None)
        if (
            get_oauth_provider(provider.name) is not None
            and get_oauth is not None
            and get_oauth(provider.credential_name) is not None
        ):
            return True
        if credential_reader.get(provider.credential_name):
            return True
    return bool(environ.get(provider.api_key_env))


def api_key_for_provider(
    provider: CredentialProvider,
    *,
    credential_reader: CredentialReader | None,
) -> str:
    """Resolve a stored, OAuth, or environment API credential."""
    if provider.credential_name and credential_reader is not None:
        credential = credential_reader.get(provider.credential_name)
        if credential:
            return credential
        get_oauth = getattr(credential_reader, "get_oauth", None)
        if get_oauth_provider(provider.name) is not None and get_oauth is not None:
            oauth_credential = get_oauth(provider.credential_name)
            access = getattr(oauth_credential, "access", None)
            if isinstance(access, str) and access:
                return access

    api_key = environ.get(provider.api_key_env)
    if api_key:
        return api_key
    credential_hint = f" or run /login {provider.name}" if provider.credential_name else ""
    raise RuntimeError(f"Missing provider API key. Set {provider.api_key_env}{credential_hint}.")
