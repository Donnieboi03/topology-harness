# agent-topo-harness

**Compound Topologies** — host-agnostic multi-agent control plane (Main → flat Topic Owners → compounds of atoms).

Same packaging idea as [browser-harness](https://github.com/browser-use/browser-harness): a focused harness you plug into any agent runtime that can spawn nested workers.

| Layer | What you get |
| :--- | :--- |
| **Doctrine** | Flat TOs, compounds, TO-owned brief, evidence gates |
| **Optional** | Durable memory (TO-only writes), critical human channel — contracts, not product locks |
| **Cost / inference** | Thin leaves vs fat Main; preference + model allowlist |
| **Adapters** | `adapters/hermes/` (spawn patch, Obsidian, Telegram, hooks) |

```
agent-topo-harness/
  SKILL.md docs/ src/          # portable core
  config/models.yaml
  adapters/hermes/             # Hermes/Virgil only
  scripts/ tests/
```

## Quick start

```bash
cd ~/Developer/agent-topo-harness
uv run pytest -q
uv run python -m agent_topo_harness.cost_smoke
# Hermes host:
./scripts/apply_hermes_delegate_patch.sh
VIRGIL_ROOT=~/Desktop/Code/Virgil ./scripts/apply_agent_topo_harness.sh
```

Paste for an agent:

```text
Read ~/Developer/agent-topo-harness/SKILL.md.
Use Compound Topologies. Vault/Telegram are optional host mappings under adapters/hermes/.
```

Details: [install.md](install.md).

## License

MIT
