# Hermes adapter

Plugs **Compound Topologies** into Hermes / hermes-agent. Core doctrine stays host-agnostic in `SKILL.md` + `docs/`.

| Path | Role |
| :--- | :--- |
| `delegate_tool/` | Nest-orchestrator patch (TO can spawn leaves) |
| `hooks/` | Prefill companion: block Main durable writes; inject context |
| `prompts/` | Hermes Main prefill + per-turn context (spawn via `delegate_task`, Obsidian, Telegram) |
| `vault-obsidian.md` | Durable-memory → Obsidian mapping |
| `critical-telegram.md` | Critical ladder → Telegram UI |
| `virgil_bridge.py` | Optional Virgil `dual_write` helper (not in core package) |
| `../../scripts/apply_hermes_delegate_patch.sh` | Apply nest patch |
| `../../scripts/apply_agent_topo_harness.sh` | Wire config + this adapter’s hooks/prompts/models |

`delegate_task` remains a Hermes tool. This adapter owns Hermes-shaped spawn, hooks, vault paths, and Telegram — not the control-plane graph itself.

```bash
cd ~/Developer/agent-topo-harness
./scripts/apply_hermes_delegate_patch.sh
VIRGIL_ROOT=/path/to/Virgil ./scripts/apply_agent_topo_harness.sh
# restart Hermes gateway
```
