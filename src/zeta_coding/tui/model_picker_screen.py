"""Textual model picker screens."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import ClassVar, Literal, cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static

from zeta_coding.session import ModelChoice
from zeta_coding.tui.config import TuiTheme
from zeta_coding.tui.model_picker import filter_model_choices, model_choice_label

BindingEntry = Binding | tuple[str, str] | tuple[str, str, str]

class ModelPickerSearchInput(Input):
    """Search input that keeps model-picker control keys local to the picker."""

    BINDINGS: ClassVar[list[BindingEntry]] = [
        Binding("escape", "cancel", "Cancel", show=False, priority=True),
        Binding("tab", "toggle_mode", "Mode", show=False, priority=True),
        Binding("ctrl+i", "toggle_mode", "Mode", show=False, priority=True),
        Binding("up", "cursor_up", "Up", show=False, priority=True),
        Binding("down", "cursor_down", "Down", show=False, priority=True),
        Binding("pageup", "page_up", "Page up", show=False, priority=True),
        Binding("pagedown", "page_down", "Page down", show=False, priority=True),
    ]

    def _picker(self) -> ModelPickerScreen:
        return cast(ModelPickerScreen, self.screen)

    def on_key(self, event: Key) -> None:
        """Route picker control keys before the input edits its text."""
        if event.key == "up":
            event.stop()
            event.prevent_default()
            self.action_cursor_up()
        elif event.key == "down":
            event.stop()
            event.prevent_default()
            self.action_cursor_down()
        elif event.key == "pageup":
            event.stop()
            event.prevent_default()
            self.action_page_up()
        elif event.key == "pagedown":
            event.stop()
            event.prevent_default()
            self.action_page_down()
        elif event.key in {"tab", "ctrl+i"}:
            event.stop()
            event.prevent_default()
            self.action_toggle_mode()
        elif event.key == "escape":
            event.stop()
            event.prevent_default()
            self.action_cancel()

    def action_cursor_up(self) -> None:
        """Move the model picker selection up."""
        self._picker().action_cursor_up()

    def action_cursor_down(self) -> None:
        """Move the model picker selection down."""
        self._picker().action_cursor_down()

    def action_page_up(self) -> None:
        """Move one page up in the model list."""
        self._picker().action_page_up()

    def action_page_down(self) -> None:
        """Move one page down in the model list."""
        self._picker().action_page_down()

    def action_toggle_mode(self) -> None:
        """Toggle between all and scoped picker modes."""
        self._picker().action_toggle_mode()

    def action_cancel(self) -> None:
        """Close the model picker."""
        self._picker().action_cancel()


class ModelPickerScreen(ModalScreen[ModelChoice | None]):
    """Model picker for the active TUI provider."""

    BINDINGS: ClassVar[list[BindingEntry]] = [
        Binding("escape", "cancel", "Cancel"),
        Binding("tab", "toggle_mode", "Mode", show=False, priority=True),
        Binding("ctrl+i", "toggle_mode", "Mode", show=False, priority=True),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("enter", "accept_model", "Select", show=False),
    ]

    def __init__(
        self,
        choices: Sequence[ModelChoice],
        *,
        scoped_choices: Sequence[ModelChoice],
        current_model: str,
        provider_name: str,
        theme: TuiTheme,
        unavailable_providers: Sequence[tuple[str, str, str]] = (),
        on_toggle_scoped: Callable[[ModelChoice], Sequence[ModelChoice]] | None = None,
        picker_kind: Literal["model", "scoped"] = "model",
    ) -> None:
        super().__init__()
        self.choices = tuple(dict.fromkeys(choices))
        self.scoped_choices = tuple(dict.fromkeys(scoped_choices))
        self.visible_choices = self.choices
        self.current_model = current_model
        self.provider_name = provider_name
        self.theme = theme
        self.unavailable_providers = tuple(unavailable_providers)
        self.on_toggle_scoped = on_toggle_scoped
        self.picker_kind = picker_kind
        self.mode: Literal["all", "scoped"] = "all"
        self.search_value = ""

    def apply_refreshed_choices(
        self,
        choices: Sequence[ModelChoice],
        unavailable_providers: Sequence[tuple[str, str, str]] = (),
    ) -> None:
        """Adopt newly discovered models without closing the open picker."""
        self.choices = tuple(dict.fromkeys(choices))
        self.unavailable_providers = tuple(unavailable_providers)
        if not self.choices:
            return
        self._update_unavailable_summary()
        self._refresh_model_list()

    def _update_unavailable_summary(self) -> None:
        """Recompute the login/offline provider summary line."""
        summary = self.query_one("#model-picker-unavailable", Static)
        login_required = sum(
            status == "login_required" for _name, status, _message in self.unavailable_providers
        )
        offline = sum(
            status == "offline" for _name, status, _message in self.unavailable_providers
        )
        parts = []
        if login_required:
            parts.append(f"{login_required} providers need login")
        if offline:
            parts.append(f"{offline} providers offline")
        summary.display = bool(parts)
        if parts:
            summary.update(" · ".join(parts))

    def compose(self) -> ComposeResult:
        """Compose the model picker."""
        with Vertical(id="model-picker"):
            title = (
                f"Model: {self.provider_name}"
                if self.picker_kind == "model"
                else "Scoped models"
            )
            yield Static(title, id="model-picker-title")
            yield Static("", id="model-picker-tabs")
            yield Static("", id="model-picker-unavailable")
            yield ModelPickerSearchInput(
                placeholder="Search models", id="model-picker-search"
            )
            yield ListView(
                *[
                    ListItem(
                        Label(
                            model_choice_label(
                                choice,
                                current_model=self.current_model,
                                current_provider=self.provider_name,
                                scoped=choice in self.scoped_choices,
                            ),
                            markup=False,
                        )
                    )
                    for choice in self.choices
                ],
                id="model-picker-list",
            )
            yield Static("", id="model-picker-help")

    def on_mount(self) -> None:
        """Focus the search field."""
        search = self.query_one("#model-picker-search", Input)
        search.focus()
        self._update_unavailable_summary()
        self._refresh_model_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter model choices as the search value changes."""
        if event.input.id != "model-picker-search":
            return
        event.stop()
        self.search_value = event.value
        self._refresh_model_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Select the highlighted model from the search field."""
        if event.input.id != "model-picker-search":
            return
        event.stop()
        self._select_visible_choice()

    def _reset_model_list_index(self, previous: int | None = None) -> None:
        """Move selection to the current model or first visible row."""
        model_list = self.query_one("#model-picker-list", ListView)
        if not self.visible_choices:
            model_list.index = None
            return
        try:
            target = self.visible_choices.index(
                ModelChoice(provider_name=self.provider_name, model=self.current_model)
            )
        except ValueError:
            # Keep the reader where they were when the row still exists.
            target = previous if previous is not None and 0 <= previous < len(self.visible_choices) else 0
        model_list.index = target
        self._scroll_selection_into_view(model_list, target)

    def on_key(self, event: Key) -> None:
        """Route model picker keys to the list."""
        if event.key == "up":
            event.stop()
            self.action_cursor_up()
        elif event.key == "down":
            event.stop()
            self.action_cursor_down()
        elif event.key in {"tab", "ctrl+i"}:
            event.stop()
            self.action_toggle_mode()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle the selected row."""
        event.stop()
        self._select_visible_choice()

    def action_cursor_up(self) -> None:
        """Move to the previous model and keep it visible."""
        self._move_selection(-1)

    def action_cursor_down(self) -> None:
        """Move to the next model and keep it visible."""
        self._move_selection(1)

    def _move_selection(self, delta: int) -> None:
        model_list = self.query_one("#model-picker-list", ListView)
        if not self.visible_choices:
            return
        current = model_list.index
        index = 0 if current is None else max(0, min(current + delta, len(self.visible_choices) - 1))
        if index == current:
            return
        model_list.index = index
        self._scroll_selection_into_view(model_list, index)

    def _scroll_selection_into_view(
        self, model_list: ListView, index: int
    ) -> None:
        """Keep the highlighted row inside the list viewport.

        ``ListView.watch_index`` scrolls its own container, but only once the
        row has been laid out. After a rebuild the regions are still stale, so
        schedule the scroll for after the next refresh as well.
        """
        children = model_list.children
        if not 0 <= index < len(children):
            return
        model_list.scroll_to_widget(children[index], animate=False)
        model_list.call_after_refresh(
            model_list.scroll_to_widget, children[index], animate=False
        )

    def action_page_up(self) -> None:
        """Move one page up in the model list."""
        self._move_selection(-self._page_size())

    def action_page_down(self) -> None:
        """Move one page down in the model list."""
        self._move_selection(self._page_size())

    def _page_size(self) -> int:
        """Return how many rows the list can currently show."""
        model_list = self.query_one("#model-picker-list", ListView)
        return max(1, model_list.scrollable_content_region.height)

    def action_accept_model(self) -> None:
        """Select the highlighted model."""
        self._select_visible_choice()

    def action_toggle_mode(self) -> None:
        """Toggle between all models and scoped models."""
        if self.picker_kind != "model":
            return
        self.mode = "scoped" if self.mode == "all" else "all"
        self._refresh_model_list()

    def action_toggle_scoped(self) -> None:
        """Add or remove the highlighted model from scoped models."""
        if self.on_toggle_scoped is None or not self.visible_choices:
            return
        model_list = self.query_one("#model-picker-list", ListView)
        index = model_list.index
        if index is None:
            return
        choice = self.visible_choices[index]
        self.scoped_choices = tuple(dict.fromkeys(self.on_toggle_scoped(choice)))
        self._refresh_model_list()

    def action_cancel(self) -> None:
        """Close without selecting a model."""
        self.dismiss(None)

    def _select_visible_choice(self) -> None:
        if not self.visible_choices:
            return
        model_list = self.query_one("#model-picker-list", ListView)
        index = model_list.index
        if index is None:
            return
        choice = self.visible_choices[index]
        if self.picker_kind == "scoped":
            self.action_toggle_scoped()
            return
        self.dismiss(choice)

    def _refresh_model_list(self) -> None:
        base_choices = self.scoped_choices if self.mode == "scoped" else self.choices
        self.visible_choices = filter_model_choices(base_choices, self.search_value)
        model_list = self.query_one("#model-picker-list", ListView)
        previous_index = model_list.index
        model_list.clear()
        model_list.extend(
            [
                ListItem(
                    Label(
                        model_choice_label(
                            choice,
                            current_model=self.current_model,
                            current_provider=self.provider_name,
                            scoped=choice in self.scoped_choices,
                            provider_heading=(
                                index == 0
                                or choice.provider_name
                                != self.visible_choices[index - 1].provider_name
                            ),
                        ),
                        markup=False,
                    )
                )
                for index, choice in enumerate(self.visible_choices)
            ]
        )
        # A rebuild replaces the whole viewport, so a stale scroll offset would
        # leave the list scrolled past the restored selection.
        model_list.scroll_home(animate=False)
        self._reset_model_list_index(previous=previous_index)
        scope_count = len(self.scoped_choices)
        tabs = self.query_one("#model-picker-tabs", Static)
        if self.picker_kind == "scoped":
            tabs.update(
                "Scoped models setup — Enter toggles membership; active model is unchanged"
            )
            help_text = (
                "No matching models - Enter toggles scoped model"
                if not self.visible_choices
                else f"Enter toggles scoped model - {scope_count} scoped"
            )
        elif self.mode == "all":
            tabs.update("Tabs: ● All models  ○ Scoped models")
            help_text = (
                "all models: no matching models - Tab switches to scoped models"
                if not self.visible_choices
                else (
                    "All models - Enter selects active model - Tab switches tabs - "
                    f"{scope_count} scoped"
                )
            )
        else:
            tabs.update("Tabs: ○ All models  ● Scoped models")
            help_text = (
                "scoped models: no matching models - Tab switches to all models"
                if not self.visible_choices
                else "Scoped models - Enter selects active model - Tab switches tabs"
            )
        self.query_one("#model-picker-help", Static).update(help_text)


