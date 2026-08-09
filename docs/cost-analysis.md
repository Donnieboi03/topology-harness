# Cost Analysis Protocol

Every multi-agent topology run must be analyzed for aggregate token spend (input **and** output). Cost helpers live in this harness (`src/agent_topo_harness`).

## What we actually claim (live A/B truth)

Do **not** promise “Compound Topologies (B) is always cheaper than monolith chat (A).”

Measured with the same model, matrix pricing (in+out), and fair setups:

| Shape | Result |
| :--- | :--- |
| **Fair one user-turn + one retry** (synthetic) | Often **`cost_A ≤ cost_B`** — graph overhead (Main route + TO/leaves) beats a single fat answer call |
| **Same fat on Main, one-shot research/coding** | **A** usually wins **$** and **wall-clock** when B is sequential |
| **Mixed session** (Main-only chat, then different topics) | **A ≈ B** on $ when Main still re-reads the full transcript every route; B’s **TO prompts stay thin** (isolation works) |
| **Forced TO on trivial chat** | **Main-only cheaper** — do not spin a TO for `ls` / one-liners |
| **Parallel scouts/leaves** | Improves **latency**, not $/token (you still pay every leaf) |

**Why agent-topo still earns its keep**

1. **Main gates the TO** — chit-chat and trivial work stay on Main; only non-trivial / multi-step / multi-source work opens a Topic Owner.
2. **Cross-topic isolation** — coding TO must not carry housing/event junk (architecture guarantee; monolith only hopes the model ignores noise).
3. **Scoped tools / blast radius** — thin leaves with explicit toolsets; avoid MCP/vault thrash on every child.
4. **When A’s fat work multiplies** — many tool/think rounds or retries *inside* the growing monolith; B keeps that work on thin sticky leaves.
5. **Parallel leaves** — deep research / multi-plane audit wall-clock when the host fans out.

**Dominant tax:** If Main re-ingests the full archive on every route, **B ≈ A_main + TO/leaf overhead**. Isolation alone does not erase the Main tax.

## 1. Automated Analysis

### Live session tree

From the Virgil repo (wrapper):

```bash
uv run python scripts/graph_analysis/session_cost.py <parent_session_id>
```

Rollup: `agent_topo_harness.cost.analyze_session_tree`.

### Synthetic A/B smoke

```bash
# harness checkout
uv run python -m agent_topo_harness.cost_smoke
# or from Virgil
uv run python scripts/agent_topo_cost_smoke.py
uv run pytest -q
```

Fair baseline: **one user-turn + one retry** for both A and B (same knobs). Asserts **Main-only &lt; forced TO** on trivial work. Does **not** assert `cost_B < cost_A`.

### Live A/B smoke (Virgil)

```bash
uv run python scripts/agent_topo_ab_replay_half.py
```

Replays the **first half** of a real Hermes mega-session user turns (chronological ping/pong). **A and B get the identical user texts and turn count.** A = monolith; B = Main-gated topic-local TOs. Reports cost (in+out matrix), wall-clock, and blind performance.


## 2. Pricing Matrix (Flash-Only)

*Prices per 1M tokens. Prefer live provider rates when billing; this matrix is the default for Flash-tier reports.*

| Model | Input | Output |
| :--- | :--- | :--- |
| `gemini-3.5-flash` | $0.075 | $0.30 |
| `gemini-3-flash-preview` | $0.075 | $0.30 |
| `gemini-2.5-flash` | $0.10 | $0.40 |

Virgil live smokes may use `scripts/llm_pricing.py` (often $0.15 / $0.60 for OpenRouter ids) — pick **one** table per report.

Assume **context caching** helps long Main prefixes when the host enables it. Prefer **sticky leaves** under a TO (reuse scout/Gen/Critiquer sessions) so leaves avoid cold rediscovery — that is reuse hygiene, not a promise vs monolith $.

## 3. Reporting

On completion of a background task (>2 subagents), report:

- **Total topology cost** (input + output)
- **Token split** (prompt vs completion)
- **Top token consumer** (Main vs TO vs which leaf)
- **Control depth** (Main → Topic Owner → leaves)
- **Composition** (compound id) when available from telemetry
- Whether Main **should have stayed in-chat** (trivial) vs opened a TO
