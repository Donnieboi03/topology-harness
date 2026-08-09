# Compound topologies (recipes)

**Compounds** are the normal unit of work under **Compound Topologies** / **agent-topo-harness**. Atoms alone are incomplete defaults; Topic Owners wire atoms (and may invent novel compounds) under control-plane invariants.

Named recipes below are preferred starting points. Main may hint; TO owns final wiring.

## How Main sets composition

In the scope + tooling card ([scope-and-tooling-card.md](scope-and-tooling-card.md)), Main may include:

```text
composition: research-build
```

or a short freeform hint:

```text
composition: swarm the APIs then refine the client; skip debate
```

- Hint is **non-binding** — TO may rewire if evidence or tooling constraints demand it.
- TO may invent a **novel compound** (any atom sequence / parallel mix) as long as: flat TOs only, leaves don’t nest, TO owns brief before producers that need a single SoT, evidence gates + critical escalation still apply.
- Record the actual composition in telemetry (`composition` / `pattern_composition`).

---

## `debug-compound`

**Intent:** Isolate failure dimensions, then fix under evidence.

```text
plane-audit  →  TO brief  →  refine-loop
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `plane-audit` | Leaves | Orthogonal failure lenses (e.g. repro ∥ regression ∥ env) |
| TO brief | Topic Owner | Merge plane findings; checklist for Generator |
| `refine-loop` | Generator / Critiquer | Hard evidence exits; fail → another round |

**When:** Bugs, regressions, “works on my machine,” multi-cause failures. Prefer this over inventing a first-class `debug-loop` atom.

---

## `research-build`

**Intent:** Breadth-first research, then implement from one brief.

```text
research-swarm  →  TO brief  →  refine-loop
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `research-swarm` | Scouts | Disjoint sub-queries; no durable-memory dumps |
| TO brief | Topic Owner | Citations + decisions; sole SoT for Generator |
| `refine-loop` | Generator / Critiquer | Build against brief + evidence gates |

**When:** New feature / integration with unknown surface area.

---

## `decide-then-audit`

**Intent:** Settle trade-offs, then risk-lens the chosen path; optionally build.

```text
debate  →  plane-audit  →  optional refine-loop
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `debate` | Additor / Reductor / Consul | Expand vs cut; tie-break in goal |
| `plane-audit` | Planes | Independent lenses on the Consul decision (**≠** debate) |
| `refine-loop` | Optional | Only if implementation is in-scope for this topic |

**When:** Architecture / roadmap choices where both value debate and catastrophic-dimension audits matter. Keep `debate` and `plane-audit` distinct.

---

## `verify-then-build`

**Intent:** Ground claims before any producer work.

```text
verify-claims  →  TO brief  →  refine-loop
```

| Step | Owner | Notes |
| :--- | :--- | :--- |
| `verify-claims` | Draft / verifiers / reconciler | Blinded checks; costly hallucinations |
| TO brief | Topic Owner | Reconciled facts only |
| `refine-loop` | Generator / Critiquer | Build only from verified brief |

**When:** Factual, legal, financial, or citation-heavy deliverables that then need an artifact.

---

## Novel compounds

TO may invent other wirings (e.g. `verify-claims` on a research brief, swarm-only, refine-only) when the topic warrants it. **Novel ≠ ignore gates.** Invariants always hold: Main scope/tooling, no TO→TO, leaves don’t nest, critical Leaf→TO→Main→host channel, and TO-only durable writes when persist is enabled.
