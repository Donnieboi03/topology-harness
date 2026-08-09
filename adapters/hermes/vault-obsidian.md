# Hermes + Virgil — Obsidian vault mapping

Maps core [durable-memory](../../docs/durable-memory.md) onto Virgil’s Obsidian / KG store.

| Core | This host |
| :--- | :--- |
| `persist: durable` | Also accept `persist: vault` (alias) |
| Durable store | Obsidian vault under `obsidian/` (+ related upsert tools) |
| TO-only writes | Topic Owner when `persist: vault` |
| Main never writes | Enforced by `hooks/enforce_compound_topologies.py` |
| Brain surgery | Human edits `obsidian/**/*.md` on disk |

## Blocked from Main (hook)

Tools / signals (non-exhaustive):

- `vault_store_fact`, `vault_upsert`, `vault_write`, `store_fact`
- Paths containing `obsidian/people`, `obsidian/orgs`, `obsidian/reflections`
- Shell redirects into `obsidian/`

## Prefill / context

Hermes-only prompts live in `adapters/hermes/prompts/` (applied by `scripts/apply_agent_topo_harness.sh`).
