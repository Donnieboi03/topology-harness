# agent-topo-harness

**Compound Topologies** — portable **orchestration policy** for multi-agent work.

This package is **not** a chat runtime and **not** a full agent OS. A host (any
system that can spawn nested workers) supplies chat, tools, and sessions. This
harness defines **who may spawn whom**, topic isolation, compounds, sticky
lanes, and evidence gates.

| Layer | Role |
| :--- | :--- |
| **Host runtime** | Chat, spawn/resume, tools, sessions |
| **This harness** | Policy / graph: Main → TO → TT |

## Glossary

| Term | Meaning |
| :--- | :--- |
| **Main** | Talking agent; gates work; handles chit-chat |
| **TO** | **Topic Orchestrator** — one per topic; mid-tier composer of compounds. Host spawn `role=orchestrator` is the same role (API name), not a fourth role. Prefer the acronym **TO** in prose once expanded. |
| **TT** | **Topic Topology** worker under a TO (scout, plane, generator, …). Not the product name. |
| **Compound Topologies** | The product / doctrine name for this control plane |
| **`to_only`** | Intent action: resume the sticky TO only (no TT re-fan) |
| **`topic_owner` / `leaf`** | Accepted **API aliases** for TO / TT — prefer **TO** / **TT** in docs and new code |

## Install

```bash
# from this checkout
uv sync
uv run python -m agent_topo_harness.cost_smoke
uv run pytest
```

See [install.md](install.md) for host wiring.

## Docs

Start at [docs/README.md](docs/README.md) and [SKILL.md](SKILL.md).

## Cost stance

Do **not** claim the topology graph is always cheaper than a monolith. Measure
with your host’s pricing table. Isolation, scoped tools, and sticky resume are
the product value; $/token depends on the workload.

## License

See repository license file if present; otherwise treat as private until published.
