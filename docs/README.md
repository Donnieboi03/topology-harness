# Docs index

Compound Topologies — portable multi-agent control plane.

Start with the [README](../README.md) for purpose and utilization, then:

| Doc | Topic |
| :--- | :--- |
| [agent-topologies.md](agent-topologies.md) | Atomics + patterns + Main / TO / TT |
| [compounds.md](compounds.md) | Named compound recipes |
| [sticky-registry.md](sticky-registry.md) | Sticky TO / TT registry |
| [intent-routing.md](intent-routing.md) | Route actions for Main |
| [tt-stubs.md](tt-stubs.md) | Short TT findings → TO brief |
| [to-brief-template.md](to-brief-template.md) | TO brief |
| [scope-and-tooling-card.md](scope-and-tooling-card.md) | Main→TO envelope |
| [evidence-gates.md](evidence-gates.md) | Hard exit criteria |
| [critical-escalation.md](critical-escalation.md) | TT→TO→Main→host |
| [durable-memory.md](durable-memory.md) | Optional persist (TO writes) |
| [vault-write-policy.md](vault-write-policy.md) | Persist write gate (host maps backend) |
| [cost-analysis.md](cost-analysis.md) | Optional session-tree / A-B measurement helpers (not doctrine) |
| [graph_telemetry.md](graph_telemetry.md) | URN + sibling telemetry |
| [adapters/cursor.md](adapters/cursor.md) | Cursor as host (Main/TO/TT → chat + Task) |

Also: [../SKILL.md](../SKILL.md), [../install.md](../install.md).

Host-specific mappings live under `docs/adapters/` (optional) or in the host
repo. The core package stays host-agnostic.
