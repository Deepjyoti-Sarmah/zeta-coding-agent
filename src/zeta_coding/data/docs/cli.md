# Zeta CLI and commands

Zeta supports print mode and a Textual interactive TUI. The CLI entry point is `zeta_coding.cli:app`.

For current user-facing behavior in a Zeta checkout, read:

- `website/content/reference/cli.md`
- `website/content/reference/slash-commands.md`
- `src/zeta_coding/commands.py`

Keep command parsing and application-specific resource loading in `zeta_coding`, not the reusable `zeta_agent` harness. When changing behavior, test both command results and the relevant print/TUI integration, then update published reference documentation.
