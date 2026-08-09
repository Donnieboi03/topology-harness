# Hermes `delegate_tool` nest-orchestrator patch

Durable Virgil patch so **Compound Topologies** can run: Main spawns flat
**Topic Owners** with `role=orchestrator` at depth 1; each TO nest-delegates
**leaf** workers; leaves cannot nest further.

Upstream Hermes (default `max_spawn_depth=1`) silently forces
`role=orchestrator` → `leaf`, which breaks Topic Owner nest-delegation.
This patch is wiped on `hermes` / `hermes-agent` upgrade — re-apply after every
upgrade.

## Apply

From the agent-topo-harness repo:

```bash
./scripts/apply_hermes_delegate_patch.sh  # adapters/hermes/delegate_tool
```

Idempotent: if `VIRGIL_NEST_ORCHESTRATOR_PATCH` is already present in the live
file, the script exits 0 without re-patching.

## Behavior (after patch)

| Caller | Child role | Result |
|--------|------------|--------|
| Main (depth 0) | `orchestrator` | Child keeps `delegate_task` (Topic Owner) when `max_spawn_depth >= 2` |
| Topic Owner (depth 1) | `leaf` (default) | Worker; **no** `delegate_task` |
| Topic Owner | `orchestrator` | **ERROR** — no nested TOs (depth floor) |
| Anyone | `orchestrator` when kill-switch off or depth too deep | **ERROR** (not silent leaf) |

Defaults changed: module `MAX_DEPTH` **1 → 2** so nest works even if
`delegation.max_spawn_depth` is unset. Virgil profile should still set
`delegation.max_spawn_depth: 2` and `orchestrator_enabled: true`.

## Files

| File | Purpose |
|------|---------|
| `nest_orchestrator.patch` | Unified diff vs hermes-agent **0.15.2** stock |
| `delegate_tool.patched.py` | Full patched copy (fallback if `patch` fails / upstream drifted) |
| `NOTES.md` | Findings from the live install on this machine |
| `STOCK_MD5.txt` / `STOCK_SOURCE.txt` | Fingerprint of the stock file the `.patch` was cut against |

## Manual fallback

If `patch` rejects (Hermes moved lines), copy the full file:

```bash
LIVE="$(./scripts/apply_hermes_delegate_patch.sh  # adapters/hermes/delegate_tool --print-live)"  # or detect yourself
cp patches/hermes/delegate_tool/delegate_tool.patched.py "$LIVE"
```

Prefer re-cutting the `.patch` against the new stock when upgrading far past
0.15.2 — the full copy may miss unrelated upstream fixes.
