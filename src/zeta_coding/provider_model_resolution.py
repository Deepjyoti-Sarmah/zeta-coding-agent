"""Provider/model validation helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class ModelProvider(Protocol):
    name: str
    models: tuple[str, ...]


def validate_model(
    provider: ModelProvider,
    model: str,
    *,
    error: Callable[[str], Exception],
) -> None:
    """Raise the caller's configuration error when a model is unavailable."""
    if model in provider.models:
        return
    available = ", ".join(sorted(provider.models)) or "none"
    raise error(
        f"Model is not configured for provider {provider.name}: {model}. "
        f"Available models: {available}"
    )
