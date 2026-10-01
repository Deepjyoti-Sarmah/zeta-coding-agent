"""Parsing and validation helpers for slash commands."""

from __future__ import annotations

from pathlib import Path


def parse_command(text: str) -> tuple[str, str]:
    """Split a slash command into its normalized name and arguments."""
    command, separator, args = text[1:].partition(" ")
    return normalize_command_name(command), args.strip() if separator else ""


def parse_export_args(args: str) -> tuple[str | None, Path | None]:
    """Parse the optional format and destination accepted by /export."""
    parts = args.split()
    export_format: str | None = None
    destination: Path | None = None
    index = 0
    while index < len(parts):
        part = parts[index]
        if part == "--format":
            index += 1
            if index >= len(parts):
                raise ValueError("Usage: /export [--format html|jsonl] [destination]")
            export_format = parts[index]
        elif part.startswith("--format="):
            export_format = part.partition("=")[2]
        elif part.startswith("-"):
            raise ValueError(f"Unknown export option: {part}")
        elif destination is None:
            destination = Path(part).expanduser()
        else:
            raise ValueError("Usage: /export [--format html|jsonl] [destination]")
        index += 1
    return export_format, destination


def validate_session_name(value: str) -> str:
    """Validate and return a single-line session name."""
    name = value.strip()
    if not name:
        raise ValueError("Usage: /name <new name>")
    if any(char in name for char in "\r\n\t"):
        raise ValueError("Session name must be a single line.")
    return name


def normalize_command_name(name: str) -> str:
    """Normalize a command name for registry lookup."""
    return name.strip().removeprefix("/").lower()
