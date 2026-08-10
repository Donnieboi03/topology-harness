---
name: agent-topo-harness
description: >-
  Compound Topologies control plane: Main gates Topic Orchestrators (TOs);
  one topic per TO; TTs (Topic Topology workers) under compounds; sticky
  lanes; evidence gates; intent routing; TT stubs. Use when designing or
  enforcing multi-agent topology policy on any host that can spawn nested
  workers.
---

# Compound Topologies (agent-topo-harness)

Portable **orchestration policy** for multi-agent systems.

A host runtime provides chat, spawn/resume, tools, and sessions. This harness
adds: Main vs Topic Orchestrator (TO) vs TT, one-topic isolation, compounds,
sticky lanes, evidence gates. Without it, a host can still spawn workers —
just without those rules (fat children, mixed topics, tool thrash).

**Control-plane pieces:** [sticky registry](docs/sticky-registry.md),
[intent routing](docs/intent-routing.md) (follow-ups default `to_only`),
[TT stubs](docs/tt-stubs.md) → TO brief. Hosts bind `session_id` and
spawn/resume.

Classify-only intent helper role: ``roles.router`` in [config/models.yaml](config/models.yaml)
(override with host env). Prefer **in-band** route emission on Main for live
turns; separate classify calls are for measurement only.

## Roles

```
Main
  └── TO(s)     ← flat only (no TO→TO)
        └── TT workers    ← compounds / atoms; no further topology spawn
```

| Role | Does | Must not |
| :--- | :--- | :--- |
| **Main** | Flat TO(s); or one trivial TT | Nested TOs; heavy work in-chat; TO for pure chit-chat |
| **TO** (Topic Orchestrator) | Compose compounds; merge TT stubs; user-facing voice for the topic | Spawn another TO; mix unrelated topics |
| **TT** (Topic Topology) | One lens / atom job; return stubs | Spawn; talk to the user as the product voice |

**Trivial:** Main in-chat for tiny Q&A; larger single job → one TT. Never a TO for pure chit-chat.

See [README.md](README.md) glossary: **TO** = Topic Orchestrator (same as host `role=orchestrator`); **TT** ≠ the product name Compound Topologies.

## Compounds

Named recipes under a TO — see [docs/compounds.md](docs/compounds.md).
Main may hint `composition:`; TO owns final wiring.

## Cost

Do **not** promise the graph is always cheaper than monolith chat. Measure on
your host. Value is isolation, scoped tools, sticky resume, evidence gates.

## Host glue

Host-owned: nest depth/role, hooks, prefill, durable-store mappings. See
[install.md](install.md). This repo stays host-agnostic.

## Doc index

| Doc | Topic |
| :--- | :--- |
| [docs/agent-topologies.md](docs/agent-topologies.md) | Atoms + control plane |
| [docs/compounds.md](docs/compounds.md) | Named compounds |
| [docs/sticky-registry.md](docs/sticky-registry.md) | Sticky TO/TT registry |
| [docs/intent-routing.md](docs/intent-routing.md) | Route actions |
| [docs/tt-stubs.md](docs/tt-stubs.md) | TT stub → TO brief |
| [docs/cost-analysis.md](docs/cost-analysis.md) | Cost protocol |
| [docs/scope-and-tooling-card.md](docs/scope-and-tooling-card.md) | Main→TO envelope |
| [docs/evidence-gates.md](docs/evidence-gates.md) | Hard exits |
| [docs/critical-escalation.md](docs/critical-escalation.md) | TT→TO→Main→host |
| [docs/durable-memory.md](docs/durable-memory.md) | Optional persist |

## Checklist

- [ ] Main routes only (or trivial TT); no TO→TO
- [ ] One TO = one topic
- [ ] TTs return stubs; TO merges
- [ ] Follow-ups prefer `to_only` over full re-fan
- [ ] Sticky resume when host supports session ids
- [ ] Evidence gates on refine / verify compounds
- [ ] Host glue applied; runtime restarted if required
