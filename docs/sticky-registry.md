# Sticky session registry

Portable control-plane piece: **one TO handle per topic** and **one TT
handle per `(topic, lane)`** until the host chat session ends (or Main /
TO releases the topic).

## Why it lives in the harness

Sticky resume is host-agnostic policy. Hosts supply opaque `session_id` values
and spawn/resume primitives.

## API

```python
from agent_topo_harness.sticky import StickyRegistry, sticky_path_for_session

reg = StickyRegistry(host_session_id="abc")
to, created = reg.get_or_create_to("logging-logs-db")
tt, _ = reg.get_or_create_tt("logging-logs-db", "scout_schema")
reg.bind_session(to, session_id="…")
reg.save(sticky_path_for_session(state_dir, "abc"))
```

| Method | Behavior |
| :--- | :--- |
| `get_or_create_to(topic)` | Create or resume TO (Topic Orchestrator) handle |
| `get_or_create_tt(topic, lane)` | Create or resume TT lane |
| `set_active_lane` / `get_active_lane` | Cursor lane on TO `meta["active_lane"]` |
| `set_task_ledger` / `get_task_ledger` | Magentic Task Ledger on TO meta |
| `set_progress_ledger` / `get_progress_ledger` | Progress Ledger on TO meta |
| `set_stall` / `get_stall` | Stall counters on TO meta |
| `release_topic(topic)` | Drop TO + all TTs for that topic |
| `save` / `load` | JSON persistence for host adapters |

Each handle may carry graph telemetry siblings (persisted with the registry):
`topology_urn`, `composition`, `parent_run_id` — see [graph_telemetry.md](graph_telemetry.md).

Ledger / stall / `active_lane` live in TO **`meta`** (no snapshot schema break).
See [to-brief-template.md](to-brief-template.md) and `agent_topo_harness.ledgers`.

Aliases: `get_or_create_orchestrator` / `get_or_create_leaf` still work. Load accepts
legacy `tos` / `leaves` / `kind: topic_owner|leaf` JSON.

## Host mapping

1. Key registry by **parent host session id**.
2. Turn start: inject a compact sticky card into Main context.
3. On `open_topic`: spawn TO (+ optional TT fan); bind child session ids.
4. On follow-up: pass `resume_session_id` or `topic:` / `lane:` so the host resumes.
5. On `to_only`: resume TO only — do not respawn TTs.
6. On `lens_resume` / `full_refan`: resume listed (or default) TT sessions, then TO merge.
7. On session end: `release_all` / delete sticky file.

## Not the same as provider prompt cache

Sticky = resume hygiene (avoid cold respawn). Provider cache hits are separate.
