# Atom taxonomy (current)

> **Hot path:** [agent-topologies.md](agent-topologies.md) ·
> [compounds.md](compounds.md).
>
> **Public surface:** atoms `swarm|plane|cove|shard`; combinator `cycle`;
> transition `revise`; prefer named compounds. The public menu is the registry.
>
> Standing *why*: [atom-theory.md](atom-theory.md) (§§1–2 + summary; §§3–5 deep
> reference).

## Closed sets

| Kind | Values |
| :--- | :--- |
| Atoms (`ATOMIC_PARADIGMS`) | `swarm` \| `plane` \| `cove` \| `shard` |
| Combinator | `cycle` |
| Transition | `revise` |

`composition_field()` carries `combinator` / `transition` under
`schema_version = 2`. URN paradigm = atom only.

**Closed primitives, open composition.** Fail-closed atom / combinator /
transition sets; freeform DAG wiring over them. Prefer named compounds.

- **`accept` belongs to the `cycle`, not the atom.**
- An **atom** is `fan(partition, worker, merge)` individuated by **merge algebra**.
- Atom/combinator boundary: an atom partitions by content and keeps every
  output; anything that runs the same task N times and discards some is a
  combinator.

## Atoms

| Atom | Partition axis | Merge algebra |
| :--- | :--- | :--- |
| `swarm` | disjoint sub-questions | union / synthesis |
| `plane` | lenses over one artifact | conjunction (AND-gate) |
| `cove` | claims, blinded | three-valued per-claim adjudication |
| `shard` | pieces of one deliverable | assembly under an interface contract |

## Derived wiring (not primitives)

- **Debate** — roughly `cycle(swarm-over-stances, revise)` with a consul accept
  predicate.
- **`to-brief`** — merge operator of the preceding atom, not a step.
- **`cycle(plane, revise)`** — produce/audit under evidence gates.

Compounds: a DAG whose nodes are atoms or `cycle`-wrapped atoms.
