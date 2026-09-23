# Zeta TUI

Zeta's full interactive interface uses Textual behind an adapter boundary. `zeta_agent` emits provider-neutral events; `zeta_coding.tui` consumes and renders them.

For current behavior in a Zeta checkout, read:

- `website/content/guides/tui.md`
- `website/content/reference/keybindings.md`
- `src/zeta_coding/tui/`

Do not introduce Textual dependencies into `zeta_agent`. Keep reusable behavior in the harness/session layers and UI behavior in the adapter. Use Textual pilot tests and fake providers for deterministic interaction tests.
