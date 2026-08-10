# Cost Analysis Protocol

Every multi-agent topology run should be analyzed for aggregate token spend
(input **and** output). Cost helpers live in this harness (`src/agent_topo_harness`).

## What we claim

Do **not** promise Compound Topologies (B) is always cheaper than monolith chat (A).

| Shape | Expected stance |
| :--- | :--- |
| Fair **one user-turn + one retry** (synthetic `cost_smoke`) | Often **A ≤ B** — graph overhead |
| Forced Orchestrator on trivial chat | **Main-only cheaper** — never open an Orchestrator for one-liners |
| Parallel TTs | Improves **latency** vs sequential TTs, **not** $/token |

**What B still buys (even when $ is higher)**

1. **Main gates the Orchestrator** — chit-chat stays on Main.
2. **Cross-topic isolation** — unrelated topics do not share one fat transcript.
3. **Scoped tools / blast radius** — explicit toolsets on TTs.
4. **Sticky session pool** — [`StickyRegistry`](sticky-registry.md); follow-ups use [intent routing](intent-routing.md) (`to_only` default). TTs return [stubs](tt-stubs.md).
5. **When fat tool work multiplies inside A** — isolation pays when tools thrash.

**Dominant tax:** If Main re-ingests the full archive every turn, **B ≈ A_main + graph overhead**. Isolation thins Orchestrator/TTs; it does not erase Main’s transcript tax.

## Control plane vs host

| | **Host runtime** | **Compound Topologies (this harness)** |
| :--- | :--- | :--- |
| What it is | Chat, spawn, tools, sessions | Who may spawn whom, topic isolation, compounds, sticky, gates |
| Spawning | Can spawn workers | Says *when* and *as what* (Main vs Orchestrator vs TT) |
| Without this layer | Flat “Main delegates whatever” | Easy to get fat children, Orchestrator nesting, tool thrash |

## Automated analysis

### Session tree (host DB)

```bash
export AGENT_TOPO_STATE_DB=/path/to/host/sessions.db
# then call analyze_session_tree(parent_id) from Python
```

### Synthetic A/B smoke

```bash
uv run python -m agent_topo_harness.cost_smoke
```

Asserts Main-only &lt; forced Orchestrator on trivial work. Does **not** assert `cost_B < cost_A`.

## Pricing — one table per report

Pick a single $/1M table per comparison. Synthetic smoke uses the harness Pro-tier
constants in `cost.py`. Host A/B scripts may use a different matrix — **do not mix**.

Sticky resume ≠ provider prompt-cache hits.

## Reporting

On completion of a multi-worker task, report:

- Total topology cost (input + output USD)
- Token split (prompt vs completion)
- Top token consumer (Main vs Orchestrator vs which TT)
- Control depth (Main → Orchestrator → TTs)
- Composition (compound id) when available
- Whether Main should have stayed in-chat vs opened an Orchestrator
- Sticky or cold spawn
