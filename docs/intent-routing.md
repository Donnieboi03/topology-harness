# Intent routing (follow-ups)

Main decides how each user turn maps onto Compound Topologies. **No length or
keyword heuristics** — route on user intent. Prefer emitting the route **in-band**
on Main; a separate classify model is optional for measurement only.

## Actions

| Action | Meaning |
| :--- | :--- |
| `main_only` | Chit-chat / trivia — stay on Main |
| `open_topic` | First substantive work on a topic — create sticky TO; may fan TTs once |
| `to_only` | Continue open topic — **resume TO only** (default follow-up) |
| `lens_resume` | Resume one/few sticky TT lanes, then TO merge |
| `full_refan` | User explicitly wants breadth re-research — fan default TT lanes again |

Prefer **`to_only` over `full_refan`**. Prefer **`main_only` over opening a TO** for trivia.

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
| Harness | Schema + parse/validate + `coerce_route_with_registry` + prompt text |
| Main (live) | Emit route before spawn/resume |
| Host | Sticky registry + spawn/resume using the **coerced** action |
| Tests | Call router or inject `RouteDecision` — never `len(msg)` |

After parse/validate, hosts should:

```python
decision = coerce_route_with_registry(
    parse_route_decision(raw),
    open_topics=registry.open_topics(),
)
```

This fails-soft: if Main emits `open_topic` for an already-sticky topic, it becomes
`to_only` (no cold re-open).

See also [sticky-registry.md](sticky-registry.md), [tt-stubs.md](tt-stubs.md).
