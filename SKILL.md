---
name: agent-topo-harness
description: "Compound Topologies control plane — Main → flat Topic Owners → compounds of atoms. Host-agnostic; optional durable memory + critical human channel via host mappings."
version: 0.2.0
---

# agent-topo-harness

Control plane for **Compound Topologies**: baseline pattern **atoms** composed into **compounds** by Topic Owners.

| Label | Meaning |
| :--- | :--- |
| **A** | Monolithic chat agent |
| **B** | Compound Topologies (Main → flat Topic Owners → pattern leaves) |

**Agent Topologies** = catalog brand. Plugs into **any** agent host that can spawn nested workers. Install / host wiring: [install.md](install.md).

## Core (required)

1. **Main** — talking agent; routes non-trivial work; scope + tooling card; optional `composition:` hint; mediates critical approvals via the **host** human channel. Does not run heavy paradigms in-chat.
2. **Topic Owner** — builds compounds from atoms; owns the brief; nest-delegates leaves only (depth 1). Sole agent writer of durable memory **when** persist is enabled.
3. **Leaves** — job-sized context; no nest-delegate; no durable writes.

| Caller | May spawn | Must not |
| :--- | :--- | :--- |
| **Main** | Flat Topic Owner(s); or one trivial leaf | Nested TOs; heavy work in-chat |
| **Topic Owner** | Pattern leaves / atom mix | Another TO; raw scout dumps to Main |
| **Leaf** | Nothing | Nest-delegate |

**Trivial:** Main in-chat for `ls`/one-shot; larger single job → one leaf. Never a TO.

Compounds are the default unit of work ([docs/compounds.md](docs/compounds.md)). Evidence gates on refine/critique ([docs/evidence-gates.md](docs/evidence-gates.md)).

## Optional capabilities (host mappings)

| Capability | Core contract | Not assumed |
| :--- | :--- | :--- |
| **Durable memory** | [docs/durable-memory.md](docs/durable-memory.md) — TO-only writes when `persist: durable` | Vault / Obsidian / any specific store |
| **Critical approval** | [docs/critical-escalation.md](docs/critical-escalation.md) — Leaf→TO→Main→**host channel** | Telegram specifically |
| **Spawn primitive** | Nest TO→leaves at depth 1 | Hermes `delegate_task` |
| **Model routing** | Preference + allowlist ([config/models.yaml](config/models.yaml)) | OpenRouter |

Hermes/Virgil mappings are **host-owned** (Virgil: `docs/compound-topologies/`, nest patch, hooks/prefill). See [install.md](install.md).

## Docs

| Doc | Purpose |
| :--- | :--- |
| [docs/agent-topologies.md](docs/agent-topologies.md) | Atom catalog |
| [docs/compounds.md](docs/compounds.md) | Named compounds |
| [docs/scope-and-tooling-card.md](docs/scope-and-tooling-card.md) | Main→TO envelope |
| [docs/to-brief-template.md](docs/to-brief-template.md) | TO brief schema |
| [docs/evidence-gates.md](docs/evidence-gates.md) | Critiquer exits |
| [docs/critical-escalation.md](docs/critical-escalation.md) | Critical ladder (portable) |
| [docs/durable-memory.md](docs/durable-memory.md) | Optional persist policy |
| [docs/cost-analysis.md](docs/cost-analysis.md) | Costing + A/B smoke |
| [docs/graph_telemetry.md](docs/graph_telemetry.md) | Telemetry fields |

## Compounds (prefer)

| Compound | Wiring |
| :--- | :--- |
| `debug-compound` | `plane-audit` → TO brief → `refine-loop` |
| `research-build` | `research-swarm` → TO brief → `refine-loop` |
| `decide-then-audit` | `debate` → `plane-audit` → optional `refine-loop` |
| `verify-then-build` | `verify-claims` → TO brief → `refine-loop` |

Keep `debate` ≠ `plane-audit`.

## Python helpers

```bash
cd ~/Developer/agent-topo-harness
uv run python -m agent_topo_harness.cost_smoke
```

Modules: `compounds`, `scope`, `evidence`, `escalate`, `durable_memory` (`vault_policy` alias), `cost`, `telemetry`, `templates`, `models`.

## Verification checklist

- [ ] Main routes only (or trivial leaf); no TO→TO
- [ ] Scope + tooling card (+ optional composition) to each TO
- [ ] Work runs as a compound (or justified novel composition)
- [ ] TO owns brief before producer; evidence exits enforced
- [ ] Critical path uses host human-approval channel
- [ ] If persist enabled → TO-only durable writes (host maps the store)
- [ ] Models subset of `config/models.yaml` allowlist when using harness routing
- [ ] Host glue applied if using Hermes (Virgil `apply_*.sh`); gateway restarted
