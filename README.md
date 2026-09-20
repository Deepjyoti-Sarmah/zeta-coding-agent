# Zeta

A minimalist Pi-style coding-agent harness in Python.

Three small packages:

- `zeta_ai` — provider layer; normalizes model responses into one event stream.
- `zeta_agent` — the harness; the loop that turns events into tool calls.
- `zeta_coding` — the agent; files, shell, sessions, skills, and a terminal UI.

## Install

```sh
uv tool install zeta-ai
```

## Run

```sh
zeta
```

## Website

The landing page lives in [`web/`](./web) — a React + Vite app, ready to deploy.

```sh
cd web
npm install
npm run dev
```
