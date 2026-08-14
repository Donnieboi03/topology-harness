---
name: topology-harness
description: >-
  Compound Topologies control plane (topology-harness): Main gates Topic
  Orchestrators (TOs); one topic per TO; TTs under compounds; sticky lanes;
  evidence gates; intent routing; TT stubs; assert_spawn_policy / topo_gate /
  coerce_route / assert_can_write. On Cursor, this chat is the host — use Task
  sub-agents as TO/TT (see docs/adapters/cursor.md); route autonomously without
  waiting for the user to say multi-agent. Use when designing or enforcing
  multi-agent topology, spawning nested workers, or when the user mentions TO,
  TT, Compound Topologies, agent topologies, or sticky resume. CLI:
  topology-harness doctrine | cursor-map | --doctor | compounds.
---

# Compound Topologies (topology-harness)

Portable **orchestration policy** for multi-agent systems.

**CLI (on PATH after install):** `topology-harness doctrine` · `cursor-map` ·
`--doctor` · `compounds` · `cost-smoke` · or heredoc Python with helpers
pre-imported.
**Cursor host:** always-apply rule treats **this chat as Main** and Cursor
`Task` sub-agents as TO/TT — see [docs/adapters/cursor.md](docs/adapters/cursor.md)
and [install.md](install.md). Do not wait for the user to say “multi-agent.”

A host runtime provides chat, spawn/resume, tools, and sessions. This harness
adds: Main vs Topic Orchestrator (TO) vs TT, one-topic isolation, compounds,
sticky lanes, evidence gates. Without it, a host can still spawn workers —
just without those rules (fat children, mixed topics, tool thrash).

**Control-plane pieces:** [sticky registry](docs/sticky-registry.md),
[intent routing](docs/intent-routing.md) (follow-ups default `to_only`; Main
emits `RouteDecision` in-band),
[TT stubs](docs/tt-stubs.md) → TO brief. Hosts bind `session_id` and
spawn/resume.

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

## Atoms and combinators

**Public menu** (the registry — teach / wire with these only):

| Kind | Closed set |
| :--- | :--- |
| **Atoms** | `swarm` \| `plane` \| `cove` \| `shard` |
| **Combinator** | `cycle` |
| **Transition** | `revise` |

Prefer **named compounds** (five recipes) — see [docs/compounds.md](docs/compounds.md).
Do not invent primitives outside the public menu.

## Compounds

Prefer the five named recipes under a TO — see [docs/compounds.md](docs/compounds.md).
Main may hint `composition:`; TO owns final wiring.

## Models (example)

[config/models.yaml](config/models.yaml): Main `google/gemini-3.1-flash-lite`;
TO `google/gemini-3-flash-preview`; atom defaults per that file.

## Host glue

Host-owned: nest depth/role, hooks, prefill, durable-store mappings. See
[install.md](install.md). This repo stays host-agnostic.

## Doc index

| Doc | Topic |
| :--- | :--- |
| [docs/agent-topologies.md](docs/agent-topologies.md) | Atoms + combinators + control plane |
| [docs/compounds.md](docs/compounds.md) | Named compounds |
| [docs/host-contracts.md](docs/host-contracts.md) | Host sticky + retire contracts |

Operational cards + optional deep theory: [docs/README.md](docs/README.md).

## Checklist

### Fail-closed in harness (call these)

- [ ] Durable writes go through `assert_can_write` / `guarded_write` (TO only)
- [ ] Every spawn calls `assert_spawn_policy` (blocks Main→leaf for topic/substantive/atomic work)
- [ ] Spawn helpers use `topo_gate(registry)` / `assert_topic_open`
- [ ] After parsing routes, call `coerce_route_with_registry(..., open_topics=reg.open_topics())`
- [ ] After sticky load: `purge_idle()`; Main card uses `topics_for_main(limit=1)`
- [ ] Explicit done: `retire_topic` then `release_topic` (idle TTL = release only)
- [ ] Atom URN paradigms only: `swarm` | `plane` | `cove` | `shard` (`NotAtomicError` otherwise)
- [ ] Cycles use `combinator=cycle` + `transition=revise`
- [ ] Prefer named compounds over ad-hoc wiring when a recipe fits

### Host must enforce (harness cannot alone)

- [ ] Nest depth / no TT spawn / no TO→TO (runtime nest patch)
- [ ] Main blocked from durable-store writes (host hook)
- [ ] Evidence PASS before treating `cycle(plane, revise)` as done (honor `evidence` helpers)
- [ ] TT stubs honored as product voice rules (prompts + review)

### Soft / prompt-only (do not pretend these are hard gates)

- `TT_STUB_INSTRUCTION`, `ROUTER_SYSTEM_PROMPT` — instruction strings (Main emits routes in-band)
- Evidence checklists — advisory unless the host blocks on `missing_gates`

### Ops

- [ ] URN Format: `topology:<paradigm>:{topic}--{lane|to}:<ulid>` (no goal prose)
- [ ] Persist: prefer `persist: durable` / `vault` on TO open when memory should compound
- [ ] Sticky resume when host supports session ids
- [ ] Host glue applied; runtime restarted if required
