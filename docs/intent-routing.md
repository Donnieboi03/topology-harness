# Intent routing

**Default: Planner** (`planner` / `open_topic`, or `resume` / `to_only` when sticky).
Open a TO for actionable / multi-step work. **Solo only** for easy direct Q&A.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

Chat chooses a route **internally** (helpers: `parse_route_decision`,
`coerce_route_with_registry`). Do **not** print `Route:` / `route:` /
RouteDecision JSON to the user — that is host plumbing, not UX.

**Separate layer:** `assert_spawn_policy` fan-token bag is defense-in-depth for
spawns — not this classifier. Don’t conflate them.

## Actions + aliases

| Alias (prefer) | Canonical | Meaning |
| :--- | :--- | :--- |
| `solo` | `main_only` | Easy direct Q&A only — stay in Chat |
| `helper` | `main_only` | Same route; host may spawn One helper Worker |
| `planner` | `open_topic` | New Planner topic — default for actionable work |
| `resume` | `to_only` | Continue open Planner; no Worker re-fan |
| — | `lens_resume` | Resume named Worker lanes |
| — | `full_refan` | Explicit breadth re-research |

**Solo (`solo` / `main_only`) — ONLY when ALL of:**

1. Direct question / opinion / meta — not “do / fix / implement / change”
2. Answerable in one turn with no multi-step action
3. No file edits and no unknown-surface research

**Otherwise → `planner` / `open_topic`** (or `resume` if a sticky Planner is open):
implement, edit, multi-step plans, research, multi-file / multi-surface work,
or any “do the thing” ask.

Prefer `planner` over `solo`. Prefer `resume` over `full_refan`.

## Host plumbing (not user-visible)

Hosts may parse JSON / `route:` lines via `parse_route_decision` when wiring
spawn. **Never surface those lines in the user-facing reply.**

```text
# host-internal only — not for Chat→user messages
route: planner kind: topic topic: fix-auth lenses: -
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
