# Graph telemetry

Floor for run identity and composition siblings. Helpers live in
`topology_harness` (`make_topology_urn`, `composition_field`,
`sibling_telemetry_fields`, fail-closed asserts).

## Topology URN

Shape: `topology:<paradigm>:<workflow-slug>:<ulid>`

**Paradigm segment = atom only:** `swarm` | `plane` | `cove` | `shard`.

Do **not** put combinators or transitions in the paradigm segment.
For `cycle(plane, revise)`, the URN paradigm stays `plane`; `combinator` /
`transition` are siblings.

Control-plane / informal tags (not atomics): `topic`, `leaf`; named compound id
may appear when no atom is set (`resolve_paradigm(compound_id=…)`).

Workflow-slug: stable handle identity — TT `{topic}--{lane}`, TO `{topic}--to`
(`workflow_slug_for`).

```
topology:plane:auth-refresh--security:01HZ…
topology:swarm:auth-refresh--scout-schema:01HZ…
topology:cove:claims-pass--verifier:01HZ…
topology:shard:api-client--mailer:01HZ…
```

## Sibling fields

| Field | Meaning |
| :--- | :--- |
| `combinator` | Public menu: `cycle` |
| `transition` | Public menu: `revise` — only with `combinator=cycle` |
| `composition` | Compound id + atoms + combinator/transition (`composition_field`) |
| `control_plane` | `main` \| `orchestrator` \| `tt` |
| `topic` / `lane` | Topic slug; TT lane (omit for TO) |
| `parent_run_id` | Shared across one fan-out |
| `sticky` / `durable_writer` / `persist` | Resume flag; writer role; persist mode |

`combinator` / `transition` omitted when unset.

## Schema

`composition_field()` stamps **`schema_version=2`** (`COMPOSITION_SCHEMA_VERSION`):
atom in the URN paradigm; `combinator` / `transition` as siblings.

Sticky handles persist `topology_urn`, `composition`, and `parent_run_id`
alongside `session_id` (see [sticky-registry.md](sticky-registry.md)).
