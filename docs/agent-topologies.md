# Agent Topologies (atom library)

User-facing names are short verbs (**atoms**). Academic aliases (`got`, `cove`, `moa`, …) are **telemetry / `paradigm` tags only**. Topic Owners compose atoms into **compounds** — see [compounds.md](compounds.md). System name: **Compound Topologies**; harness: **agent-topo-harness**.

## Control plane (who spawns whom)

```
Main (talking agent)
  └── Topic Owner(s)     ← flat only (no TO→TO); mid-tier orchestrator
        ├── research-swarm
        ├── refine-loop
        ├── debate
        ├── plane-audit
        ├── verify-claims
        └── …leaves only (no further topology spawn)
```

- **Main** owns the flat set of Topic Owners; may pass a `composition:` hint.
- **Topic Owner** may nest-delegate pattern **leaves** only (`role=orchestrator`, depth 1). May compose **any** atom mix / invent novel compounds under invariants.
- **Leaves** never spawn.

**Durable memory** is not a topology and is **optional**. When the host has a store and Main sets `persist: durable` (or a host alias like `vault`), **TO is the sole agent writer**. Main never writes; leaves are read-only. See [durable-memory.md](durable-memory.md). Obsidian specifics: Hermes adapter.

## Pattern library (atoms)

### `research-swarm` (alias: swarm / parallel scouts)
- **Roles**: Scouts R1…Rn with mutually exclusive sub-queries.
- **Trigger**: Multi-source research, siloed docs, breadth over one deep dive.
- **Merge**: **Topic Owner writes one brief** (citations) before any code — [to-brief-template.md](to-brief-template.md).

### `refine-loop` (alias: generator / critiquer)
- **Roles**: Generator produces from the **TO brief** only; Critiquer audits against a **checklist or tests**.
- **Trigger**: Code, high-precision artifacts, likely first-try failure.
- **Hard exit gates** (fail → another Generator round): tests, typecheck, lint/syntax, docs for code; see [evidence-gates.md](evidence-gates.md). Opinions are not exits.
- **Exit**: Critiquer pass under evidence gates, max rounds, or tests green.

### `debate` (alias: consul — additor / reductor)
- **Roles**: Additor expands; Reductor cuts scope/debt/cost; Consul synthesizes.
- **Trigger**: Roadmap or architecture **trade-offs** (expand vs cut).
- **Exit**: Consul decision with tie-break rule in the goal.
- **Not** `plane-audit` — debate is adversarial scope/value; planes are independent risk lenses. Keep both.

### `plane-audit` (alias: orthogonal planes)
- **Roles**: Independent planes (e.g. security ∥ performance ∥ UX).
- **Trigger**: Failure in any single dimension is catastrophic.
- **Merge**: Topic Owner (or referee) requires all planes clear with evidence.
- **Not** `debate` — do not collapse planes into additor/reductor.

### `verify-claims` (alias: cove)
- **Roles**: Draft → extract claims → blinded verifiers → reconciler.
- **Trigger**: Factual / legal / financial reporting where hallucinations are costly.
- **Merge**: TO owns reconciled brief before any build step.

### Internal-only paradigms (telemetry tags)

Use in `paradigm` / topology URN — do not expose as Main’s primary vocabulary:

| Tag | Maps to |
| :--- | :--- |
| `swarm` | `research-swarm` |
| `refine` | `refine-loop` |
| `debate` / `consul` | `debate` |
| `planes` | `plane-audit` |
| `cove` | `verify-claims` |
| `got` | Non-linear search with backtracking (rare; Topic Owner only) |
| `moa` | Layered proposers → aggregator (rare; Topic Owner only) |
| `adversarial` | Proposer vs red-team + referee (high-security) |

## Durable memory (optional flag, not a topology)

- **`persist: none`** (default) or **`persist: durable`** (host may alias `vault`).
- Coordinate via the host store when enabled — retrieve + approved upserts, not chat history alone.
- **Writer**: Topic Owner only. Scouts do not dump raw notes. Main does not write. Leaves: read-only if allowlisted.
- **Brain surgery**: human corrects the store offline; agents do not “fix” durable data from Main.
- Details: [durable-memory.md](durable-memory.md).