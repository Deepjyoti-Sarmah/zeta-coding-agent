"""Compact session status formatting for the TUI."""

from __future__ import annotations

from typing import Protocol

from zeta_coding.session_stats import SessionStats


class StatusSession(Protocol):
    context_token_estimate: int
    context_window_tokens: int
    session_stats: SessionStats


def compact_status_line(session: StatusSession) -> str:
    """Build the minimal context, cache, and cost status line."""
    parts = [context_summary(session)]
    cache_status = cache_status_text(session.session_stats)
    if cache_status is not None:
        parts.append(cache_status)
    cost_status = cost_status_text(session.session_stats)
    if cost_status is not None:
        parts.append(cost_status)
    return " · ".join(parts)


def context_summary(session: StatusSession) -> str:
    """Return compact context usage with percentage and token counts."""
    used = max(session.context_token_estimate, 0)
    limit = session.context_window_tokens
    if limit <= 0:
        return f"{compact_token_count(used)}/?"
    percentage = min(round(used / limit * 100), 100)
    return f"{percentage}% · {compact_token_count(used)}/{compact_token_count(limit)}"


def cache_status_text(stats: SessionStats) -> str | None:
    if stats.cache_percentage is None:
        return None
    return f"{stats.cache_percentage:.0f}% cached"


def cost_status_text(stats: SessionStats) -> str | None:
    if stats.estimated_cost is None:
        return None
    return f"${stats.estimated_cost:.3f}"


def compact_token_count(value: int) -> str:
    """Format a token count using compact, readable units."""
    if value < 1_000:
        return str(value)
    if value < 10_000:
        return f"{value / 1_000:.1f}k".replace(".0k", "k")
    if value < 1_000_000:
        return f"{value // 1_000}k"
    return f"{value / 1_000_000:.1f}m".replace(".0m", "m")
