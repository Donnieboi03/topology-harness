---
name: agent-topo-install
description: Install agent-topo-harness and wire Compound Topologies into the current agent host.
---

# Install — agent-topo-harness

Prefer a durable checkout: `~/Developer/agent-topo-harness` (alongside browser-harness).

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

**Not required:** Obsidian vault, Telegram, Hermes, OpenRouter — those are adapter choices.

## Hermes adapter

```bash
cd ~/Developer/agent-topo-harness
./scripts/apply_hermes_delegate_patch.sh
VIRGIL_ROOT=/path/to/Virgil ./scripts/apply_agent_topo_harness.sh
# restart Hermes gateway
```

| Piece | Source | Effect |
| :--- | :--- | :--- |
| Nest patch | `adapters/hermes/delegate_tool/` | TO can nest-delegate leaves |
| Prefill + hooks | `adapters/hermes/prompts/`, `adapters/hermes/hooks/` | Enforce compounds + Main durable-write deny (Obsidian) |
| Models | `config/models.yaml` | OpenRouter preference + allowlist |
| `external_dirs` | harness root (+ `$VIRGIL_ROOT/skills`) | Discovers this `SKILL.md` |

Mappings: [adapters/hermes/vault-obsidian.md](adapters/hermes/vault-obsidian.md), [adapters/hermes/critical-telegram.md](adapters/hermes/critical-telegram.md).

Set `OPENROUTER_API_KEY` when using OpenRouter via the apply script.

## Virgil

```bash
ln -sfn ~/Developer/agent-topo-harness /path/to/Virgil/agent-topo-harness
# wrappers: Virgil/scripts/apply_*.sh
```
