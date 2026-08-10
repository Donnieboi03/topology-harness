# Graph telemetry

## Topology URN

Shape: `topology:<paradigm>:<workflow-slug>:<ulid>`

### paradigm

From atom mapping (`paradigm_for_atom` / `resolve_paradigm`):

| Atom | Paradigm |
| :--- | :--- |
| `research-swarm` | `swarm` |
| `refine-loop` | `refine` |
| `debate` | `debate` |
| `plane-audit` | `planes` |
| `verify-claims` | `cove` |
| `to-brief` | `topic` |

- **Never** default `leaf` for named compounds — use the compound/atom tag.
- `leaf` only for true Main → single informal TT.
- Topic Orchestrator (TO) → `topic` (or explicit `moa`).

### workflow-slug

Stable handle identity — **not** goal prose:

| Actor | Slug |
| :--- | :--- |
| TT | `{topic}--{lane}` |
| TO | `{topic}--to` |

Helper: `workflow_slug_for(topic, lane, role=…)`.

### Examples

```
topology:topic:virgil-codebase-audit--to:01HZ…
topology:planes:virgil-codebase-audit--implementation:01HZ…
topology:swarm:auth-refresh--scout-schema:01HZ…
topology:leaf:quick-fix--default:01HZ…   # informal Main→TT only
```

## Sibling fields (not stuffed into the URN)

| Field | Meaning |
| :--- | :--- |
| `composition` | Compound id / freeform wiring (`composition_field`) |
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
