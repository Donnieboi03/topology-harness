# Multi-Agent Topology Telemetry

Beyond cost and tokens, Compound Topologies need metadata to optimize cognitive dynamics. Harness id: **`agent-topo-harness`**.

## Key Metrics

### 1. Topology & Tracing

- **harness**: `agent-topo-harness`
- **topology_type**: `DAG`, `Cyclic`, `TreeOfThought`, `MixtureOfAgents`, `TopicOwner`, `Compound`.
- **control_plane**: `main | topic_owner | leaf`.
- **pattern**: `research-swarm | refine-loop | debate | plane-audit | verify-claims | …` (atom actually running).
- **composition** / **pattern_composition**: compound id (`debug-compound`, `research-build`, …) or ordered/parallel atom list actually wired by the TO.
- **paradigm** (telemetry tag): `swarm`, `refine`, `cove`, …
- **loop_cycle_index**: Iteration count in refine / self-correction loops.
- **backtracked**: Boolean; true if a search path was abandoned.
- **persist_vault**: Boolean; durable memory flag for the run.
- **vault_writer**: always `topic_owner` when writes occur (Main/leaves never).
- **evidence_gates_passed**: Boolean or per-gate map (`tests`, `typecheck`, `lint`, `docs`, …).
- **critical_escalations**: Count (and optional ids) of Leaf→TO→Main→Telegram critical mediations.

### 2. Cognitive Dynamics

- **Consensus Score**: Semantic agreement ratio across parallel experts.
- **Variance of Critiques**: Spread of auditor scores.
- **Calibrated Confidence**: Self-reported agent confidence (0.0–1.0).

### 3. Resource Profiling

- **Parallel Efficiency**: Active computation vs wall-clock time.
- **TTFT**: Latency to first token on subagent calls.
- **Retry count**: User or Topic Owner fix loops before acceptance.

## JSON Telemetry Schema

Stored in `references/graph_telemetry_schema.json` when present. Prefer fields above when extending the schema so A/B cost smoke and session rollup share naming with **agent-topo-harness**.
