from __future__ import annotations

import unittest
from pathlib import Path

from zeta_coding.command_parsing import (
    normalize_command_name,
    parse_command,
    parse_export_args,
    validate_session_name,
)
from zeta_coding.commands import create_default_command_registry
from zeta_coding.session_stats import SessionStats


class CommandParsingTests(unittest.TestCase):
    def test_parse_command_normalizes_name_and_arguments(self) -> None:
        self.assertEqual(parse_command("/MODEL  gpt-4.1 "), ("model", "gpt-4.1"))
        self.assertEqual(normalize_command_name(" /Models "), "models")

    def test_parse_export_args_accepts_option_forms(self) -> None:
        self.assertEqual(
            parse_export_args("--format html output.html"),
            ("html", Path("output.html")),
        )
        self.assertEqual(parse_export_args("--format=jsonl"), ("jsonl", None))

    def test_parse_export_args_rejects_unknown_options(self) -> None:
        with self.assertRaises(ValueError):
            parse_export_args("--unknown")

    def test_validate_session_name_rejects_multiline_names(self) -> None:
        with self.assertRaises(ValueError):
            validate_session_name("first\nsecond")


class SessionStatsTests(unittest.TestCase):
    def test_cache_percentage_uses_prompt_tokens(self) -> None:
        stats = SessionStats(input_tokens=1000, cache_read_tokens=820)

        self.assertEqual(stats.cache_percentage, 82.0)

    def test_cache_percentage_is_hidden_without_cache_reads(self) -> None:
        stats = SessionStats(input_tokens=1000)

        self.assertIsNone(stats.cache_percentage)


class CommandRegistryTests(unittest.TestCase):
    def test_builtin_registry_contains_aliases(self) -> None:
        registry = create_default_command_registry()

        self.assertIs(registry.get("/exit"), registry.get("quit"))
        self.assertIsNone(registry.get("scoped"))

    def test_builtin_commands_are_sorted(self) -> None:
        registry = create_default_command_registry()
        names = [command.name for command in registry.list_commands()]

        self.assertEqual(names, sorted(names))
        self.assertIn("models", names)
        self.assertIn("model", names)


if __name__ == "__main__":
    unittest.main()
