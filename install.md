# Install

## Package

```bash
cd /path/to/agent-topo-harness
uv sync
uv run python -m agent_topo_harness.cost_smoke
uv run pytest
```

Python package root: `src/agent_topo_harness/`.

## Host responsibilities

This harness does **not** spawn workers. The agent host must:

1. Enforce nest depth / role (Main → TO → TT only).
2. Persist sticky session ids (`StickyRegistry` + host spawn/resume).
3. Inject Main policy (prefill / system card) including intent `route:` lines.
4. Map optional `persist: durable` to the host’s store (TO-only writes).
5. Map critical escalation to the host’s human channel.

Use `StickyRegistry` + intent `route:` decisions + TT stubs (see docs).

## Config

[config/models.yaml](config/models.yaml) is an **example** role→model allowlist.
Hosts copy or generate equivalent config; do not commit API keys here.

Environment for session-tree rollups:

```bash
export AGENT_TOPO_STATE_DB=/path/to/host/sessions.db
```

No default home-directory DB path is shipped.

## Security

- Do not commit `.env`, API keys, or personal session databases.
- Prefer allowlisted models (`assert_allowed` / `roles.*`).
- Sticky JSON holds opaque session ids only — treat host state dirs as private.
