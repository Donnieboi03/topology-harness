# topology-harness

**Compound Topologies** — a portable **control-plane policy package** for
multi-agent systems.

This repository is **not** a chat app, **not** a model router, and **not** a
full agent OS. A **host** (any runtime that can spawn nested workers with
sessions and tools) owns those concerns. This harness defines the **rules of
the graph**: who may spawn whom, how topics stay isolated, which patterns are
atomic, how sticky handles work, and which checks fail closed.

```
┌─────────────────────────────────────────────────────────┐
│  Host runtime                                           │
│  chat UI · spawn/resume · tools · sessions · billing    │
└──────────────────────────┬──────────────────────────────┘
                           │ calls helpers / honors policy
┌──────────────────────────▼──────────────────────────────┐
│  topology-harness                                     │
│  Main → Topic Orchestrator (TO) → Topic Topology (TT)   │
│  sticky · routing · atomics · evidence · telemetry      │
└─────────────────────────────────────────────────────────┘
```

Without this layer, a host can still fan out workers — typically as fat
children, mixed topics, and unreviewed “just implement” leaves.

### Cursor / agent CLI

When Cursor Rules install this package, **Cursor is the host**:

```bash
uv tool install -e .          # topology-harness on PATH
topology-harness --doctor
topology-harness cursor-map
topology-harness doctrine
```

Always-apply rule: `~/.cursor/rules/topology-harness.mdc`  
Skill: `~/.cursor/skills/topology-harness/` → this repo’s `SKILL.md`  
Adapter: [docs/adapters/cursor.md](docs/adapters/cursor.md)  
Details: [install.md](install.md)

Other hosts bind the same helpers to their own spawn API; see utilization below.

---

## Purpose

| Goal | What this package provides |
| :--- | :--- |
| **Control plane** | Roles and spawn invariants (Main / TO / TT) |
| **Topic isolation** | One TO per topic; sticky resume per `(topic, lane)` |
| **Atomic paradigms** | Exactly four URN tags: `swarm`, `plane`, `cove`, `shard` |
| **Combinators** | Public menu: `cycle` only; public transition: `revise` only |
| **Compounds** | Named recipes that wire atoms and combinator applications |
| **Fail-closed helpers** | Durable-write gate, spawn policy, topic-open gate, route coerce |
| **Telemetry** | Topology URNs + sibling fields (`composition`, `parent_run_id`, …) |

**Non-goals:** implementing Telegram/IDE chat, patching a specific host’s
delegate tool, or owning durable-memory backends. Hosts map `persist: durable`
and critical escalation to their own stores and channels.

---

## Glossary

| Term | Meaning |
| :--- | :--- |
| **Main** | User-facing agent; routes work; handles chit-chat |
| **TO** | **Topic Orchestrator** — one per topic; composes compounds; user-facing voice for that topic. Host API name is often `role=orchestrator`. |
| **TT** | **Topic Topology** worker under a TO (scout, plane lens, verifier, …) |
| **Atom** | URN paradigm tag — public menu only `swarm` \| `plane` \| `cove` \| `shard`. An instance of `fan(partition, worker, merge)`, individuated by merge algebra |
| **Combinator** | Public menu: `cycle` only (wraps an atom; carries state between rounds) |
| **Transition** | Public menu: `revise` only (mutates the subject between cycle rounds) |
| **Compound** | Named recipe under a TO — prefer the five recipes; a DAG over atoms and combinator applications |
| **`to_only`** | Intent action: resume sticky TO only (no TT re-fan) |
| **`topic_owner` / `leaf`** | Accepted **API aliases** for TO / TT — prefer TO / TT in new prose |

### The four atoms

There is only one *shape* — a fan from the TO to blind workers and back. The
atoms differ by **merge algebra**, which is what makes each one a distinct,
checkable contract. Full rationale: [docs/atom-theory.md](docs/atom-theory.md).

| Atom | Merge algebra | Intent |
| :--- | :--- | :--- |
| `swarm` | union | Parallel scouts / breadth |
| `plane` | conjunction | Orthogonal risk lenses |
| `cove` | per-claim adjudication | Claim extraction + verification |
| `shard` | assembly under a contract | Interlocking pieces of one deliverable |

### The combinator layer

**Public menu:** combinator `cycle`, transition `revise`. Prefer named compounds
([docs/compounds.md](docs/compounds.md)).

```
cycle(atom, revise, accept, bound)
```

Passing non-atoms as `atom=` raises `NotAtomicError`.

---

## Control plane

```
Main
  └── TO(s)     ← flat only (no TO→TO)
        └── TT workers    ← atomics / compound steps; no further topology spawn
```

| Role | Does | Must not |
| :--- | :--- | :--- |
| **Main** | Open/resume TO(s); trivial chat or (rare) informal leaf | Nested TOs; substantive implement-as-leaf; TO for pure chit-chat |
| **TO** | Compose compounds; merge TT stubs; durable writes when persist on | Spawn another TO; mix unrelated topics |
| **TT** | One lens / step; return stubs | Spawn; speak as the product voice |

