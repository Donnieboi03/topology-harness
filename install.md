---
name: agent-topo-install
description: Install agent-topo-harness and wire Compound Topologies into the current agent host.
---

# Install — agent-topo-harness

Clone once into a durable path (prefer `~/Developer/agent-topo-harness`, same pattern as browser-harness).

```bash
# if not already present
git clone <repo-url> ~/Developer/agent-topo-harness
cd ~/Developer/agent-topo-harness
uv sync   # or: uv pip install -e ".[dev]" / uv run pytest
```

## Any agent host

1. Put this repo’s `SKILL.md` on the agent’s skill path (symlink is fine).
2. Follow spawn rules in `SKILL.md` (Main → flat Topic Owners → compound leaves).
3. Prefer models from `config/models.yaml` (edit allowlist there).

The control plane is **not** Hermes-specific. Only the adapter under `adapters/hermes/` knows about `delegate_task` / Hermes hooks.

## Hermes adapter (Virgil / hermes-agent)

```bash
cd ~/Developer/agent-topo-harness
./scripts/apply_hermes_delegate_patch.sh
VIRGIL_ROOT=/path/to/Virgil ./scripts/apply_agent_topo_harness.sh
# restart Hermes gateway
```

| Piece | Source | Effect |
| :--- | :--- | :--- |
| Nest patch | `adapters/hermes/delegate_tool/` | TO can nest-delegate leaves |
| `external_dirs` | harness root (+ `$VIRGIL_ROOT/skills`) | Discovers this `SKILL.md` |
| Prefill + hooks | `prompts/`, `hooks/` | Enforce compounds + block Main vault writes |
| Models | `config/models.yaml` | OpenRouter preference + allowlisted fallbacks |

Re-run the nest patch after every `hermes` upgrade. Re-run apply after editing `config/models.yaml`.

Set `OPENROUTER_API_KEY` (or Hermes `auth.json`) when using OpenRouter.

## Virgil checkout wiring

Virgil should **symlink** or path-depend on this repo:

```bash
# example
ln -sfn ~/Developer/agent-topo-harness /path/to/Virgil/agent-topo-harness
```

Virgil `pyproject.toml` `pythonpath` / thin wrappers under `Virgil/scripts/` call into this checkout.

## Smoke

```bash
cd ~/Developer/agent-topo-harness
uv run pytest -q
uv run python -m agent_topo_harness.cost_smoke
```
