"""Routing helpers for slash-command output."""

from __future__ import annotations


def message_uses_transcript(command_text: str) -> bool:
    """Return whether command output belongs in the conversation transcript."""
    command_name = command_text.split(maxsplit=1)[0].casefold()
    return command_name in {"/reload", "/system", "/models"}


def message_uses_notification(command_text: str, message: str) -> bool:
    """Return whether command output should be shown as a notification."""
    command_name = command_text.split(maxsplit=1)[0].casefold()
    return command_name == "/name" and message.startswith("Session renamed: ")


def output_title(command_text: str) -> str:
    """Return the modal title for command output."""
    command_name = command_text.split(maxsplit=1)[0].removeprefix("/")
    return f"/{command_name or 'help'}"
