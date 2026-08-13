# Install

## Package

```bash
cd ~/Developer/topology-harness   # or your checkout
uv sync
uv tool install -e .              # puts `topology-harness` on PATH
topology-harness --doctor
uv run pytest
```

Python package root: `src/topology_harness/`.

## Cursor integration (Cursor as host)

Same ergonomics as `browser-harness`: when you install the rule/skill here,
**this Cursor chat is Main** and Cursor `Task` sub-agents are TO / TT.

1. **Always-on rule** — `~/.cursor/rules/topology-harness.mdc`  
   (`alwaysApply: true`) — autonomous routing + Cursor role map.
2. **Personal skill** — `~/.cursor/skills/topology-harness/` → this repo’s
   `SKILL.md` + `docs/` (symlinked).
3. **Adapter doc** — [docs/adapters/cursor.md](docs/adapters/cursor.md).
4. **CLI on PATH** — `topology-harness`:

```bash
topology-harness doctrine          # compact control-plane card
topology-harness cursor-map        # Main/TO/TT → Cursor Task binding
topology-harness --doctor          # imports + cost smoke + Cursor wiring
topology-harness compounds
topology-harness cost-smoke
topology-harness <<'PY'
print(ATOMIC_PARADIGMS)
PY
```

Sticky (best-effort on Cursor): workspace `.cursor/topology-sticky/registry.json`.

Re-check after upgrades:

```bash
topology-harness --doctor
```

## Host responsibilities

This harness does **not** spawn workers. The agent host must:

1. Enforce nest depth / role (Main → TO → TT only).
2. Call **`assert_spawn_policy`** before every child mint (blocks Main→leaf for
   topic / substantive / atomic work).
3. Persist sticky session ids (`StickyRegistry` + host spawn/resume).
4. Coerce routes with `coerce_route_with_registry` after parse.
5. Inject Main policy (prefill / system card); Main emits `RouteDecision`
   in-band (`route:` / JSON).
6. Map optional `persist: durable` to the host’s store (TO-only writes via
   `assert_can_write`).
7. Map critical escalation to the host’s human channel.

See [README.md](README.md) utilization section and doctrine under `docs/`.

## Config

[config/models.yaml](config/models.yaml) is an **example** role→model allowlist.
Hosts copy or generate equivalent config; do not commit API keys here.

| Role | Model |
| :--- | :--- |
| Main | `google/gemini-2.5-flash-lite` |
| TO | `google/gemini-3-flash-preview` |
| `swarm` / `plane` | `google/gemini-3.5-flash-lite` |
| `cove` | `google/gemini-3.1-flash-lite` |
| `shard` | `google/gemini-3.6-flash` |

Environment for host session DB (when using host-side cost rollups):

```bash
export TOPOLOGY_HARNESS_STATE_DB=/path/to/host/sessions.db
```

No default home-directory DB path is shipped.

## Security

- Do not commit `.env`, API keys, or personal session databases.
- Prefer allowlisted models (`assert_allowed` / `roles.*`).
- Sticky JSON holds opaque session ids only — treat host state dirs as private.
