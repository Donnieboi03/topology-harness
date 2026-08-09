# Cost Analysis Protocol

Every multi-agent topology run must be analyzed for aggregate token spend. Cost capabilities live in this harness (`src/agent_topo_harness`).

## 1. Automated Analysis

### Live session tree

From the Virgil repo (wrapper):

```bash
uv run python scripts/graph_analysis/session_cost.py <parent_session_id>
```

Rollup is implemented in `agent_topo_harness.cost.analyze_session_tree`.

### Synthetic A/B smoke

Compare monolithic chat (**A**) vs Compound Topologies (**B**):

```bash
# from Virgil root
uv run python -m agent_topo_harness.cost_smoke
# or (sets path itself)
uv run python scripts/agent_topo_cost_smoke.py
uv run pytest -q
```

Smoke uses a synthetic cached Gemini pricing model: fat-\(C_0\) expects `cost_B < cost_A`; trivial Main-only should beat a forced Topic Owner.

## 2. Pricing Matrix (Flash-Only)

*Prices per 1M tokens. Prefer live Gemini Standard rates when billing; this matrix is the default for Flash-tier reports.*

| Model | Input | Output |
| :--- | :--- | :--- |
| `gemini-3.5-flash` | $0.075 | $0.30 |
| `gemini-3-flash-preview` | $0.075 | $0.30 |
| `gemini-2.5-flash` | $0.10 | $0.40 |

Assume **context caching** is on for long Main prefixes; Topic Owner / leaf prompts are mostly cold unless a refine-loop reuses a stable code prefix.

## 3. Reporting

On completion of a background task (>2 subagents), report:

- **Total topology cost**
- **Token efficiency** (input vs output)
- **Top token consumer** (which role burned the most)
- **Control depth** (Main → Topic Owner → leaves)
- **Composition** (compound id / atom wiring) when available from telemetry
