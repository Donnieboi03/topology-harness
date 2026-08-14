# Cursor adapter

Compound Topologies is **host-agnostic**. With Cursor Rules / Skills installed,
**Cursor is the host**: implement Main / TO / TT with Cursor primitives.

## Role map

| Control-plane role | Cursor primitive |
| :--- | :--- |
| Main | Primary agent in the chat |
| TO (Topic Orchestrator) | `Task` with `subagent_type=generalPurpose` (or equivalent), one per topic |
| TT (Topic Topology worker) | `Task` with `explore` / `generalPurpose` / `shell` — lens or atom only |

## Routing

Main chooses (internally) the same actions as [intent-routing.md](../intent-routing.md):

`main_only` | `open_topic` | `to_only` | `lens_resume` | `full_refan`

Default follow-up bias: **`to_only`**. Coerce `open_topic` → `to_only` when the
topic is already sticky-open (`coerce_route_with_registry`).

Do **not** wait for the user to say “use multi-agent” or “use a compound.”

## Sticky

Cursor Tasks are short-lived. Approximate sticky continuity with a workspace
registry file:

```text
.cursor/topology-sticky/registry.json
```

Use `StickyRegistry` from `topology_harness`. The registry’s session id field is
an opaque host key (e.g. `cursor` or the repo name). Shared sticky fields and
the retire-flush contract are documented in [host-contracts.md](../host-contracts.md).

Sticky is **ephemeral**: after load call `purge_idle()` (24h TO-touch TTL →
release only); inject Main context via `topics_for_main(limit=1)`; on session
end `release_all` / delete the file. Not a knowledge archive — BB/KG is.

On open: `get_or_create_orchestrator(topic)` and store a brief digest / last Task
label in `meta`. On resume: load the registry and pass the prior brief into the
next TO Task prompt.

On topic close: call `retire_topic(...)` (blackboard) then `release_topic(topic)`.
See [durable-memory.md](../durable-memory.md). Idle TTL never auto-retires.

Add `.cursor/topology-sticky/` to `.gitignore` if the file should stay local.

## Spawn policy

Before Main launches worker Tasks for substantive / sticky-open / atomic work,
apply `assert_spawn_policy` intent: **open or resume a TO first**.
TTs are launched by the TO (or by Main only as a single trivial TT).

Inject `TT_STUB_INSTRUCTION` into every TT Task prompt. TO merges stubs into the
user-facing answer.

## Compounds

List recipes with `topology-harness compounds` / `get_compound(...)`. Wire lenses
as parallel TT Tasks under one TO; merge before answering the user.

## Durable memory

If the workspace has a vault or memory write path: **TO-only** writes
(`assert_can_write`). Main and TT Tasks must not upsert durable memory.
Prefer the regioned blackboard (`Blackboard` / `retire_topic`) — see
[host-contracts.md](../host-contracts.md).

## CLI

```bash
topology-harness cursor-map
topology-harness doctrine
topology-harness --doctor
```
