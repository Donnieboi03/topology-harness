# Intent routing

**Default: Solo** (`solo` / `main_only`). Stay in Chat unless fan criteria match.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

Chat emits a `RouteDecision` in-band (JSON or `route:` line). No length heuristics.

**Separate layer:** `assert_spawn_policy` fan-token bag is defense-in-depth for
spawns — not this classifier. Don’t conflate them.

## Actions + aliases

| Alias (prefer) | Canonical | Meaning |
| :--- | :--- | :--- |
| `solo` | `main_only` | Default — stay in Chat |
| `helper` | `main_only` | Same route; host may spawn One helper Worker |
| `planner` | `open_topic` | New Planner topic — **only if fan criteria** |
| `resume` | `to_only` | Continue open Planner; no Worker re-fan |
| — | `lens_resume` | Resume named Worker lanes |
| — | `full_refan` | Explicit breadth re-research |

**Fan criteria (`planner` / `open_topic`) — ONLY when:**

1. Multi-file or multi-surface implement, or
2. Research with unknown surface area, or
3. User wants multiple / orthogonal angles

Prefer `solo` over `planner`. Prefer `resume` over `full_refan`.

## Emit

```text
route: solo kind: chat topic: - lenses: -
```

Helpers: `parse_route_decision`, `coerce_route_with_registry`, `ACTION_ALIASES`.

## Coerce

```python
reg.purge_idle()
decision = coerce_route_with_registry(
    parse_route_decision(raw),
    open_topics=reg.open_topics(),
)
# open_topic → to_only when topic already sticky-open
# Chat card: topics_for_main(limit=1)
```

See [sticky-registry.md](sticky-registry.md).
