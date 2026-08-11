# Graph telemetry

## Topology URN

Shape: `topology:<paradigm>:<workflow-slug>:<ulid>`

### paradigm (atomics only)

Only **three** atomics get URN paradigm tags:

| Atom (user verb) | Paradigm |
| :--- | :--- |
| `research-swarm` / `swarm` | `swarm` |
| `plane-audit` / `plane` (legacy `planes`) | `plane` |
| `verify-claims` / `cove` | `cove` |

**Not atomics** (do **not** put these in the URN paradigm segment):

- `refine-loop` / Gen+Critiquer — compound **wiring**; record under `composition`
- `debate`, `to-brief`, consul roles — patterns / roles, not atomic paradigms

Fail-closed helpers: `paradigm_for_atom`, `assert_atomic_paradigm`, `NotAtomicError`.

Control-plane tags (not atomics):

- Topic Orchestrator → `topic` (or explicit `moa`)
- Informal Main → single TT → `leaf`
- Named compound id may appear as paradigm when no atom is set (`resolve_paradigm(compound_id=…)`)

### workflow-slug

Stable handle identity — **not** goal prose:

| Actor | Slug |
| :--- | :--- |
| TT | `{topic}--{lane}` |
| TO | `{topic}--to` |

Helper: `workflow_slug_for(topic, lane, role=…)`.

### Examples

```
topology:topic:auth-refresh--to:01HZ…
topology:plane:auth-refresh--security:01HZ…
topology:swarm:auth-refresh--scout-schema:01HZ…
topology:cove:claims-pass--verifier:01HZ…
topology:leaf:quick-fix--default:01HZ…   # informal Main→TT only
```

## Sibling fields (not stuffed into the URN)

| Field | Meaning |
| :--- | :--- |
| `composition` | Compound id / freeform wiring (`composition_field`) — **home for refine-loop** |
| `control_plane` | `main` \| `orchestrator` \| `tt` |
| `topic` | Kebab topic slug |
| `lane` | TT lane id (omit for TO) |
| `sticky` | Whether this worker resumed a prior session |
| `durable_writer` | Always `orchestrator` when persist writes occur |
| `parent_run_id` | Shared across one fan-out (siblings share) |
| `persist` | `none` \| `durable` (host alias `vault`) |

Helpers: `make_topology_urn`, `workflow_slug_for`, `resolve_paradigm`,
`paradigm_for_atom`, `composition_field`, `sibling_telemetry_fields`.

Sticky handles persist `topology_urn`, `composition`, and `parent_run_id`
alongside `session_id` (see [sticky-registry.md](sticky-registry.md)).

## Fail-closed host hooks

| Helper | Behavior |
| :--- | :--- |
| `assert_can_write(role)` | Only TO may durable-write |
| `assert_spawn_policy(...)` | Blocks Main→leaf for topic/substantive/atomic work; returns URN paradigm |
| `assert_topic_open` / `topo_gate(registry)` | Topic must have sticky TO |
| `coerce_route_with_registry` | `open_topic` → `to_only` when topic already open |
| `validate_route_decision` | Route schema only |
