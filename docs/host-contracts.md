# Host contracts

Shared sticky + retire + escalation every host must honor.

> **Aliases:** Chat = Main · Planner = TO / orchestrator · Worker = TT / leaf

## Sticky

| Field | Meaning |
| :--- | :--- |
| `host_session_id` | Opaque parent key (`hermes_session_id` alias on load) |
| Handle `kind` | `orchestrator` (Planner) or `tt` (Worker) |
| `topic` / `lane` | Topic slug; Worker lane |
| `session_id` | Child handle |
| `touched_at` | Last Planner touch (idle TTL) |
| `meta` | Ledgers, brief digests |

Constants: `STICKY_HANDLE_KINDS`, `STICKY_PERSIST_KEYS`, `STICKY_IDLE_TTL_SECONDS` (24h).

| Binding | Path |
| :--- | :--- |
| Cursor | `.cursor/topology-sticky/registry.json` |
| Hermes (example) | host bridge under `$HERMES_HOME/state/sticky/` |

| Event | Action |
| :--- | :--- |
| Done | `retire_topic` then `release_topic` |
| Abandon | `retire_topic(..., abandoned=True)` then release |
| Idle ≥ TTL | `purge_idle` → release only |
| Session end | `release_all` |

Details: [sticky-registry.md](sticky-registry.md).

## Retire flush

```python
retire_topic("planner", topic, brief, path=kb_path)  # aliases: orchestrator / to
# then StickyRegistry.release_topic(topic)
```

Brief regions: [durable-memory.md](durable-memory.md). Mid-topic: Planner-gated
`append_evidence` / `upsert_open_questions` only.

## Critical escalation

Worker → Planner → Chat → **host human channel**. Do not bury criticals in
Worker stubs. Host maps the final hop (Telegram, ticket, etc.). Chat never
silently swallows a Planner escalate.

## Adapters

- Cursor: [adapters/cursor.md](adapters/cursor.md)
- Other hosts: bind sticky paths + nest depth; package stays host-agnostic
