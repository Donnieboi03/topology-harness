# Install

## Package

```bash
cd /path/to/topology-harness
uv sync
uv run python -m topology_harness.cost_smoke
uv run pytest
```

Python package root: `src/topology_harness/`.

## Host responsibilities

This harness does **not** spawn workers. The agent host must:

1. Enforce nest depth / role (Main → TO → TT only).
2. Call **`assert_spawn_policy`** before every child mint (blocks Main→leaf for
   topic / substantive / atomic work).
3. Persist sticky session ids (`StickyRegistry` + host spawn/resume).
4. Coerce routes with `coerce_route_with_registry` after parse.
5. Inject Main policy (prefill / system card) including intent `route:` lines.
6. Map optional `persist: durable` to the host’s store (TO-only writes via
   `assert_can_write`).
7. Map critical escalation to the host’s human channel.

See [README.md](README.md) utilization section and doctrine under `docs/`.

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
