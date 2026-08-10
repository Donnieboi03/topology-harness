# Evidence gates

Critiquer / plane / verifier **exit criteria** are evidence, not opinions. Fail → another producer round (or Orchestrator revises the brief). Soft “looks good” is not a pass.

## Code / docs matrix (refine-loop default)

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
| `research-swarm` | Citations, primary sources, contradicted claims called out; no unsourced assertions in the Orchestrator brief |
| `debate` | Consul decision records both sides + explicit tie-break rule applied |
| `plane-audit` | Each plane returns checklist items with commands/logs/screenshots as applicable; all required planes clear |
| `verify-claims` | Each claim: verified / disputed / unknown with verifier notes; reconciler output only |
| Novel compounds | Map each producer stage to the closest row above |

## Critiquer prompt stub

```text
Audit against the brief evidence checklist only.
For each gate: PASS | FAIL | N/A with command output or artifact pointer.
No PASS without evidence. Opinions are FAIL.
```
