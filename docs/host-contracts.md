# Host contracts (Cursor ↔ Hermes)

Shared control-plane contracts both hosts must honor. Doctrine lives in this
package; hosts supply spawn/resume, chat, and storage paths.

## Sticky registry (shared fields)

Use `StickyRegistry` (`topology_harness.sticky`). Sticky is a **short-lived
resume map** — not a knowledge archive. See [sticky-registry.md](sticky-registry.md).

| Field / constant | Meaning |
| :--- | :--- |
| `host_session_id` | Opaque parent session key (`hermes_session_id` alias on load) |
| Handle `kind` | `orchestrator` (TO) or `tt` (API aliases: `topic_owner` / `leaf`) |
| `topic`, `lane` | Topic slug; TT lane id |
| `session_id` | Host child handle (Cursor Task label / Hermes session id) |
| `touched_at` | Unix time of last **TO touch** (idle TTL) |
| `topology_urn`, `composition`, `parent_run_id` | Graph telemetry siblings |
| `meta` | Ledgers, `active_lane`, brief digests |

Constants: `STICKY_HANDLE_KINDS`, `STICKY_PERSIST_KEYS`, `STICKY_IDLE_TTL_SECONDS`
(default 24h; env `TOPOLOGY_HARNESS_STICKY_IDLE_TTL`).

| Host | Registry path |
| :--- | :--- |
| Cursor | `.cursor/topology-sticky/registry.json` |
| Hermes (example host) | `$HERMES_HOME/state/sticky/<session>.json` (via host bridge) |

### Lifecycle

| Event | Action |
| :--- | :--- |
| Explicit done (gated brief) | `retire_topic(...)` then `release_topic(topic)` |
| Explicit abandon | `retire_topic(..., abandoned=True)` then `release_topic` |
| Idle ≥ 24h (no TO touch) | `purge_idle` → **release only** (never invent conclusions) |
| Host session end | `release_all` (+ delete sticky file) |

After load: call `purge_idle()` before injecting Main's card. Main card uses
`topics_for_main(limit=1)`; route coerce uses full live `open_topics()` after purge.

## Retire helper (both hosts)

Primary durable flush (blackboard / KG) — **not** the same as sticky release:

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
