# Optional measurement helpers

Optional **synthetic** A/B helpers for hosts that want to **measure** cast
math offline. Not live session accounting.

**Live spend** is host-owned: Hermes session DB (`estimated_cost_usd`,
`parent_session_id` tree) plus sticky `topology_urn` join. Hosts may join
session cost to URNs with their own scripts. Do not expect this package to
open Hermes SQLite.

| Helper | Role |
| :--- | :--- |
| `cost_A` / `cost_B` | Synthetic one-turn models |
| `python -m topology_harness.cost_smoke` | Sanity check Main-only vs forced-TO on trivia |

Example cast rates align with [config/models.yaml](../config/models.yaml):
Main `google/gemini-3.1-flash-lite`, TO `google/gemini-3-flash-preview`, atoms
as in that file.

Do not mix pricing matrices across hosts.
