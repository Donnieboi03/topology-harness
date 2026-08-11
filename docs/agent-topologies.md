# Agent Topologies (pattern library)

**Atomic paradigms** (URN tags) are only three: **`swarm`**, **`plane`**,
**`cove`**. Academic aliases and compound wiring steps are not atomics.

System name: **Compound Topologies**; harness: **agent-topo-harness**.
TOs compose atomics (+ optional non-atomic wiring like `refine-loop`) into
**compounds** — see [compounds.md](compounds.md).

## Control plane (who spawns whom)

```
Main (talking agent)
  └── TO(s)     ← flat only; mid-tier (host role often orchestrator)
        ├── research-swarm   (atomic → swarm)
        ├── plane-audit      (atomic → plane)
        ├── verify-claims    (atomic → cove)
        ├── refine-loop      (wiring / Gen+Critiquer — NOT an atomic URN tag)
        ├── debate           (pattern — NOT an atomic URN tag)
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
| Refine | One Generator + one Critiquer | Another produce/audit round |
| Debate | Additor / Reductor / Consul | Another expand/cut pass |
| Plane-audit | One TT per plane | Re-check that plane after a fix |
| Verify-claims | Draft / verifier / reconciler | Another claim pass |

**Durable memory** is optional. When Main sets `persist: durable`, **TO
is the sole agent writer**. Main never writes; TTs are read-only. See
[durable-memory.md](durable-memory.md).

## Atomics (URN paradigms)

### `research-swarm` → `swarm`
- **Roles**: Scouts with mutually exclusive sub-queries.
- **Lifecycle**: Sticky per scout lens.
- **Merge**: TO writes one brief — [to-brief-template.md](to-brief-template.md).

### `plane-audit` → `plane`
- **Roles**: Independent planes (e.g. security ∥ performance ∥ UX).
- **Lifecycle**: Sticky per plane TT.
- **Merge**: TO requires all planes clear with evidence.

### `verify-claims` → `cove`
- **Roles**: Draft → extract claims → blinded verifiers → reconciler.
- **Merge**: TO owns reconciled brief before any build step.

## Non-atomic patterns (composition / wiring)

These remain useful under a TO but **must not** appear as URN `paradigm`
atom tags (`NotAtomicError` if passed to `paradigm_for_atom`).

### `refine-loop`
- **Roles**: Generator produces from the **TO brief** only; Critiquer
  audits against a checklist or tests.
- **Lifecycle**: Sticky Gen + Critiquer until TO releases.
- **Hard exit gates**: see [evidence-gates.md](evidence-gates.md).
- **Telemetry**: put under `composition` (e.g. compound wiring), not paradigm.

### `debate`
- **Roles**: Additor / Reductor / Consul.
- **Not** `plane-audit` — debate is adversarial scope/value; planes are
  independent risk lenses.

### `to-brief`
- TO synthesis step — not a TT atom and not an atomic paradigm.

## Enforcement honesty

| Policy | Harness | Host must |
| :--- | :--- | :--- |
| TO-only durable writes | `assert_can_write` (fail-closed) | Wrap every write / Main store hook |
| Main→leaf for topic/substantive work | `assert_spawn_policy` | Call before every spawn |
| Topic open before TT work | `topo_gate` / `assert_topic_open` | Decorate spawn helpers |
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

See [graph_telemetry.md](graph_telemetry.md).
