# Agent Topologies (pattern library)

System name: **Compound Topologies**; harness: **topology-harness**.
TOs compose atoms and combinator applications into **compounds** — see
[compounds.md](compounds.md).

## Public closed menu

The **public menu is the registry**. Teach and wire only these:

| Kind | Public choices |
| :--- | :--- |
| **Atoms** | `swarm` \| `plane` \| `cove` \| `shard` only |
| **Combinator** | `cycle` only |
| **Transition** | `revise` only |
| **Compounds** | Prefer the five named recipes in [compounds.md](compounds.md) |

An **atom** is an instance of the generic fan `fan(partition, worker, merge)`,
individuated by its **merge algebra**. The rule that decides membership:

> An atom partitions by content and keeps every output. Anything that runs the
> same task N times and discards some is a **combinator**.

Why each atom is distinct — and why the star shape is near-optimal in the first
place — is in [atom-theory.md](atom-theory.md).

## Control plane (who spawns whom)

```
Main (talking agent)
  └── TO(s)     ← flat only; mid-tier (host role often orchestrator)
        ├── research-swarm        (atom → swarm)
        ├── plane-audit           (atom → plane)
        ├── verify-claims         (atom → cove)
        ├── parallel-build        (atom → shard)
        ├── cycle(plane, revise)  (combinator application)
        └── …TTs only (no further topology spawn)
```

- **Main** owns the flat set of TOs; may pass a `composition:` hint.
- **TO** may nest-delegate **TTs** only (`role=orchestrator`, depth 1).
  May compose any mix / invent novel compounds under invariants.
- **TTs** never spawn (host must enforce nest depth; harness cannot alone).
- **One TO = one topic.** All work under it stays on-topic.
  Directional split (scouts/planes) = lenses of the same topic; unrelated work
  → another TO.

### Sticky TTs (reuse — session-scoped)

Workers stay alive until the host session ends (or Main/TO releases a
topic). Tear-down-after-done forces cold respawn.

Until release:
- Prefer **reusing the same TT session** for that role/lane.
- Same for TOs: **one handle per topic**; follow-ups resume it.
- **Registry:** [`StickyRegistry`](sticky-registry.md).
- **Follow-ups:** [intent routing](intent-routing.md) — default `to_only`
  (`coerce_route_with_registry` fails-soft coerces re-`open_topic`).
- **TT outputs:** [tt stubs](tt-stubs.md) — short findings; TO writes
  the brief / user answer.
- **Topic must be open:** `topo_gate(registry)` / `assert_topic_open`.

This is **hygiene** (avoid thrash) — sticky resume and scoped tools, not a
latency or spend guarantee. See [sticky-registry.md](sticky-registry.md).

| Lane | Sticky unit | Reuse when |
| :--- | :--- | :--- |
| Research scout | One scout per directional lens | More research on that lens |
| `cycle(plane, revise)` | One Generator + one Critiquer | Another produce/audit round |
| Debate wiring | Additor / Reductor / Consul | Another expand/cut pass |
| Plane-audit | One TT per plane | Re-check that plane after a fix |
| Verify-claims | Draft / verifier / reconciler | Another claim pass |
| Shard build | One builder per piece | Re-build that piece after an assembly failure |

**Durable memory** is optional. When Main sets `persist: durable`, **TO
is the sole agent writer**. Main never writes; TTs are read-only. See
[durable-memory.md](durable-memory.md).

## Atoms (URN paradigms)

The merge is **not** TO discretion — the atom determines it, and the TO must
declare the atom *before* it fans. That is what makes "did the TO merge
correctly?" a checkable question.

| Atom | Partition axis | Merge algebra | Merge can fail? |
| :--- | :--- | :--- | :--- |
| `swarm` | disjoint sub-questions | union / synthesis | no (total) |
| `plane` | lenses over one artifact | conjunction (AND-gate) | no — lanes fail, merge does not |
| `cove` | claims, blinded | per-claim three-valued adjudication | no (yields UNKNOWNs) |
| `shard` | pieces of one deliverable | assembly under an interface contract | **yes (partial)** |

