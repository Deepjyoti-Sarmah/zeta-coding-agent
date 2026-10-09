from __future__ import annotations

import asyncio
import unittest
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Input, ListView

from zeta_coding.session import ModelChoice
from zeta_coding.tui.app import ZetaTuiApp, _theme_css_variables
from zeta_coding.tui.config import ZETA_DARK_THEME
from zeta_coding.tui.model_picker_screen import ModelPickerScreen

_MODELS = tuple(ModelChoice(provider_name="openai-codex", model=f"gpt-5.{i}") for i in range(60))
_SCOPED = _MODELS[:3]


def _choices() -> tuple[ModelChoice, ...]:
    return _MODELS


def _picker() -> ModelPickerScreen:
    return ModelPickerScreen(
        _choices(),
        scoped_choices=_SCOPED,
        current_model="gpt-5.0",
        provider_name="openai-codex",
        theme=ZETA_DARK_THEME,
        unavailable_providers=tuple(
            (f"p{index}", "login_required", "run /login") for index in range(22)
        ),
    )


class _Harness(App[None]):
    """Hosts the real app CSS so layout regressions are caught for real."""

    CSS = ZetaTuiApp.CSS

    def get_theme_variable_defaults(self) -> dict[str, str]:
        return {
            **super().get_theme_variable_defaults(),
            **_theme_css_variables(ZETA_DARK_THEME),
        }

    def compose(self) -> ComposeResult:
        return iter(())


def _visible_band(app: App[None], screen: ModelPickerScreen) -> tuple[int, int]:
    """Return the rows of the list that the dialog actually shows."""
    model_list = screen.query_one("#model-picker-list", ListView)
    modal = screen.query_one("#model-picker")
    return (
        max(model_list.region.y, modal.region.y),
        min(model_list.region.bottom, modal.region.bottom),
    )


class ModelPickerLayoutTests(unittest.TestCase):
    """The list must never be clipped by the dialog at any terminal size."""

    SIZES: ClassVar[tuple[tuple[int, int], ...]] = [
        (100, 24), (100, 40), (90, 20), (80, 18)
    ]

    def _drive(self, size: tuple[int, int], presses: tuple[str, ...]) -> dict[str, object]:
        async def run() -> dict[str, object]:
            app = _Harness()
            async with app.run_test(size=size) as pilot:
                app.push_screen(_picker())
                await pilot.pause()
                screen = app.screen
                assert isinstance(screen, ModelPickerScreen)
                model_list = screen.query_one("#model-picker-list", ListView)
                modal = screen.query_one("#model-picker")
                top, bottom = _visible_band(app, screen)
                clipped = model_list.region.bottom > modal.region.bottom
                off_screen = modal.region.bottom > app.screen.size.height
                for key in presses:
                    await pilot.press(key)
                    await pilot.pause()
                    row = model_list.highlighted_child
                    if row is not None and not (
                        row.region.height > 0 and top <= row.region.y < bottom
                    ):
                        clipped = True
                return {
                    "clipped": clipped,
                    "off_screen": off_screen,
                    "mode": screen.mode,
                    "items": len(screen.visible_choices),
                    "scroll": model_list.scroll_offset.y,
                    "focus_is_search": isinstance(app.focused, Input),
                    "search": screen.search_value,
                }

        return asyncio.run(run())

    def test_list_is_not_clipped_and_selection_stays_visible(self) -> None:
        for size in self.SIZES:
            with self.subTest(size=size):
                result = self._drive(size, ("down",) * 30)
                self.assertFalse(result["clipped"], "selection scrolled out of view")
                self.assertFalse(result["off_screen"], "dialog overflowed the screen")

    def test_selection_returns_into_view_when_moving_up(self) -> None:
        for size in self.SIZES:
            with self.subTest(size=size):
                result = self._drive(size, ("down",) * 20 + ("up",) * 20)
                self.assertFalse(result["clipped"])

    def test_tab_cycles_back_to_all_models(self) -> None:
        for size in self.SIZES:
            with self.subTest(size=size):
                result = self._drive(size, ("tab", "tab", "tab", "tab"))
                self.assertEqual(result["mode"], "all")
                self.assertEqual(result["items"], len(_choices()))
                self.assertEqual(result["scroll"], 0)

    def test_search_keeps_focus_after_arrow_navigation(self) -> None:
        result = self._drive((100, 40), ("down", "down", "down"))
        self.assertTrue(result["focus_is_search"])

    def test_typing_filters_the_model_list(self) -> None:
        result = self._drive((100, 40), ("g", "p", "t", "-", "5", ".", "4"))
        self.assertEqual(result["search"], "gpt-5.4")


class ModelPickerRefreshTests(unittest.TestCase):
    def test_open_picker_adopts_newly_discovered_models(self) -> None:
        async def run() -> None:
            app = _Harness()
            async with app.run_test(size=(100, 40)) as pilot:
                app.push_screen(_picker())
                await pilot.pause()
                screen = app.screen
                assert isinstance(screen, ModelPickerScreen)
                model_list = screen.query_one("#model-picker-list", ListView)
                self.assertEqual(len(model_list.children), len(_choices()))

                screen.apply_refreshed_choices(
                    [ModelChoice(provider_name="openai-codex", model="gpt-new")],
                    (("new-provider", "login_required", "run /login"),),
                )
                await pilot.pause()

                self.assertEqual(screen.choices, (
                    ModelChoice(provider_name="openai-codex", model="gpt-new"),
                ))
                self.assertEqual(len(model_list.children), 1)
                summary = screen.query_one("#model-picker-unavailable")
                self.assertIn("1 providers need login", summary.render().plain)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
