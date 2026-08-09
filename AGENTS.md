# AGENTS.md — agent-topo-harness

1. Read **SKILL.md** before changing spawn / vault / critical / compound policy.
2. Policy docs live under **docs/** — hosts (Virgil, etc.) keep thin pointers only.
3. Python helpers: `src/agent_topo_harness/`. Prefer extending modules over one-off scripts.
4. Host glue: `adapters/<host>/` (Hermes nest patch today). Do not bury doctrine in an adapter.
5. Apply scripts: `scripts/apply_*.sh` — re-run after model allowlist or Hermes upgrades.
6. Orthogonal to browser-harness (browser substrate) and to host memory/vault products.