### `research-swarm` → `swarm`
- **Roles**: Scouts with mutually exclusive sub-queries.
- **Lifecycle**: Sticky per scout lens.
- **Merge**: union — TO writes one brief; a silent scout thins it, never fails it.

### `plane-audit` → `plane`
- **Roles**: Independent planes (e.g. security ∥ performance ∥ UX).
- **Lifecycle**: Sticky per plane TT.
- **Merge**: conjunction — all planes clear with evidence, or the audit fails.

### `verify-claims` → `cove`
- **Roles**: Draft → extract claims → blinded verifiers → reconciler.
- **Merge**: per-claim verdict table. A REFUTED claim is a *successful* outcome,
  not a failure — this is why cove is not a plane.

### `parallel-build` → `shard`
- **Roles**: One builder TT per piece, all working under one interface contract.
- **Precondition**: the TO settles the contract (signatures, boundaries, shared
  vocabulary, schema) **before** the fan. Unlike swarm, shard cannot start
  without it.
- **Merge**: assembly. The only atom whose merge is a *partial* function — N
  workers can each succeed and integration still fail.
- **Not coding-specific.** Chapters under a shared outline, service configs
  under a port map, and pipeline stages under a schema are all shards.
- **Smell test**: two workers producing the same thing is *redundancy* → swarm;
  a *collision* → shard.

## Combinators (wrap an atom)

Not atoms. A combinator takes an atom and returns something runnable.
**Public menu: `cycle` only.** `cycle` is the only combinator that carries
state between rounds.

```
cycle(atom, transition, accept, bound)
```

**Public transition: `revise` only** — mutates the subject artifact.
Example: `cycle(plane, revise)` — audit, fix, re-audit.

The atom is fixed for the lifetime of a cycle — changing it would make "the
gates passed" mean something different each round. `accept` and `bound` belong
to the cycle.

### `cycle(plane, revise)`

The **Critiquer** is the evaluator atom (usually a one-lane plane); the
**Generator** *is* the transition function,
`artifact_{n+1} = T(artifact_n, critique_n)`. Neither is a topology.

- **Lifecycle**: Sticky Gen + Critiquer until TO releases.
- **Hard exit gates**: see [evidence-gates.md](evidence-gates.md).
- **Telemetry**: `atom=plane` in the URN, plus `combinator=cycle` /
  `transition=revise` as siblings.

### Debate is a composite

A fan over stances wrapped in a cycle whose transition is rebuttal, with a
consul tie-break as the accept predicate. Derived wiring — not a primitive —
and **not** `plane-audit`: debate is adversarial scope/value; planes are
independent risk lenses.

### `to-brief` is not a step

It is the **merge operator** of whichever atom precedes it. Absorbed into the
atom definition; do not list it in wiring.

## Enforcement honesty

| Policy | Harness | Host must |
| :--- | :--- | :--- |
| TO-only durable writes | `assert_can_write` (fail-closed) | Wrap every write / Main store hook |
| Main→leaf for topic/substantive work | `assert_spawn_policy` | Call before every spawn |
| Topic open before TT work | `topo_gate` / `assert_topic_open` | Decorate spawn helpers |
| Atom / transition / combinator sets closed | `assert_atomic_paradigm`, `assert_transition`, `assert_combinator` | Pass validated values |
| Intent routing policy | Schema + `coerce_route_with_registry` | Parse + coerce before spawn |
| Sticky “must be open” | Registry + gates above | Persist sticky JSON |
| Evidence / TT stubs “enforced” | Soft helpers + prompts | Honor gates before “done” |
| Nest depth / TT cannot spawn | — | Runtime nest limits |
| Model allowlist | `assert_allowed` | Load host config |

## Durable memory (optional flag, not a topology)

- **`persist: none`** (harness default) or **`persist: durable`** (host may
  alias `vault`).
- Prefer `persist: durable` / `vault` on Topic Orchestrator open when durable
  memory should compound; leave `none` for throwaway leaves / ephemeral asks.
- **Writer**: TO only. TTs: read-only if allowlisted. Main does not write.
- Details: [durable-memory.md](durable-memory.md).

## Graph telemetry

See [graph_telemetry.md](graph_telemetry.md). URN atom + sibling
`combinator` / `transition`; `schema_version=2`.
