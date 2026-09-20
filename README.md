# topology-harness

**Planner by default for actionable work.** Solo only for easy direct Q&A.

Portable **control-plane policy** for multi-agent hosts. Not a chat app. Not a
model router. Hosts own spawn/resume/tools; this package owns who may spawn whom.

```
Chat
  └── Planner     ← default for implement / edit / multi-step / research
        └── Workers   ← orthogonal stubs; Planner merges
```

| Mode | When |
| :--- | :--- |
| **Solo** | Easy direct question / opinion / meta — one turn, no edits |
| **One helper** | Optional single Worker dig; prefer Planner for multi-step |
| **Planner+workers** | Default for any actionable or multi-step work |

> **Aliases:** Chat = Main · Planner = TO / orchestrator / topic_owner · Worker = TT / leaf

---

## Purpose

| Goal | What you get |
| :--- | :--- |
| Roles | Chat → Planner → Worker |
| Sticky | One Planner per topic; resume map (24h idle TTL) |
| Atoms | `swarm` \| `plane` \| `cove` \| `shard` |
| Combinators | `cycle` + transition `revise` only |
| Fail-closed | `assert_spawn_policy`, `assert_can_write`, `topo_gate`, route coerce |

---

## Glossary (plain first)

| Term | Meaning |
| :--- | :--- |
| **Chat** | User-facing agent; Solo for easy Q&A; opens/resumes Planner; pastes briefs verbatim |
| **Planner** | One topic; fans Workers; authors the brief |
| **Worker** | One orthogonal lens; stub only |
| **Atom** | Fan pattern tagged `swarm` / `plane` / `cove` / `shard` |
| **Compound** | Named recipe wiring atoms (see [docs/compounds.md](docs/compounds.md)) |
| **solo / helper / planner / resume** | Route aliases → `main_only` / One helper / `open_topic` / `to_only` |

---

## Install / CLI

```bash
uv tool install -e .
topology-harness --doctor
topology-harness doctrine
topology-harness cursor-map
topology-harness compounds
```

Cursor rule: [docs/adapters/cursor-rule.mdc](docs/adapters/cursor-rule.mdc) → `~/.cursor/rules/`  
Details: [install.md](install.md)

---

## Utilization

### Sticky

```python
from topology_harness import StickyRegistry, sticky_path_for_session
reg = StickyRegistry(host_session_id="…")
planner, _ = reg.get_or_create_orchestrator("auth-refresh")
reg.save(sticky_path_for_session(state_dir, "…"))
```

### Routing

```python
from topology_harness import parse_route_decision, coerce_route_with_registry
decision = coerce_route_with_registry(
    parse_route_decision(raw), open_topics=reg.open_topics()
)
# aliases: solo→main_only, planner→open_topic, resume→to_only
```

### Spawn policy

```python
from topology_harness import assert_spawn_policy
# Chat→Worker blocked for sticky-open / named topic / atom-compound fans
assert_spawn_policy(
    parent_depth=0, role="planner", topic="auth-refresh", goal="…"
)
# One helper OK without topic when no fan tokens:
assert_spawn_policy(
    parent_depth=0, role="worker", goal="Implement the fix", open_topics=[]
)
```

### Stubs / durable / evidence

- Workers: `WORKER_STUB_INSTRUCTION` (= `TT_STUB_INSTRUCTION`); orthogonal partition
- Durable writes: `assert_can_write("planner")` — Planner only
- Evidence helpers advisory unless host blocks on them

---

## Docs

| Doc | Topic |
| :--- | :--- |
| [SKILL.md](SKILL.md) | Agent card |
| [docs/README.md](docs/README.md) | Index |
| [docs/advanced.md](docs/advanced.md) | Atoms / compounds / CLI |
| [docs/adapters/cursor.md](docs/adapters/cursor.md) | Cursor host |
| [install.md](install.md) | Wiring |

---

## License

Private until published.
