# Vault write policy → durable memory

**Portable policy:** [durable-memory.md](durable-memory.md).

Compound Topologies do not assume every agent has a vault. “Vault” is a **Virgil/Hermes Obsidian** mapping of the optional `persist: durable` capability.

| Doc | Role |
| :--- | :--- |
| [durable-memory.md](durable-memory.md) | Core: TO-only writes when persist enabled |
| Virgil `docs/compound-topologies/vault-obsidian.md` | Host: Obsidian paths, `vault_store_fact`, `persist: vault` alias |

Compatibility: `agent_topo_harness.vault_policy` re-exports `durable_memory`.
