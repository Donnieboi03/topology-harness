# Optional measurement helpers

Optional A/B and session-tree helpers for hosts that want to **measure** spend.
Not part of Compound Topologies doctrine — control-plane value is isolation,
sticky resume, scoped tools, and evidence gates.

| Helper | Role |
| :--- | :--- |
| `cost_A` / `cost_B` | Synthetic one-turn models |
| `analyze_session_tree` | Roll up tokens from a host session DB |
| `python -m agent_topo_harness.cost_smoke` | Sanity check Main-only vs forced-TO on trivia |

Rates and DB paths are host-specific (`AGENT_TOPO_STATE_DB`). Do not mix matrices
across hosts.
