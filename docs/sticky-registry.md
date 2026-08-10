# Sticky session registry

Portable control-plane piece: **one Orchestrator handle per topic** and **one TT
handle per `(topic, lane)`** until the host chat session ends (or Main /
Orchestrator releases the topic).

## Why it lives in the harness

Sticky resume is host-agnostic policy. Hosts supply opaque `session_id` values
and spawn/resume primitives.

## API

```python
from agent_topo_harness.sticky import StickyRegistry, sticky_path_for_session

reg = StickyRegistry(host_session_id="abc")
orch, created = reg.get_or_create_orchestrator("logging-logs-db")
tt, _ = reg.get_or_create_tt("logging-logs-db", "scout_schema")
reg.bind_session(orch, host_session_id="…")
reg.save(sticky_path_for_session(state_dir, "abc"))
```

| Method | Behavior |
| :--- | :--- |
| `get_or_create_orchestrator(topic)` | Create or resume Orchestrator handle |
| `get_or_create_tt(topic, lane)` | Create or resume TT lane |
| `release_topic(topic)` | Drop Orchestrator + all TTs for that topic |
| `save` / `load` | JSON persistence for host adapters |

Aliases: `get_or_create_to` / `get_or_create_leaf` still work. Load accepts
legacy `tos` / `leaves` / `kind: topic_owner|leaf` JSON.

## Host mapping

1. Key registry by **parent host session id**.
2. Turn start: inject a compact sticky card into Main context.
3. On `open_topic`: spawn Orchestrator (+ optional TT fan); bind child session ids.
4. On follow-up: pass `resume_session_id` or `topic:` / `lane:` so the host resumes.
5. On `to_only`: resume Orchestrator only — do not respawn TTs.
6. On `lens_resume` / `full_refan`: resume listed (or default) TT sessions, then Orchestrator merge.
7. On session end: `release_all` / delete sticky file.

## Not the same as provider prompt cache

Sticky = resume hygiene (avoid cold respawn). Provider cache hits are separate.
