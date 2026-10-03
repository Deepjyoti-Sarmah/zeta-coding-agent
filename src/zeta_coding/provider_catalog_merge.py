"""Dependency-light helpers for merging provider catalog values."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeVar

Metadata = TypeVar("Metadata")


def unique_strings(values: tuple[str, ...]) -> tuple[str, ...]:
    """Remove duplicate strings while preserving their first-seen order."""
    return tuple(dict.fromkeys(values))


def merge_provider_metadata(base: Metadata, metadata: Metadata) -> Metadata:
    """Merge fields from a saved provider metadata entry into catalog metadata."""
    from dataclasses import replace

    return replace(
        base,
        name=metadata.name or base.name,
        api=metadata.api or base.api,
        base_url=metadata.base_url or base.base_url,
        reasoning=metadata.reasoning if metadata.reasoning is not None else base.reasoning,
        input=metadata.input or base.input,
        cost={**base.cost, **metadata.cost},
        cost_tiers=metadata.cost_tiers or base.cost_tiers,
        context_window=metadata.context_window or base.context_window,
        max_tokens=metadata.max_tokens or base.max_tokens,
        headers={**base.headers, **metadata.headers},
        compat={**base.compat, **metadata.compat},
        thinking_level_map={**base.thinking_level_map, **metadata.thinking_level_map},
    )


def merge_model_metadata(
    incoming: Mapping[str, Metadata],
    existing: Mapping[str, Metadata],
    merge: Callable[[Metadata, Metadata], Metadata],
) -> dict[str, Metadata]:
    """Merge metadata, allowing existing entries to fill missing catalog entries."""
    merged = dict(incoming)
    for model, metadata in existing.items():
        merged[model] = merge(merged[model], metadata) if model in merged else metadata
    return merged
