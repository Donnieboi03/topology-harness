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
- **One TO = one topic.** All atoms under that TO stay on-topic. Directional split (scouts/planes) = lenses of the same topic; unrelated work → another TO.

### Sticky leaves (reuse — general)

Until the TO **releases** a lane, prefer **reusing the same leaf session** for more work of that role on this topic — do **not** cold-respawn and re-pay schemas + rediscovery. This is **hygiene** (avoid thrash), not a promise that B is cheaper than monolith A — see [cost-analysis.md](cost-analysis.md).

| Lane | Sticky unit | Reuse when |
| :--- | :--- | :--- |
| Research scout | One scout per directional lens | More research on that lens / follow-ups |
| Refine | One Generator + one Critiquer | Another produce/audit round |
| Debate | Additor / Reductor / Consul | Another expand/cut pass |
| Plane-audit | One leaf per plane | Re-check that plane after a fix |
| Verify-claims | Draft / verifier / reconciler roles | Another claim pass |

- Spawn with `background=True` so the TO can continue and feed follow-ups into the **same** worker when the host supports resume/poll; otherwise brief one leaf to iterate until its lane success criteria.
- Release a lane when its success criteria are met or the TO ends the topic — then tear down.
- Parallel sticky lanes are fine (e.g. scout-A ∥ scout-B) if they stay on-topic and merge through the TO brief.

**Durable memory** is not a topology and is **optional**. When the host has a store and Main sets `persist: durable` (or a host alias like `vault`), **TO is the sole agent writer**. Main never writes; leaves are read-only. See [durable-memory.md](durable-memory.md). Obsidian specifics: Hermes adapter.

## Pattern library (atoms)

### `refine-loop` (alias: generator / critiquer)
- **Roles**: Generator produces from the **TO brief** only; Critiquer audits against a **checklist or tests**.
- **Trigger**: Code, high-precision artifacts, likely first-try failure.
- **Lifecycle**: Follow **Sticky leaves** above — one Gen + one Critiquer for the topic until TO releases. Do not cold-respawn Gen every critique round.
- **Mission**: One Gen/Critiquer pair per TO by default. Parallel Gens only for independent on-topic workstreams.
- **Hard exit gates** (fail → another Generator **round** on the sticky Gen): tests, typecheck, lint/syntax, docs for code; see [evidence-gates.md](evidence-gates.md). Opinions are not exits.
- **Exit**: Critiquer pass under evidence gates, max rounds, or tests green.

### `research-swarm` (alias: swarm / parallel scouts)
- **Roles**: Scouts R1…Rn with mutually exclusive sub-queries.
- **Trigger**: Multi-source research, siloed docs, breadth over one deep dive.
- **Lifecycle**: Sticky per scout lens — more research on the same lens reuses that scout; do not spawn a fresh scout for every follow-up question on the same axis.
- **Merge**: **Topic Owner writes one brief** (citations) before any code — [to-brief-template.md](to-brief-template.md).

### `debate` (alias: consul — additor / reductor)
- **Roles**: Additor expands; Reductor cuts scope/debt/cost; Consul synthesizes.
- **Trigger**: Roadmap or architecture **trade-offs** (expand vs cut).
- **Lifecycle**: Sticky Additor / Reductor / Consul for further passes on the same decision — do not cold-respawn for every tweak.
- **Exit**: Consul decision with tie-break rule in the goal.
- **Not** `plane-audit` — debate is adversarial scope/value; planes are independent risk lenses. Keep both.

### `plane-audit` (alias: orthogonal planes)
- **Roles**: Independent planes (e.g. security ∥ performance ∥ UX).
- **Trigger**: Failure in any single dimension is catastrophic.
- **Lifecycle**: Sticky per plane — re-audit after a fix reuses that plane leaf.
- **Merge**: Topic Owner (or referee) requires all planes clear with evidence.
- **Not** `debate` — do not collapse planes into additor/reductor.

### `verify-claims` (alias: cove)
- **Roles**: Draft → extract claims → blinded verifiers → reconciler.
- **Trigger**: Factual / legal / financial reporting where hallucinations are costly.
- **Lifecycle**: Sticky per role for another claim pass on the same draft/topic.
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