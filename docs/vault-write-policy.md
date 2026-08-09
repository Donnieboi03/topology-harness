# Vault write policy (TO-only)

Durable Obsidian / KG writes under Compound Topologies:

| Who | Vault |
| :--- | :--- |
| **Topic Owner** | **Sole agent writer** when `persist: vault` — approved facts after merge only |
| **Main** | **Never** vault-write |
| **Leaves** | **No** vault write; read-only retrieval OK if tooling allowlist permits |
| **Human** | **Brain surgery** — edit notes on disk when the graph is wrong |

## Rules

1. `persist: vault` is a run flag, not a topology. Without it, agents do not upsert.
2. Scouts / planes / generators never call vault upsert tools — they return findings to the TO.
3. TO upserts **merged, approved** facts only (no raw dump, no speculative identity merges).
4. Prefer retrieve → reconcile in the brief → selective upsert.
5. Wrong graph? Stop agents from “fixing” via Main chat; human edits on disk (**brain surgery**), then continue.

## Telemetry

When vault activity occurs, record `vault_writer=topic_owner` (never `main` / `leaf`). See [graph_telemetry.md](graph_telemetry.md).
