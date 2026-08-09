# Multi-Agent Topology Telemetry

Beyond cost and tokens, Compound Topologies need metadata to optimize cognitive dynamics. Harness id: **`agent-topo-harness`**.

## Key Metrics

### 1. Topology & Tracing

- **harness**: `agent-topo-harness`
- **topology_type**: `DAG`, `Cyclic`, `TreeOfThought`, `MixtureOfAgents`, `TopicOwner`, `Compound`.
- **control_plane**: `main | topic_owner | leaf`.
- **pattern**: `research-swarm | refine-loop | debate | plane-audit | verify-claims | …` (atom actually running).
- **composition** / **pattern_composition**: compound id or ordered/parallel atom list wired by the TO.
- **paradigm** (telemetry tag): `swarm`, `refine`, `cove`, …
- **loop_cycle_index**: Iteration count in refine / self-correction loops.
- **backtracked**: Boolean; true if a search path was abandoned.
- **persist_durable**: Boolean; durable memory in scope for the run (`persist_vault` legacy alias OK).
- **durable_writer**: always `topic_owner` when writes occur (`vault_writer` legacy alias OK).
- **evidence_gates_passed**: Boolean or per-gate map (`tests`, `typecheck`, `lint`, `docs`, …).
- **critical_escalations**: Count (and optional ids) of Leaf→TO→Main→host-channel mediations.
- **critical_channel**: Host channel id (`telegram`, `slack`, `web`, …).

### 2. Cognitive Dynamics

- **Consensus Score**: Semantic agreement ratio across parallel experts.
- **Variance of Critiques**: Spread of auditor scores.
- **Calibrated Confidence**: Self-reported agent confidence (0.0–1.0).

### 3. Resource Profiling

- **Parallel Efficiency**: Active computation vs wall-clock time.
- **TTFT**: Latency to first token on subagent calls.
- **Retry count**: User or Topic Owner fix loops before acceptance.

## JSON Telemetry Schema

Prefer the field names above when extending host telemetry so A/B cost smoke and session rollup share naming with **agent-topo-harness**. A formal JSON schema file is optional and not shipped in this repo yet.