**Informal Main→leaf** is only for throwaway Q&A. Substantive topic work,
atomics, compounds, and “implement/formalize/audit” goals must go
**Main → TO → TT**. The harness enforces this via `assert_spawn_policy` when
the host calls it.

---

## Install

```bash
cd /path/to/topology-harness
uv sync
uv run python -m topology_harness.cost_smoke
uv run pytest
```

Python package: `src/topology_harness/`.

See [install.md](install.md) for host wiring checklist.

---

## Utilization (host cookbook)

### 1. Sticky registry

```python
from topology_harness import StickyRegistry, sticky_path_for_session

reg = StickyRegistry(host_session_id="parent-session-id")
to, created = reg.get_or_create_orchestrator(
    "auth-refresh",
    topology_urn="topology:topic:auth-refresh--to:01A",
    composition="debug-compound",
)
tt, _ = reg.get_or_create_tt("auth-refresh", "security")
reg.bind_session(to, "child-session-to")
reg.save(sticky_path_for_session(state_dir, "parent-session-id"))
```

### 2. Intent routing

```python
from topology_harness import (
    parse_route_decision,
    coerce_route_with_registry,
)

decision = coerce_route_with_registry(
    parse_route_decision(raw_from_main),
    open_topics=reg.open_topics(),
)
# open_topic → to_only when the topic is already sticky-open
```

### 3. Spawn policy (closes Main→leaf escape hatch)

```python
from topology_harness import assert_spawn_policy

paradigm = assert_spawn_policy(
    parent_depth=0,          # Main
    role="orchestrator",     # required for substantive/topic work
    topic="auth-refresh",
    goal=user_goal,
    open_topics=reg.open_topics(),
)
# Raises SpawnPolicyError if Main tries leaf for topic/atomic/implement work
```

Under a TO (`parent_depth >= 1`), spawn TTs with an atomic or composition:

```python
paradigm = assert_spawn_policy(
    parent_depth=1,
    role="leaf",
    topic="auth-refresh",
    lane="security",
    atom="plane-audit",          # → plane
    composition="debug-compound",
    goal="Security plane audit",
)
```

### 4. Topic-open gate

```python
from topology_harness import topo_gate, assert_topic_open

@topo_gate(reg)
def spawn_tt(topic: str, lane: str) -> None:
    ...
```

### 5. Topology URN

```python
from topology_harness import make_topology_urn, workflow_slug_for, resolve_paradigm

urn = make_topology_urn(
    resolve_paradigm(atom="plane-audit"),
    workflow_slug_for("auth-refresh", "security"),
)
# topology:plane:auth-refresh--security:<ulid>
```

Sibling fields (not in the URN): `composition`, `control_plane`, `parent_run_id`,
`persist`, `sticky`, … via `sibling_telemetry_fields`.

### 6. Durable writes

```python
from topology_harness import assert_can_write

assert_can_write("orchestrator")  # TO only — Main/TT raise PermissionError
```

Hosts must wrap every durable-store write. Prefer `persist: durable` (alias
`vault`) on TO open when memory should compound.

### 7. Evidence / stubs / compounds

- Compounds: `get_compound("debug-compound")` — see [docs/compounds.md](docs/compounds.md)
- TT stubs: `TT_STUB_INSTRUCTION`, `parse_tt_stub` — soft helpers; host must honor
- Evidence: `missing_gates` / `all_gates_passed` — advisory unless host blocks

---

## What is fail-closed vs prompt-soft

| Policy | Harness | Host must |
| :--- | :--- | :--- |
| TO-only durable writes | `assert_can_write` | Wrap writes / block Main store tools |
| Main→leaf for topic work | `assert_spawn_policy` | Call before every spawn |
| Topic must be open | `topo_gate` / `assert_topic_open` | Decorate TT spawn helpers |
| open→to_only when sticky | `coerce_route_with_registry` | Call after parse |
| Atom-only URN tags | `paradigm_for_atom` / `NotAtomicError` | Pass atoms only in `atom=` |
| Closed transition / combinator sets | `assert_transition` / `assert_combinator` | Pass validated values |
| Nest depth / TT cannot spawn | — | Runtime nest limits |
| Critiquer PASS / stub shape | prompts + soft helpers | Block “done” without gates |

---

## Docs index

| Doc | Topic |
| :--- | :--- |
| [SKILL.md](SKILL.md) | Agent-facing overview + checklist |
| [docs/README.md](docs/README.md) | Full doctrine index (hot / operational / optional deep) |
| [docs/agent-topologies.md](docs/agent-topologies.md) | Atoms + combinators (pattern library) |
| [docs/compounds.md](docs/compounds.md) | Named compounds |
| [docs/host-contracts.md](docs/host-contracts.md) | Host sticky + retire contracts |
| [install.md](install.md) | Host wiring |

Optional deep: [docs/atom-theory.md](docs/atom-theory.md).

---

## License

See repository license file if present; otherwise treat as private until published.
