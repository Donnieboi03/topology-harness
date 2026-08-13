# Intent routing (follow-ups)

Main decides how each user turn maps onto Compound Topologies. **No length or
keyword heuristics** — route on user intent. Main emits a **`RouteDecision`
in-band** on the live turn (JSON or a `route:` line). Do not use a separate
classify-only model for live turns.

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

Helpers: `topology_harness.routing` (`RouteDecision`, `parse_route_decision`,
`coerce_route_with_registry`). Optional measurement may reuse
`ROUTER_SYSTEM_PROMPT` as prompt text only — live product path is Main in-band.

## Integration

| Layer | Role |
| :--- | :--- |
| Harness | Schema + parse/validate + `coerce_route_with_registry` + prompt text |
| Main (live) | Emit `RouteDecision` before spawn/resume |
| Host | Sticky registry + spawn/resume using the **coerced** action |
| Tests | Inject `RouteDecision` — never `len(msg)` |

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
