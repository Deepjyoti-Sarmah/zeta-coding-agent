"""Shared result types for slash commands."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Result of handling a coding-session slash command."""

    handled: bool
    exit_requested: bool = False
    clear_requested: bool = False
    reload_requested: bool = False
    new_session_requested: bool = False
    compact_summary: str | None = None
    export_requested: bool = False
    export_destination: Path | None = None
    export_format: str | None = None
    resume_session_id: str | None = None
    resume_picker_requested: bool = False
    prompts_picker_requested: bool = False
    tree_picker_requested: bool = False
    login_picker_requested: bool = False
    custom_provider_login_requested: bool = False
    login_provider: str | None = None
    login_method: str | None = None
    logout_picker_requested: bool = False
    logout_provider: str | None = None
    model_picker_requested: bool = False
    model_catalog_refresh_requested: bool = False
    tools_picker_requested: bool = False
    scoped_models_picker_requested: bool = False
    skills_picker_requested: bool = False
    theme_picker_requested: bool = False
    thinking_level: str | None = None
    theme: str | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class CommandSession(Protocol):
    cwd: Path
    model: str
    provider_name: str
    available_models: tuple[str, ...]
    available_providers: tuple[str, ...]

    def set_model(self, model: str) -> None: ...
    def reload_provider_settings(self) -> None: ...


@dataclass(frozen=True, slots=True)
class CommandContext:
    """Runtime context passed to a slash-command handler."""

    session: CommandSession
    registry: CommandRegistryProtocol
    text: str
    name: str
    args: str


class CommandRegistryProtocol(Protocol):
    def get(self, name: str) -> SlashCommand | None: ...


CommandHandler = Callable[[CommandContext], CommandResult]


@dataclass(frozen=True, slots=True)
class SlashCommand:
    """A registered slash command and its user-facing metadata."""

    name: str
    description: str
    usage: str
    handler: CommandHandler
    aliases: tuple[str, ...] = ()
    search_terms: tuple[str, ...] = ()
