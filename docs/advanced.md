# Advanced (atoms + compounds)

Skip this for Solo day-to-day. Open only when a Planner fans Workers.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

## Public menu (closed)

| Kind | Choices |
| :--- | :--- |
| **Atoms** | `swarm` \| `plane` \| `cove` \| `shard` |
| **Combinator** | `cycle` |
| **Transition** | `revise` |

Prefer named recipes: [compounds.md](compounds.md).

| Atom | Plain meaning |
| :--- | :--- |
| `swarm` | Parallel scouts; union merge |
| `plane` | Orthogonal risk lenses; conjunction |
| `cove` | Claim verify; per-claim verdicts |
| `shard` | Interlocking pieces under one contract |

**Orthogonal partition (mandatory for swarm/plane):** each Worker gets a disjoint
domain or distinct outlook — not clones of the Planner thesis.

Produce/audit under evidence = `cycle(plane, revise)` — not a separate atom.

## CLI

```bash
topology-harness compounds
topology-harness doctrine
topology-harness <<'PY'
print(ATOMIC_PARADIGMS)
print(get_compound("debug-compound"))
PY
```

Helpers: `resolve_paradigm`, `assert_combinator`, `assert_transition`,
`sibling_telemetry_fields` (`schema_version=2`: URN = atom; `combinator` /
`transition` as siblings).
