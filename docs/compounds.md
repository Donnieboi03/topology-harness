# Compounds (recipes)

Prefer these **five recipes** under a Planner. Skip for Solo.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

## Public menu

| Kind | Choices |
| :--- | :--- |
| Atoms | `swarm` \| `plane` \| `cove` \| `shard` |
| Combinator | `cycle` |
| Transition | `revise` |

**Orthogonal partition** on every swarm/plane fan: disjoint domains or outlooks.

Chat may hint `composition:`; Planner owns final wiring. No new atoms/combinators.

Shared refine node:

```python
{"atom": "plane", "combinator": "cycle", "transition": "revise"}
```

---

## `debug-compound`

`plane-audit → cycle(plane, revise)`

| Step | Who | Notes |
| :--- | :--- | :--- |
| `plane-audit` | Workers | Orthogonal failure lenses; sticky per plane |
| `cycle(plane, revise)` | Gen / Critiquer | Evidence exits |

**When:** Bugs, regressions, multi-cause failures.

---

## `research-build`

`research-swarm → cycle(plane, revise)`

| Step | Who | Notes |
| :--- | :--- | :--- |
| `research-swarm` | Scouts | Disjoint sub-queries |
| `cycle(plane, revise)` | Gen / Critiquer | Build from one brief |

**When:** New feature / unknown surface.

---

## `decide-then-audit`

`cycle(swarm, revise) → plane-audit → optional cycle(plane, revise)`

| Step | Who | Notes |
| :--- | :--- | :--- |
| Debate swarm | Stance Workers | Opposing outlooks; seed-only |
| `plane-audit` | Risk Workers | ≠ debate clones |
| Optional refine | Gen / Critiquer | If implement in-scope |

**When:** Architecture / roadmap trade-offs.

---

## `verify-then-build`

`verify-claims → cycle(plane, revise)`

| Step | Who | Notes |
| :--- | :--- | :--- |
| `verify-claims` | Draft / verifiers | Blinded; REFUTED is success |
| Refine | Gen / Critiquer | Build from reconciled facts |

**When:** Citation-heavy / factual deliverables.

---

## `parallel-build`

`contract → shard → assembly → optional cycle(plane, revise)`

| Step | Who | Notes |
| :--- | :--- | :--- |
| Contract | Planner | **Required before fan** |
| `shard` | Builder Workers | One piece each |
| Assembly | Planner | Can fail even if every Worker succeeded |

**When:** Pieces must fit. Independent answers → `research-swarm` instead.

---

## Novel wiring

Planner may rewire closed primitives. Invariants still hold: no Planner→Planner,
Workers don’t nest, Planner-only durable writes, escalate criticals via
[host-contracts.md](host-contracts.md).

Index: [advanced.md](advanced.md) · CLI: `topology-harness compounds`
