# Zeta architecture

Zeta preserves Pi's separation of concerns:

```text
AgentHarness = reusable agent brain
AgentSession = coding-agent environment
TUI = one possible frontend
```

Packages:

- `zeta_ai`: provider/model streaming and provider-neutral events.
- `zeta_agent`: portable harness, loop, tools, messages, events, and sessions.
- `zeta_coding`: CLI application, resources, skills, extensions, commands, persistence, rendering, and TUI integration.

Keep `zeta_agent` independent of Typer, Rich, Textual, application resource locations, and provider-specific assumptions. Prefer typed data models, explicit async boundaries, deterministic fakes, and small abstractions.

In a Zeta checkout, read `AGENTS.md`, `website/content/internals/architecture.md`, and relevant `dev-notes/architecture/` documents before broad architectural changes.
