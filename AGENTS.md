# AGENTS.md — agent-topo-harness

1. Read **SKILL.md** — core control plane is host-agnostic.
2. Optional capabilities: **docs/durable-memory.md**, **docs/critical-escalation.md**. Do not assume vault/Telegram in core docs.
3. Host glue only under **adapters/<host>/** (Hermes: nest patch, Obsidian, Telegram, hooks/prompts).
4. Python: `src/agent_topo_harness/` — prefer `durable_memory` over vault naming in new code.
5. Orthogonal to browser-harness (browser substrate) and to host memory products.
