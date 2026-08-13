# Optional measurement helpers

Optional A/B helpers for hosts that want to **measure** spend.
Not part of Compound Topologies doctrine — control-plane value is isolation,
sticky resume, scoped tools, and evidence gates.

| Helper | Role |
| :--- | :--- |
| `cost_A` / `cost_B` | Synthetic one-turn models |
| `python -m topology_harness.cost_smoke` | Sanity check Main-only vs forced-TO on trivia |

Example cast rates align with [config/models.yaml](../config/models.yaml):
Main `google/gemini-2.5-flash-lite`, TO `google/gemini-3-flash-preview`, atoms
as in that file.

Host session DB (when doing host-side rollups outside this package):

```bash
export TOPOLOGY_HARNESS_STATE_DB=/path/to/host/sessions.db
```

Do not mix matrices across hosts.
