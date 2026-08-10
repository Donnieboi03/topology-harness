# Intent routing (follow-ups)

Main decides how each user turn maps onto Compound Topologies. **No length or
keyword heuristics** — route on user intent. Prefer emitting the route **in-band**
on Main; a separate classify model is optional for measurement only.

## Actions

| Action | Meaning |
| :--- | :--- |
| `main_only` | Chit-chat / trivia — stay on Main |
| `open_topic` | First substantive work on a topic — create sticky Orchestrator; may fan TTs once |
| `to_only` | Continue open topic — **resume Orchestrator only** (default follow-up) |
| `lens_resume` | Resume one/few sticky TT lanes, then Orchestrator merge |
| `full_refan` | User explicitly wants breadth re-research — fan default TT lanes again |

Prefer **`to_only` over `full_refan`**. Prefer **`main_only` over opening an Orchestrator** for trivia.

## Emit format

JSON (preferred) or one line:

```text
route: to_only kind: topic topic: logging-logs-db lenses: -
```

Helpers: `agent_topo_harness.routing`. Example classify model: `roles.router` in
[config/models.yaml](../config/models.yaml).

## Integration

| Layer | Role |
| :--- | :--- |
| Harness | Schema + parse/validate + system prompt text |
| Main (live) | Emit route before spawn/resume |
| Host | Sticky registry + spawn/resume using the action |
| Tests | Call router or inject `RouteDecision` — never `len(msg)` |

See also [sticky-registry.md](sticky-registry.md), [tt-stubs.md](tt-stubs.md).
