# agent-topo-harness

**Compound Topologies** control plane — host-agnostic multi-agent graph doctrine (Main → flat Topic Owners → compounds of atoms).

Same packaging idea as [browser-harness](https://github.com/browser-use/browser-harness): a focused harness (`SKILL.md`, `docs/`, `src/`, `tests/`) you plug into any agent runtime that can spawn nested workers.

| Layer | What you get |
| :--- | :--- |
| **Doctrine** | Flat TOs, compounds (`debug-compound`, `research-build`, …), TO-owned brief, evidence gates, critical escalation |
| **Cost / inference** | Thin leaves vs fat Main — lower tokens, faster loops, bounded model allowlists |
| **Enforcement** | Prefill + hooks + `config/models.yaml` preference/fallback allowlist |
| **Adapters** | `adapters/hermes/` today; other hosts plug the same SKILL |

```
agent-topo-harness/
  SKILL.md
  install.md
  config/models.yaml
  prompts/ hooks/
  docs/
  src/agent_topo_harness/
  adapters/hermes/          # Hermes nest patch + notes
  scripts/                  # apply into a host profile
  tests/
```

## Quick start

```bash
cd ~/Developer/agent-topo-harness
./scripts/apply_hermes_delegate_patch.sh
# Optional: also register Virgil skills dir
VIRGIL_ROOT=~/Desktop/Code/Virgil ./scripts/apply_agent_topo_harness.sh
uv run pytest -q
uv run python -m agent_topo_harness.cost_smoke
```

Paste for an agent:

```text
Read ~/Developer/agent-topo-harness/SKILL.md and install.md.
Use Compound Topologies (Main → flat Topic Owners → compounds of atoms).
```

Details: [install.md](install.md).

## License

MIT (unless otherwise noted when published).
