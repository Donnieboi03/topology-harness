# Install

## Package

```bash
cd ~/Developer/topology-harness   # or your checkout
uv sync
uv tool install -e .
topology-harness --doctor
uv run pytest
```

Package root: `src/topology_harness/`.

## Cursor (Chat = this chat)

1. **Always-on rule** — copy/symlink [docs/adapters/cursor-rule.mdc](docs/adapters/cursor-rule.mdc)  
   → `~/.cursor/rules/topology-harness.mdc` (`alwaysApply: true`).
2. **Skill** — `~/.cursor/skills/topology-harness/` → this repo’s `SKILL.md` + `docs/`.
3. **Adapter** — [docs/adapters/cursor.md](docs/adapters/cursor.md).
4. **CLI:**

```bash
topology-harness doctrine
topology-harness cursor-map
topology-harness --doctor
topology-harness compounds
```

Sticky (best-effort): `.cursor/topology-sticky/registry.json`.

## Host must

1. Nest depth: Chat → Planner → Worker only.
2. Call `assert_spawn_policy` before every child mint.
3. Persist sticky; `purge_idle` after load; coerce routes.
4. Chat emits `RouteDecision` in-band (`solo` / `helper` / `planner` / `resume` aliases OK).
5. Map `persist: durable` → store; Planner-only writes via `assert_can_write`.
6. Escalate criticals Chat → host human channel (see [docs/host-contracts.md](docs/host-contracts.md)).

## Config example

[config/models.yaml](config/models.yaml) — role→model allowlist. No API keys here.

| Role | Model |
| :--- | :--- |
| Chat | `google/gemini-3.1-flash-lite` |
| Planner | `google/gemini-3-flash-preview` |
| `swarm` / `plane` | `google/gemini-3.5-flash-lite` |
| `cove` | `google/gemini-3.1-flash-lite` |
| `shard` | `google/gemini-3.6-flash` |

```bash
export TOPOLOGY_HARNESS_STATE_DB=/path/to/host/sessions.db
```

## Security

No `.env` / keys / personal DBs in git. Sticky JSON = opaque session ids only.
