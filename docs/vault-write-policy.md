# Persist write policy

Compound Topologies do not assume every agent has a durable store. `persist:
durable` is optional.

| Doc | Role |
| :--- | :--- |
| [durable-memory.md](durable-memory.md) | Policy: TO-only writes |
| Host adapter | Maps `durable` to a concrete backend |

Gate helpers: `topology_harness.durable_memory.assert_can_write`.
