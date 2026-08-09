# Durable memory (optional capability)

Compound Topologies do **not** require a vault, Obsidian, or any specific memory product.

When a host *has* a durable store (notes, KG, CRM, vector DB, …), writes follow one rule:

| Who | Durable store |
| :--- | :--- |
| **Topic Owner** | **Sole agent writer** when `persist` is enabled — merged/approved facts only |
| **Main** | **Never** writes durable memory |
| **Leaves** | **No** writes; read-only retrieval if tooling allowlist permits |
| **Human** | Correct the store offline when the graph/data is wrong (“brain surgery”) |

## Rules

1. `persist` is a **run flag**, not a topology. Values: `none` (default) or `durable`. Hosts may alias (`vault` → `durable`).
2. Without `persist: durable` (or host alias), agents do not upsert.
3. Scouts / planes / generators return findings to the TO — they never upsert.
4. TO upserts **merged, approved** facts only (no raw dumps, no speculative identity merges).
5. Prefer retrieve → reconcile in the brief → selective upsert.

## Telemetry

- `persist_durable` (bool) — was durable memory in scope for the run?
- `durable_writer` — always `topic_owner` when writes occur.

## Host mappings

| Host | Mapping |
| :--- | :--- |
| Hermes + Virgil Obsidian | See [`adapters/hermes/vault-obsidian.md`](../adapters/hermes/vault-obsidian.md) (`persist: vault` alias, path/tool denylist) |
| Other | Implement the same role gate; name your store in the adapter |

Core Python: `agent_topo_harness.durable_memory` (`vault_policy` is a compatibility alias).
