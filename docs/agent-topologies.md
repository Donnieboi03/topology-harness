# Agent Topologies (atom library)

User-facing names are short verbs (**atoms**). Academic aliases (`got`, `cove`,
`moa`, …) are **telemetry / `paradigm` tags only**. TOs compose atoms
into **compounds** — see [compounds.md](compounds.md). System name: **Compound
Topologies**; harness: **agent-topo-harness**.

## Control plane (who spawns whom)

```
Main (talking agent)
  └── TO(s)     ← flat only; mid-tier (host role often orchestrator)
        ├── research-swarm
        ├── refine-loop
        ├── debate
        ├── plane-audit
        ├── verify-claims
        └── …TTs only (no further topology spawn)
```

- **Main** owns the flat set of TOs; may pass a `composition:` hint.
- **TO** may nest-delegate **TTs** only (`role=orchestrator`, depth 1).
  May compose any atom mix / invent novel compounds under invariants.
- **TTs** never spawn.
- **One TO = one topic.** All atoms under it stay on-topic.
  Directional split (scouts/planes) = lenses of the same topic; unrelated work
  → another TO.

### Sticky TTs (reuse — session-scoped)

Workers stay alive until the host session ends (or Main/TO releases a
topic). Tear-down-after-done forces cold respawn.

Until release:
- Prefer **reusing the same TT session** for that role/lane.
- Same for TOs: **one handle per topic**; follow-ups resume it.
- **Registry:** [`StickyRegistry`](sticky-registry.md).
- **Follow-ups:** [intent routing](intent-routing.md) — default `to_only`.
- **TT outputs:** [tt stubs](tt-stubs.md) — short findings; TO writes
  the brief / user answer.

This is **hygiene** (avoid thrash) — not a promise the graph is cheaper than a
monolith. See [cost-analysis.md](cost-analysis.md).

| Lane | Sticky unit | Reuse when |
| :--- | :--- | :--- |
| Research scout | One scout per directional lens | More research on that lens |
| Refine | One Generator + one Critiquer | Another produce/audit round |
| Debate | Additor / Reductor / Consul | Another expand/cut pass |
| Plane-audit | One TT per plane | Re-check that plane after a fix |
| Verify-claims | Draft / verifier / reconciler | Another claim pass |

- Spawn background when the host supports resume/poll so the TO can
  feed follow-ups into the **same** worker.
- Parallel sticky lanes are fine if they stay on-topic and merge through the
  TO brief.

**Durable memory** is optional. When Main sets `persist: durable`, **TO
is the sole agent writer**. Main never writes; TTs are read-only. See
[durable-memory.md](durable-memory.md).

## Pattern library (atoms)

### `refine-loop`
- **Roles**: Generator produces from the **TO brief** only; Critiquer
  audits against a checklist or tests.
- **Lifecycle**: Sticky Gen + Critiquer until TO releases.
- **Hard exit gates**: see [evidence-gates.md](evidence-gates.md).

### `research-swarm`
- **Roles**: Scouts with mutually exclusive sub-queries.
- **Lifecycle**: Sticky per scout lens.
- **Merge**: TO writes one brief — [to-brief-template.md](to-brief-template.md).

### `debate`
- **Roles**: Additor / Reductor / Consul.
- **Not** `plane-audit` — debate is adversarial scope/value; planes are
  independent risk lenses.

### `plane-audit`
- **Roles**: Independent planes (e.g. security ∥ performance ∥ UX).
- **Lifecycle**: Sticky per plane TT.
- **Merge**: TO requires all planes clear with evidence.

### `verify-claims`
- **Roles**: Draft → extract claims → blinded verifiers → reconciler.
- **Merge**: TO owns reconciled brief before any build step.

### Internal-only paradigms (telemetry tags)

| Tag | Maps to |
| :--- | :--- |
| `swarm` | `research-swarm` |
| `refine` | `refine-loop` |
| `debate` / `consul` | `debate` |
| `planes` | `plane-audit` |
| `cove` | `verify-claims` |
| `got` / `moa` / `adversarial` | Rare; TO only |

## Durable memory (optional flag, not a topology)

- **`persist: none`** (default) or **`persist: durable`** (host may alias).
- **Writer**: TO only. TTs: read-only if allowlisted. Main does not write.
- Details: [durable-memory.md](durable-memory.md).
