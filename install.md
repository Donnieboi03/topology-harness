---
name: agent-topo-install
description: Install agent-topo-harness and wire Compound Topologies into the current agent host.
---

# Install — agent-topo-harness

Prefer a durable checkout: `~/Developer/agent-topo-harness`.

```bash
cd ~/Developer/agent-topo-harness
uv sync
uv run pytest -q
```

## Any agent host

1. Put this repo’s `SKILL.md` on the agent’s skill path (symlink is fine).
2. Follow core spawn rules in `SKILL.md` (Main → flat Topic Owners → compounds).
3. Optional: map durable memory + critical channel per [docs/durable-memory.md](docs/durable-memory.md) and [docs/critical-escalation.md](docs/critical-escalation.md).
4. Prefer models from `config/models.yaml` when using harness routing.

**Host owns all glue** (spawn patch, hooks, prefill, vault/Telegram mappings). This repo ships doctrine + portable Python helpers only.

**Not required:** Obsidian vault, Telegram, Hermes, OpenRouter — those are host choices.

## Hermes / Virgil (reference host)

Glue lives in the Virgil checkout, not here:

```bash
cd /path/to/Virgil
./scripts/apply_hermes_delegate_patch.sh
./scripts/apply_agent_topo_harness.sh   # needs AGENT_TOPO_HARNESS or ~/Developer/agent-topo-harness
# restart Hermes gateway
```

| Piece | Host path (Virgil) | Effect |
| :--- | :--- | :--- |
| Nest patch | `patches/hermes/delegate_tool/` | TO can nest-delegate leaves |
| Prefill + hooks | `prompts/compound_topologies_*`, `hooks/enforce_compound_topologies.py` | Enforce compounds + Main durable-write deny |
| Models | harness `config/models.yaml` (applied by host script) | OpenRouter preference + allowlist |
| `external_dirs` | harness root (+ Virgil `skills/`) | Discovers this `SKILL.md` |

Mappings: Virgil `docs/compound-topologies/`.

```bash
ln -sfn ~/Developer/agent-topo-harness /path/to/Virgil/agent-topo-harness
```

Set `OPENROUTER_API_KEY` when using OpenRouter via the apply script.
