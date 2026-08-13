# Evidence gates

Critiquer / plane / verifier **exit criteria** are evidence, not opinions. Fail → another producer round (or TO revises the brief). Soft “looks good” is not a pass.

## Code / docs matrix (`cycle(plane, revise)` default)

| Gate | Pass signal | Fail → |
| :--- | :--- | :--- |
| **Tests** | Targeted tests run green (or new tests cover the change) | Generator round |
| **Typecheck** | Project typecheck clean for touched paths | Generator round |
| **Lint / syntax** | Lint or parse clean on touched files | Generator round |
| **Docs** | User-facing / API docs updated when behavior changed | Generator round |

Skip a row only if Main’s scope card explicitly marks it N/A (e.g. pure prose topic).

## Per-atom analogs

| Atom | Evidence stand-ins |
| :--- | :--- |
| `research-swarm` | Citations, primary sources, contradicted claims called out; no unsourced assertions in the TO brief |
| `plane-audit` | Each plane returns checklist items with commands/logs/screenshots as applicable; all required planes clear |
| `verify-claims` | Each claim: verified / disputed / unknown with verifier notes; reconciler output only |
| `parallel-build` (`shard`) | `interfaces_agree` · `no_overlapping_writes` · `assembles_clean` — see below |
| `debate` (composite) | Consul decision records both sides + explicit tie-break rule applied |
| Novel compounds | Map each producer stage to the closest row above |

### Why `shard` gets its own gates

`shard` is the only atom whose merge is a **partial function**: every worker can
succeed at its own piece and assembly still fail. The other atoms cannot fail at
the merge — a plane fails in a *lane*, a cove records a REFUTED *verdict*. So
shard needs gates on the merge itself, not just per worker.

| Gate | Pass signal |
| :--- | :--- |
| `interfaces_agree` | Every piece matches the contract the TO fixed before the fan — signatures, schema, shared vocabulary |
| `no_overlapping_writes` | No two shards wrote the same region / file / section |
| `assembles_clean` | The whole thing composes: it links and imports, or cross-references resolve and terminology is consistent |

Gate names are **domain-neutral by design.** `assembles_clean` means
"cross-references resolve, terminology consistent" for a document exactly as
much as "it links" for a module — `shard` is not coding-specific.

## Critiquer prompt stub

```text
Audit against the brief evidence checklist only.
For each gate: PASS | FAIL | N/A with command output or artifact pointer.
No PASS without evidence. Opinions are FAIL.
```
