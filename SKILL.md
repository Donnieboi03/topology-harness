---
name: topology-harness
description: >-
  Compound Topologies control plane: Main gates Topic Orchestrators (TOs);
  one topic per TO; TTs (Topic Topology workers) under compounds; sticky
  lanes; evidence gates; intent routing; TT stubs. Use when designing or
  enforcing multi-agent topology policy on any host that can spawn nested
  workers.
---

# Compound Topologies (topology-harness)

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
| [docs/scope-and-tooling-card.md](docs/scope-and-tooling-card.md) | Main→TO envelope |
| [docs/evidence-gates.md](docs/evidence-gates.md) | Hard exits |
| [docs/critical-escalation.md](docs/critical-escalation.md) | TT→TO→Main→host |
| [docs/durable-memory.md](docs/durable-memory.md) | Optional persist |
| [docs/graph_telemetry.md](docs/graph_telemetry.md) | URN + siblings |

## Checklist

### Fail-closed in harness (call these)

- [ ] Durable writes go through `assert_can_write` / `guarded_write` (TO only)
- [ ] Every spawn calls `assert_spawn_policy` (blocks Main→leaf for topic/substantive/atomic work)
- [ ] Spawn helpers use `topo_gate(registry)` / `assert_topic_open`
- [ ] After parsing routes, call `coerce_route_with_registry(..., open_topics=reg.open_topics())`
- [ ] Atomic URN paradigms only: `swarm` | `plane` | `cove` (`NotAtomicError` otherwise)

### Host must enforce (harness cannot alone)

- [ ] Nest depth / no TT spawn / no TO→TO (runtime nest patch)
- [ ] Main blocked from durable-store writes (host hook)
- [ ] Evidence PASS before treating refine-loop as done (honor `evidence` helpers)
- [ ] TT stubs honored as product voice rules (prompts + review)

### Soft / prompt-only (do not pretend these are hard gates)

- `TT_STUB_INSTRUCTION`, `ROUTER_SYSTEM_PROMPT` — instruction strings
- Evidence checklists — advisory unless the host blocks on `missing_gates`

### Ops

- [ ] URN Format: `topology:<paradigm>:{topic}--{lane|to}:<ulid>` (no goal prose)
- [ ] Persist: prefer `persist: durable` / `vault` on TO open when memory should compound
- [ ] Sticky resume when host supports session ids
- [ ] Host glue applied; runtime restarted if required

