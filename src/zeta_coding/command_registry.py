"""Registration and execution of slash commands."""

from __future__ import annotations

from zeta_coding.command_parsing import parse_command
from zeta_coding.command_types import (
    CommandContext,
    CommandResult,
    CommandSession,
    SlashCommand,
)


class CommandRegistry:
    """Register, find, and execute slash commands."""

    def __init__(self) -> None:
        self._commands: dict[str, SlashCommand] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: SlashCommand) -> None:
        name = command.name.strip().removeprefix("/").lower()
        if name in self._commands:
            raise ValueError(f"Duplicate slash command: /{name}")
        self._commands[name] = command
        for alias in command.aliases:
            normalized_alias = alias.strip().removeprefix("/").lower()
            if normalized_alias in self._commands or normalized_alias in self._aliases:
                raise ValueError(f"Duplicate slash command alias: /{normalized_alias}")
            self._aliases[normalized_alias] = name

    def get(self, name: str) -> SlashCommand | None:
        normalized = name.strip().removeprefix("/").lower()
        return self._commands.get(self._aliases.get(normalized, normalized))

    def list_commands(self) -> tuple[SlashCommand, ...]:
        return tuple(self._commands[name] for name in sorted(self._commands))

    def execute(self, session: CommandSession, text: str) -> CommandResult:
        stripped = text.strip()
        if not stripped.startswith("/") or stripped.startswith("/skill:"):
            return CommandResult(handled=False)
        name, args = parse_command(stripped)
        if not name:
            return CommandResult(handled=False)
        command = self.get(name)
        if command is None and name == "scoped" and args.lower() == "models":
            command = self.get("scoped-models")
            name, args = "scoped-models", ""
        if command is None:
            return CommandResult(handled=False)
        return command.handler(CommandContext(session, self, stripped, name, args))
