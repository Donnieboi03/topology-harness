# AGENTS.md — agent-topo-harness

1. Read **SKILL.md** — core control plane is host-agnostic.
2. Optional capabilities: **docs/durable-memory.md**, **docs/critical-escalation.md**. Do not assume vault/Telegram in core docs.
3. **Host owns glue** — nest patches, hooks, prefill, product mappings live in the agent host (e.g. Virgil), not under this repo.
4. Python: `src/agent_topo_harness/` — prefer `durable_memory` over vault naming in new code.
5. Orthogonal to host memory products and other substrate harnesses.
