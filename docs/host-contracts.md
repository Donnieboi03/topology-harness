# Host contracts (Cursor ↔ Hermes)

Shared control-plane contracts both hosts must honor. Doctrine lives in this
package; hosts supply spawn/resume, chat, and storage paths.

## Sticky registry (shared fields)

Use `StickyRegistry` (`topology_harness.sticky`).

| Field / constant | Meaning |
| :--- | :--- |
| `host_session_id` | Opaque parent session key (`hermes_session_id` alias on load) |
| Handle `kind` | `orchestrator` (TO) or `tt` (API aliases: `topic_owner` / `leaf`) |
| `topic`, `lane` | Topic slug; TT lane id |
| `session_id` | Host child handle (Cursor Task label / Hermes session id) |
| `topology_urn`, `composition`, `parent_run_id` | Graph telemetry siblings |
| `meta` | Ledgers, `active_lane`, brief digests |

Constants: `STICKY_HANDLE_KINDS`, `STICKY_PERSIST_KEYS`.

| Host | Registry path |
| :--- | :--- |
| Cursor | `.cursor/topology-sticky/registry.json` |
| Hermes (example host) | `$HERMES_HOME/state/sticky/<session>.json` (via host bridge) |

On topic close: flush durable KB (below), then `release_topic(topic)`.

## Retire helper (both hosts)

Primary durable flush:

```python
from topology_harness import Blackboard, retire_topic

retire_topic(
    "orchestrator",
    topic,
    brief,  # typed regions — see durable-memory.md
    path=kb_path,  # host-configurable JSONL
    abandoned=False,
)
# then StickyRegistry.release_topic(topic)
```

Contract details and region schema: [durable-memory.md](durable-memory.md).

Mid-topic (still TO-gated): `Blackboard.append_evidence`,
`Blackboard.upsert_open_questions`. Main / TT must not write conclusions.

## Adapters

- Cursor: [adapters/cursor.md](adapters/cursor.md)
- Hermes (or any other host): bind sticky paths, spawn/resume, and nest depth
  in the host; this package stays host-agnostic.
