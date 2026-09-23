"""Textual TUI frontend for Zeta coding sessions."""

from __future__ import annotations

from zeta_coding.tui.adapter import TuiEventAdapter
from zeta_coding.tui.app import ZetaTuiApp, run_tui_app
from zeta_coding.tui.autocomplete import CompletionOption
from zeta_coding.tui.config import (
    BUILTIN_TUI_THEME_NAMES,
    HIGH_CONTRAST_THEME,
    ZETA_DARK_THEME,
    ZETA_LIGHT_THEME,
    TuiConfigError,
    TuiKeybindings,
    TuiRoleStyle,
    TuiSettings,
    TuiTheme,
    TuiThemeName,
    TurnNotificationMode,
    get_tui_theme,
    load_tui_settings,
    save_tui_settings,
    tui_settings_path,
)
from zeta_coding.tui.state import ChatItem, TuiState
from zeta_coding.tui.widgets import (
    CompactSessionInfo,
    SessionSidebar,
    StreamingTranscriptMessageWidget,
    TranscriptMessageWidget,
    TranscriptView,
    render_chat_item,
    render_compact_session_info,
    render_session_sidebar,
    transcript_item_selection_text,
)

__all__ = [
    "BUILTIN_TUI_THEME_NAMES",
    "ChatItem",
    "CompletionOption",
    "CompactSessionInfo",
    "ZetaTuiApp",
    "SessionSidebar",
    "ZETA_DARK_THEME",
    "ZETA_LIGHT_THEME",
    "StreamingTranscriptMessageWidget",
    "TranscriptMessageWidget",
    "TranscriptView",
    "TuiEventAdapter",
    "TuiConfigError",
    "HIGH_CONTRAST_THEME",
    "TuiKeybindings",
    "TuiRoleStyle",
    "TuiSettings",
    "TuiTheme",
    "TuiThemeName",
    "TurnNotificationMode",
    "TuiState",
    "get_tui_theme",
    "load_tui_settings",
    "render_chat_item",
    "render_compact_session_info",
    "render_session_sidebar",
    "run_tui_app",
    "save_tui_settings",
    "transcript_item_selection_text",
    "tui_settings_path",
]
