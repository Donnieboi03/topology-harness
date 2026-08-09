# NOTES — live Hermes `delegate_tool.py` (Wave 1d)

## Where found (this machine)

| Path | Notes |
|------|--------|
| **`/opt/homebrew/lib/python3.11/site-packages/tools/delegate_tool.py`** | **Live** — `hermes` / `hermes-agent` **v0.15.2** (`/opt/homebrew/bin/hermes` → python3.11 site-packages). MD5 at cut time: see `STOCK_MD5.txt`. |
| `/Users/donnieb/Desktop/Code/Virgil/.venv/lib/python3.14/site-packages/tools/delegate_tool.py` | Older / different copy (~2801 lines vs 3230). Not what `hermes` CLI loads. |
| `~/.hermes/` | Profile/data only — **no** `delegate_tool.py`. |

Detection used by the apply script: `hermes` on PATH → `sys.path` import of `tools.delegate_tool`, else common Homebrew / venv site-packages globs.

## Stock nesting model (hermes-agent 0.15.2)

- Depth: parent `_delegate_depth` default **0**; each child is `parent + 1`.
- `delegation.max_spawn_depth` (default module `MAX_DEPTH=1`): agents at depth `>= max_spawn` cannot call `delegate_task` (hard JSON error).
- `role=orchestrator` vs `leaf` in `_build_child_agent`:
  - `orchestrator_ok = orchestrator_enabled and child_depth < max_spawn`
  - else **silent** `effective_role = "leaf"` (delegation toolset stripped)
- Leaves: `DELEGATE_BLOCKED_TOOLS` always strips `delegate_task`; orchestrators re-add toolset `"delegation"`.
- Mild post-hoc summary tag already existed: `[WARNING: Role 'orchestrator' degraded to 'leaf']` — easy to miss; topologies look like they ran as a single leaf.

Implication with **default** `max_spawn_depth=1`: Main→child with `role=orchestrator` **always** degrades (because `child_depth=1` is not `< 1`). Nest TO→leaf needs **`max_spawn_depth >= 2`**.

Virgil executor profile already had `max_spawn_depth: 2` + `orchestrator_enabled: true`, but upgrade resets site-packages and a fresh config default still silently breaks Compound Topologies.

## What this patch changes

1. **`MAX_DEPTH` default 1 → 2** — Main(0)→TO(1)→leaf(2) without relying solely on config.
2. **`OrchestratorRoleDenied`** — if `role=orchestrator` would have been forced to leaf, **raise**; `delegate_task` catches and returns `tool_error(...)` with an explicit Compound Topologies / nest-orchestrator message.
3. Louder leftover summary `[ERROR: ...]` if degradation ever slips past build-time.
4. Schema / tool description text: “silently forced to leaf” → documents **ERROR** behavior.

Leaves remain unable to nest (blocklist + depth floor). Nested TO (`role=orchestrator` at depth 2 when max=2) **errors** instead of quietly becoming a leaf.

## Safe apply

Do **not** hand-edit site-packages as the source of truth. Re-run
`scripts/apply_hermes_delegate_patch.sh` after every Hermes upgrade. If
`patch` fails on drift, use `delegate_tool.patched.py` copy fallback or
re-diff against the new stock and update this folder.
