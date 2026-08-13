# Compound topologies (recipes)

**Compounds** are the normal unit of work under **Compound Topologies** /
**topology-harness**. Prefer the **five named recipes** below.

## Public closed menu

The **public menu is the registry**. Teach and wire only these:

| Kind | Public choices |
| :--- | :--- |
| **Atoms** | `swarm` \| `plane` \| `cove` \| `shard` only |
| **Combinator** | `cycle` only |
| **Transition** | `revise` only |
| **Compounds** | Prefer the five named recipes in this file |

Atoms alone are incomplete defaults; TOs wire atoms **and** combinator
applications — especially `cycle(plane, revise)` — under control-plane
invariants.

A compound is a **DAG whose nodes are atoms or combinator-wrapped atoms**. A
wiring entry is either a plain atom verb or a structured node. The shared
`REFINE` node in code is:

```python
{"atom": "plane", "combinator": "cycle", "transition": "revise"}
```

`to-brief` does not appear in wiring: it is the **merge operator** of the
atom that precedes it, absorbed into that atom's definition.

**Closed primitives, open composition.** Atoms, transitions, and combinators
stay fail-closed in code; the DAG wiring over them stays freeform.

Named recipes below are preferred starting points. Main may hint; TO owns final wiring.

## How Main sets composition

In the scope + tooling card ([scope-and-tooling-card.md](scope-and-tooling-card.md)), Main may include:

```text
composition: research-build
```

or a short freeform hint:

```text
composition: swarm the APIs then cycle(plane, revise) the client
```

- Hint is **non-binding** — TO may rewire if evidence or tooling constraints demand it.
- TO may invent a **novel compound** — any *wiring* of the closed primitives — as long as: flat TOs only, TTs don’t nest, TO owns brief before producers that need a single SoT, evidence gates + critical escalation still apply.
- **TO may not invent new atoms, transitions, or combinators.** Those sets are closed and fail-closed; novelty lives in the wiring, not the primitives.
- Record the actual composition in telemetry (`composition` / `pattern_composition`), including `combinator` / `transition` when a cycle is used (`schema_version=2`).

---

## `debug-compound`

**Intent:** Isolate failure dimensions, then fix under evidence.

```text
plane-audit  →  cycle(plane, revise)
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `plane-audit` | TTs | Orthogonal failure lenses (e.g. repro ∥ regression ∥ env); **sticky per plane**. Its merge — the TO brief — is the checklist for the next node |
| `cycle(plane, revise)` | Generator / Critiquer | Critiquer is the evaluator plane; Generator is the `revise` transition. Hard evidence exits; **sticky** until TO releases |

**When:** Bugs, regressions, “works on my machine,” multi-cause failures.

---

## `research-build`

**Intent:** Breadth-first research, then implement from one brief.

```text
research-swarm  →  cycle(plane, revise)
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `research-swarm` | Scouts | Disjoint sub-queries; **sticky per lens**; no durable-memory dumps. Its union merge is the brief — citations + decisions, sole SoT for the Generator |
| `cycle(plane, revise)` | Generator / Critiquer | Sticky Gen/Critiquer; evidence gates |

**When:** New feature / integration with unknown surface area.

---

## `decide-then-audit`

**Intent:** Settle trade-offs, then risk-lens the chosen path; optionally build.

```text
cycle(swarm, revise)  →  plane-audit  →  optional cycle(plane, revise)
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `cycle(swarm, revise)` | Additor / Reductor / Consul | Debate: a fan over stances, cycled on rebuttal, consul tie-break as the accept predicate. Sticky roles |
| `plane-audit` | Planes | Independent lenses (**≠** debate); sticky per plane |
| `cycle(plane, revise)` | Optional | Sticky Gen/Critiquer if implementation is in-scope |

**When:** Architecture / roadmap choices where both value debate and catastrophic-dimension audits matter. Keep debate and `plane-audit` distinct — debate is adversarial scope/value, planes are independent risk lenses.

---

## `verify-then-build`

**Intent:** Ground claims before any producer work.

```text
verify-claims  →  cycle(plane, revise)
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `verify-claims` | Draft / verifiers / reconciler | Blinded checks; costly hallucinations. Merge is a per-claim verdict table — REFUTED is a result, not a failure |
| `cycle(plane, revise)` | Generator / Critiquer | Build only from reconciled facts |

**When:** Factual, legal, financial, or citation-heavy deliverables that then need an artifact.

---

## `parallel-build`

**Intent:** Build interlocking pieces in parallel under one interface contract.

```text
TO settles contract  →  shard  →  assembly gates  →  optional cycle(plane, revise)
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| Contract | TO | Signatures, boundaries, shared vocabulary, schema. **Required before the fan** — unlike a swarm, a shard cannot start without it |
| `shard` | Builder TTs | One piece each; no overlapping writes |
| Assembly | TO | `interfaces_agree`, `no_overlapping_writes`, `assembles_clean`. The only merge that can fail with every worker succeeding |
| `cycle(plane, revise)` | Optional | When assembly fails or the pieces need polish |

**When:** The deliverable decomposes into pieces that must fit. Not coding-specific: chapters under a shared outline, service configs under a port map, and pipeline stages under a schema are all shards.

**Do not use** when the pieces are independent answers rather than parts of one artifact — that is a `research-swarm`.

---

## Novel compounds

TO may invent other wirings (e.g. `verify-claims` on a research brief, swarm-only,
`cycle(plane, revise)`-only) when the topic warrants it. **Novel ≠ new
primitives:** the atom, transition, and combinator sets are closed; novelty is
in the DAG over them. **Novel ≠ ignore gates.** Invariants always hold: Main
scope/tooling, no TO→TO, TTs don't nest, critical TT→TO→Main→host channel, and
TO-only durable writes when persist is enabled.
