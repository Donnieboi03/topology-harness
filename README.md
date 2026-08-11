# agent-topo-harness

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
│  agent-topo-harness                                     │
│  Main → Topic Orchestrator (TO) → Topic Topology (TT)   │
│  sticky · routing · atomics · evidence · telemetry      │
└─────────────────────────────────────────────────────────┘
```

Without this layer, a host can still fan out workers — typically as fat
children, mixed topics, and unreviewed “just implement” leaves.

---

## Purpose

| Goal | What this package provides |
| :--- | :--- |
| **Control plane** | Roles and spawn invariants (Main / TO / TT) |
| **Topic isolation** | One TO per topic; sticky resume per `(topic, lane)` |
| **Atomic paradigms** | Exactly three URN tags: `swarm`, `plane`, `cove` |
| **Compounds** | Named recipes that wire atomics + non-atomic steps (e.g. `refine-loop`) |
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
| **Atomic** | URN paradigm tag — only `swarm` \| `plane` \| `cove` |
| **Compound** | Named recipe under a TO (may include non-atomic wiring like `refine-loop`) |
| **`to_only`** | Intent action: resume sticky TO only (no TT re-fan) |
| **`topic_owner` / `leaf`** | Accepted **API aliases** for TO / TT — prefer TO / TT in new prose |

### The three atomics

| Atom (user verb) | URN paradigm | Intent |
| :--- | :--- | :--- |
| `research-swarm` | `swarm` | Parallel scouts / breadth |
| `plane-audit` | `plane` | Orthogonal risk lenses |
| `verify-claims` | `cove` | Claim extraction + verification |

`refine-loop` (Generator / Critiquer), `debate`, and `to-brief` are **not**
atomics. Put them in **`composition`** / compound wiring. Passing them as
`atom=` raises `NotAtomicError`.

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
cd /path/to/agent-topo-harness
uv sync
uv run python -m agent_topo_harness.cost_smoke
uv run pytest
```

Python package: `src/agent_topo_harness/`.

See [install.md](install.md) for host wiring checklist.

---

## Utilization (host cookbook)

### 1. Sticky registry

```python
from agent_topo_harness import StickyRegistry, sticky_path_for_session

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
from agent_topo_harness import (
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
from agent_topo_harness import assert_spawn_policy

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
from agent_topo_harness import topo_gate, assert_topic_open

@topo_gate(reg)
def spawn_tt(topic: str, lane: str) -> None:
    ...
```

### 5. Topology URN

```python
from agent_topo_harness import make_topology_urn, workflow_slug_for, resolve_paradigm

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
from agent_topo_harness import assert_can_write

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
| Atomic-only URN tags | `paradigm_for_atom` / `NotAtomicError` | Pass atomics only in `atom=` |
| Nest depth / TT cannot spawn | — | Runtime nest limits |
| Critiquer PASS / stub shape | prompts + soft helpers | Block “done” without gates |

---

## Docs index

| Doc | Topic |
| :--- | :--- |
| [SKILL.md](SKILL.md) | Agent-facing overview + checklist |
| [docs/README.md](docs/README.md) | Full doctrine index |
| [docs/agent-topologies.md](docs/agent-topologies.md) | Atomics + patterns |
| [docs/compounds.md](docs/compounds.md) | Named compounds |
| [docs/sticky-registry.md](docs/sticky-registry.md) | Sticky TO/TT registry |
| [docs/intent-routing.md](docs/intent-routing.md) | Route actions |
| [docs/graph_telemetry.md](docs/graph_telemetry.md) | URN + siblings |
| [docs/evidence-gates.md](docs/evidence-gates.md) | Hard exits for refine wiring |
| [docs/durable-memory.md](docs/durable-memory.md) | Optional persist |
| [install.md](install.md) | Host wiring |

---

## License

See repository license file if present; otherwise treat as private until published.
