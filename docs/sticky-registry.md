# Sticky session registry

Portable control-plane piece: **one TO handle per topic** and **one TT
handle per `(topic, lane)`** — a **short-lived resume map**, not a knowledge
archive. Durable knowledge belongs on the blackboard / KG via
[`retire_topic`](durable-memory.md).

Handles live until: explicit `release_topic` / `release_all`, **idle TTL**
(default 24h without TO touch), or host session end.

## Why it lives in the harness

Sticky resume is host-agnostic policy. Hosts supply opaque `session_id` values
and spawn/resume primitives.

## Retire vs release

| | **Retire** (`retire_topic`) | **Release** (`release_topic` / `release_all`) |
| :--- | :--- | :--- |
| What | Flush gated brief → blackboard / KG | Drop sticky handles |
| When | Explicit done / abandon with real TO findings | Done after retire; idle TTL; session end |
| Idle TTL | Never auto-retire | **Yes** — release only (no invented conclusions) |

## Idle TTL (24h, TO-touch refresh)

- Default: `STICKY_IDLE_TTL_SECONDS = 24 * 3600` (override:
  `TOPOLOGY_HARNESS_STICKY_IDLE_TTL`).
- Clock resets on **TO touch**: `get_or_create_to` (create or resume), TO
  `bind_session`, `touch_topic`, or TT create/resume (bumps parent TO).
- Not refreshed by Main merely seeing the sticky card or by `load` / `purge_idle` scans.
- Hosts call `purge_idle()` after load (no auto-purge inside `load`).

## API

```python
from topology_harness.sticky import StickyRegistry, sticky_path_for_session

reg = StickyRegistry(host_session_id="abc")
to, created = reg.get_or_create_to("logging-logs-db")  # sets/refreshes touched_at
tt, _ = reg.get_or_create_tt("logging-logs-db", "scout_schema")
reg.bind_session(to, session_id="…")
released = reg.purge_idle()  # after load on host turn start
main_topics = reg.topics_for_main(limit=1)  # Main card
reg.save(sticky_path_for_session(state_dir, "abc"))
```

| Method | Behavior |
| :--- | :--- |
| `get_or_create_to(topic)` | Create or resume TO; **refreshes `touched_at`** |
| `get_or_create_tt(topic, lane)` | Create or resume TT; bumps parent TO `touched_at` |
| `touch_topic(topic)` | Host resume outside get_or_create |
| `topics_for_main(limit=1)` | Most-recently-touched topics for Main card |
| `purge_idle(ttl_seconds=None)` | Release idle TOs (no retire) |
| `set_active_lane` / ledgers / stall | TO `meta` blobs |
| `release_topic(topic)` | Drop TO + all TTs for that topic |
| `release_all()` | Clear registry (session end) |
| `save` / `load` | JSON persistence for host adapters |

Each handle may carry `touched_at`, graph telemetry siblings
(`topology_urn`, `composition`, `parent_run_id`) — see
[graph_telemetry.md](graph_telemetry.md).

Aliases: `get_or_create_orchestrator` (= `get_or_create_to`). Load still accepts
legacy JSON shapes `tos` / `leaves` / `kind: topic_owner|leaf` (normalized to
orchestrator / tt on load). Missing `touched_at` on load is treated as stale
by `purge_idle`.

Schema constants: `STICKY_HANDLE_KINDS`, `STICKY_PERSIST_KEYS`,
`STICKY_IDLE_TTL_SECONDS` (see also [host-contracts.md](host-contracts.md)).

## Host mapping

1. Key registry by **parent host session id**.
2. After load: `purge_idle()` then save if anything released.
3. Turn start: inject sticky card via **`topics_for_main(limit=1)`** (keep Main thin).
4. Coerce routes with full live `open_topics()` after purge.
5. On `open_topic`: spawn TO (+ optional TT fan); bind child session ids.
6. On `to_only`: resume TO only — do not respawn TTs.
7. On explicit done: `retire_topic` then `release_topic`.
8. On session end: `release_all` / delete sticky file.

## Not the same as provider prompt cache

Sticky = resume hygiene (avoid cold respawn while a topic is live). Provider
cache hits are separate. Blackboard / KG is the durable store.
