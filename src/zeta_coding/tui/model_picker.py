"""Pure model-picker formatting and filtering helpers."""

from __future__ import annotations

from collections.abc import Sequence

from zeta_coding.session import ModelChoice


def model_choice_label(
    choice: ModelChoice,
    *,
    current_model: str,
    current_provider: str,
    scoped: bool = False,
    provider_heading: bool = False,
) -> str:
    """Format one model choice with current and provider-group markers."""
    marker = (
        "* "
        if (choice.provider_name == current_provider and choice.model == current_model)
        else "  "
    )
    suffix = " [scoped]" if scoped else ""
    if provider_heading:
        return f"{choice.provider_name}\n{marker}  {choice.model}{suffix}"
    return f"  {marker}{choice.model}{suffix}"


def filter_model_choices(
    choices: Sequence[ModelChoice],
    query: str,
) -> tuple[ModelChoice, ...]:
    """Filter choices by provider or model name."""
    normalized = query.strip().lower()
    if not normalized:
        return tuple(choices)
    return tuple(
        choice
        for choice in choices
        if normalized in choice.provider_name.lower()
        or normalized in choice.model.lower()
    )
