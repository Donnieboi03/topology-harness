---
name: topology-harness
description: >-
  Compound Topologies (topology-harness): Planner (TO) default for actionable
  work; Solo only for easy direct Q&A; Chat / Planner / Worker; modes Solo |
  One helper | Planner+workers. Sticky lanes; intent routing; Worker stubs;
  assert_spawn_policy / topo_gate / coerce_route / assert_can_write.
  On Cursor this chat is Chat — Task sub-agents are Planner/Worker
  (docs/adapters/cursor.md). Route without waiting for “multi-agent.”
  CLI: topology-harness doctrine | cursor-map | --doctor | compounds.
---

# topology-harness

**Planner first for action.** Open (or resume) a TO for any multi-step action,
implement, edit, or research. **Solo only** for easy direct questions.

> **Aliases:** Chat = Main · Planner = TO / orchestrator / topic_owner · Worker = TT / leaf

**CLI:** `topology-harness doctrine` · `cursor-map` · `--doctor` · `compounds`  
**Cursor:** [docs/adapters/cursor.md](docs/adapters/cursor.md) · [install.md](install.md)

## Output style (ADHD)

Attribution: [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd).

**Chat (Main) always uses this when talking to the operator.** Solo answers and post-Planner turns. Workers never speak to the operator.

1. Verdict / next action first.
2. ≤5 bullets; number multi-step work.
3. End with one <2-min next step when work remains.
4. Errors: location, cause, fix. No closers.
5. After a Planner returns: publish the Planner **User card** (already ADHD). Do **not** dump Host brief, Task ledger, Progress, composition ids, or Worker JSON. Do **not** invent or invert Planner facts. If the Planner omitted a User card, Chat writes one from Decisions — still ADHD, still no host dump.

## Roles

```
Chat
  └── Planner(s)   ← default for actionable work; no Planner→Planner
        └── Workers  ← orthogonal stubs; no further spawn
```

| Role | Does | Must not |
| :--- | :--- | :--- |
| **Chat** | Solo Q&A (ADHD); open/resume Planner; publish User card | Dump host ledger; invent Planner facts; fan Workers when a topic is sticky-open |
| **Planner** | One topic; merge stubs; author User card + Host brief | Spawn another Planner; answer-key Worker goals; address the operator |
| **Worker** | One orthogonal lens; stub | Talk to the user; spawn |

## Sticky + stubs

- Sticky: `.cursor/topology-sticky/registry.json` — resume Planner; don’t cold re-fan
- Workers: `WORKER_STUB_INSTRUCTION` / `TT_STUB_INSTRUCTION`; orthogonal partition; seed-only goals

## Checklist (fail-closed)

- [ ] Durable writes → `assert_can_write` / `guarded_write` (Planner only)
- [ ] Every spawn → `assert_spawn_policy`
- [ ] Routes → `coerce_route_with_registry(..., open_topics=…)`
- [ ] After sticky load → `purge_idle()`; Chat card → `topics_for_main(limit=1)`
- [ ] Done → `retire_topic` then `release_topic`
- [ ] Atoms only: `swarm|plane|cove|shard`; cycles: `cycle` + `revise`

## Advanced

Atoms, named compounds, CLI deep refs: [docs/advanced.md](docs/advanced.md).
Not required for day-to-day Planner work without Worker fans.
