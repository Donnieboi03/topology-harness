# agent-topo-harness

**Compound Topologies** — host-agnostic multi-agent control plane (Main → flat Topic Owners → compounds of atoms).

A focused harness you plug into any agent runtime that can spawn nested workers.

| Layer | What you get |
| :--- | :--- |
| **Doctrine** | Flat TOs, compounds, TO-owned brief, evidence gates |
| **Optional** | Durable memory (TO-only writes), critical human channel — contracts, not product locks |
| **Cost / inference** | Main gates TO vs in-chat; thin topic leaves; model allowlist. **Not** “always cheaper than monolith” — see [docs/cost-analysis.md](docs/cost-analysis.md) |
| **Host glue** | Owned by the agent host (spawn patch, hooks, prefill, vault/Telegram) — not this repo |

```
agent-topo-harness/
  SKILL.md docs/ src/          # portable core
  config/models.yaml
  tests/
```

## Quick start

```bash
cd ~/Developer/agent-topo-harness
uv run pytest -q
uv run python -m agent_topo_harness.cost_smoke
# Hermes/Virgil host (glue lives in Virgil):
cd /path/to/Virgil
./scripts/apply_hermes_delegate_patch.sh
./scripts/apply_agent_topo_harness.sh
```

Paste for an agent:

```text
Read ~/Developer/agent-topo-harness/SKILL.md.
Use Compound Topologies. Host maps optional vault/Telegram; see install.md.
```

Details: [install.md](install.md).

## License

MIT
