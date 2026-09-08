# Sticky registry

Short-lived **resume map**: one Planner per topic, one Worker per `(topic, lane)`.
Not a knowledge archive — durable KB is [durable-memory.md](durable-memory.md).

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

## Retire vs release

| | Retire | Release |
| :--- | :--- | :--- |
| What | Flush gated brief → blackboard | Drop sticky handles |
| When | Explicit done / abandon | After retire; idle TTL; session end |
| Idle TTL | Never auto-retire | Yes — release only |

## Idle TTL

- Default 24h (`TOPOLOGY_HARNESS_STICKY_IDLE_TTL`)
- Refreshes on Planner touch / Worker create under that topic
- Hosts: `purge_idle()` after load (not inside `load`)

## API

```python
reg = StickyRegistry(host_session_id="…")
planner, _ = reg.get_or_create_planner("logging-logs-db")  # aliases: get_or_create_orchestrator / get_or_create_to
worker, _ = reg.get_or_create_worker("logging-logs-db", "scout_schema")  # alias: get_or_create_tt
reg.purge_idle()
reg.topics_for_main(limit=1)
reg.release_topic("logging-logs-db")
```

## Host turns

1. Load → `purge_idle()` → save if released
2. Chat card: `topics_for_main(limit=1)`
3. Coerce routes with full `open_topics()`
4. `planner`/`open_topic`: spawn Planner (+ optional Worker fan)
5. `resume`/`to_only`: resume Planner only
6. Done: `retire_topic` then `release_topic`

Shared fields: [host-contracts.md](host-contracts.md).
