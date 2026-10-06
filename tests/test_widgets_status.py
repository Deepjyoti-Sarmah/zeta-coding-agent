from __future__ import annotations

import unittest
from types import SimpleNamespace

from zeta_coding.session_stats import SessionStats
from zeta_coding.tui.widgets import (
    _cache_status,
    _compact_status_line,
    _context_summary,
    _cost_status,
)


class CompactStatusFormattingTests(unittest.TestCase):
    def test_context_summary_uses_compact_counts(self) -> None:
        session = SimpleNamespace(
            context_token_estimate=70_000,
            context_window_tokens=200_000,
        )

        self.assertEqual(_context_summary(session), "35% · 70k/200k")

    def test_context_summary_handles_unknown_limit(self) -> None:
        session = SimpleNamespace(context_token_estimate=2_000, context_window_tokens=0)

        self.assertEqual(_context_summary(session), "2k/?")

    def test_optional_segments_are_hidden_when_unavailable(self) -> None:
        stats = SessionStats()

        self.assertIsNone(_cache_status(stats))
        self.assertIsNone(_cost_status(stats))

    def test_compact_status_line_joins_available_segments(self) -> None:
        session = SimpleNamespace(
            context_token_estimate=70_000,
            context_window_tokens=200_000,
            session_stats=SessionStats(
                input_tokens=1_000,
                cache_read_tokens=820,
                estimated_cost=0.671,
            ),
        )

        self.assertEqual(
            _compact_status_line(session),
            "35% · 70k/200k · 82% cached · $0.671",
        )


if __name__ == "__main__":
    unittest.main()
