# Docs index

Compound Topologies — portable multi-agent control plane.

Start with the [README](../README.md) for purpose and utilization.

## Hot path

| Doc | Topic |
| :--- | :--- |
| [agent-topologies.md](agent-topologies.md) | Atoms + combinators + Main / TO / TT |
| [compounds.md](compounds.md) | Named compound recipes (prefer these) |

**Public surface:** atoms `swarm|plane|cove|shard`; combinator `cycle`;
transition `revise`. The public menu is the registry.

## Operational

| Doc | Topic |
| :--- | :--- |
| [sticky-registry.md](sticky-registry.md) | Sticky TO / TT registry |
| [intent-routing.md](intent-routing.md) | Route actions for Main |
| [tt-stubs.md](tt-stubs.md) | Short TT findings → TO brief |
| [to-brief-template.md](to-brief-template.md) | TO brief |
| [scope-and-tooling-card.md](scope-and-tooling-card.md) | Main→TO envelope |
| [evidence-gates.md](evidence-gates.md) | Hard exit criteria |
| [critical-escalation.md](critical-escalation.md) | TT→TO→Main→host |
| [durable-memory.md](durable-memory.md) | Optional persist (TO writes) + blackboard retire-flush |
| [host-contracts.md](host-contracts.md) | Cursor ↔ Hermes sticky + retire contracts |
| [vault-write-policy.md](vault-write-policy.md) | Persist write gate (host maps backend) |
| [graph_telemetry.md](graph_telemetry.md) | URN + sibling telemetry (`schema_version=2`) |
| [adapters/cursor.md](adapters/cursor.md) | Cursor as host (Main/TO/TT → chat + Task) |

## Theory / notes

| Doc | Topic |
| :--- | :--- |
| [atom-theory.md](atom-theory.md) | Why these primitives (§§1–2 + summary; §§3–5 deep ref) |
| [handoff-atom-taxonomy.md](handoff-atom-taxonomy.md) | Compact taxonomy card |
| [cost-analysis.md](cost-analysis.md) | Optional A-B measurement helpers |

Also: [../SKILL.md](../SKILL.md), [../install.md](../install.md),
[../HANDOFF.md](../HANDOFF.md) (spawn-policy handoff).

Host-specific mappings live under `docs/adapters/` (optional) or in the host
repo. The core package stays host-agnostic.
