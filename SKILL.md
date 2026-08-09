---
name: agent-topo-harness
description: "Compound Topologies control plane — Main routes flat Topic Owners; TOs compose atoms into compounds; evidence gates, Telegram critical mediation, TO-only vault. Use for multi-agent orchestration in Virgil/Hermes."
version: 0.1.0
---

# agent-topo-harness

Control plane for **Compound Topologies**: baseline pattern **atoms** composed into **compounds** by Topic Owners. Skills policy + Python helpers live in this package (same shape as browser-harness: root `SKILL.md`, `docs/`, `src/`).

| Label | Meaning |
| :--- | :--- |
| **A** | Monolithic chat agent |
| **B** | Compound Topologies (Main → flat Topic Owners → pattern leaves) |

**Agent Topologies** = catalog brand. Do not use DTO / “Delegated Topic Orchestration.”

For install / Hermes nest patch / Virgil wiring, read [install.md](install.md).

**Enforcement (not honor-system only):** host adapters apply prefill + hooks + OpenRouter preference/fallback **allowlist** from [`config/models.yaml`](config/models.yaml). Hermes: `./scripts/apply_agent_topo_harness.sh` (see [install.md](install.md)). Edit that YAML; re-apply; restart the host gateway.

## Roles

1. **Main** — chat, scope + tooling card, optional `composition:` hint, spawn flat TOs or trivial work, mediate critical approvals via Hermes Telegram. Never vault-write.
2. **Topic Owner** — builds compounds from atoms; owns the brief; sole agent vault writer when `persist: vault`; nest-delegates leaves only (`role=orchestrator`, depth 1).
3. **Leaves** — job-sized context; no nest-delegate; no vault write; read-only retrieval if allowlisted.

## Spawn policy

| Caller | May spawn | Must not |
| :--- | :--- | :--- |
| **Main** | Flat Topic Owner(s); or one trivial leaf | Nested TOs; heavy paradigms in-chat; vault writes |
| **Topic Owner** | Pattern leaves / atom mix | Another TO; raw scout dumps to Main/vault |
| **Leaf** | Nothing | Nest-delegate; vault write |

**Trivial:** Main in-chat for `ls`/one-shot; larger single job → one leaf (`background=True`). Never a TO.

## Docs (this repo)

| Doc | Purpose |
| :--- | :--- |
| [docs/agent-topologies.md](docs/agent-topologies.md) | Atom catalog |
| [docs/compounds.md](docs/compounds.md) | Named compounds (normal unit of work) |
| [docs/scope-and-tooling-card.md](docs/scope-and-tooling-card.md) | Main→TO envelope |
| [docs/to-brief-template.md](docs/to-brief-template.md) | TO brief schema |
| [docs/evidence-gates.md](docs/evidence-gates.md) | Critiquer exits |
| [docs/critical-escalation.md](docs/critical-escalation.md) | Leaf→TO→Main→Telegram |
| [docs/vault-write-policy.md](docs/vault-write-policy.md) | TO-only agent writes |
| [docs/cost-analysis.md](docs/cost-analysis.md) | Costing + A/B smoke |
| [docs/graph_telemetry.md](docs/graph_telemetry.md) | Telemetry fields |

## Compounds (prefer)

| Compound | Wiring |
| :--- | :--- |
| `debug-compound` | `plane-audit` → TO brief → `refine-loop` |
| `research-build` | `research-swarm` → TO brief → `refine-loop` |
| `decide-then-audit` | `debate` → `plane-audit` → optional `refine-loop` |
| `verify-then-build` | `verify-claims` → TO brief → `refine-loop` |

Atoms alone are incomplete; **compounds** are the default unit. Keep `debate` ≠ `plane-audit`.

## Python helpers

```bash
cd ~/Developer/agent-topo-harness
uv run python -m agent_topo_harness.cost_smoke
```

Package modules: `compounds`, `scope`, `evidence`, `escalate`, `vault_policy`, `cost`, `telemetry`, `templates`, `models`.

## Verification checklist

- [ ] Host adapter applied (`apply_*.sh`); gateway restarted; `OPENROUTER_API_KEY` set if using OpenRouter
- [ ] Main routes only (or trivial leaf); no Main vault write; no TO→TO
- [ ] Scope + tooling card (+ optional composition) to each TO
- [ ] Work runs as a compound (or justified novel composition)
- [ ] TO owns brief before producer; evidence exits enforced
- [ ] Critical path uses Hermes Telegram UI
- [ ] `persist: vault` → TO-only writes
- [ ] Cost smoke / tree rollup for multi-agent runs
- [ ] Models used are subset of `config/models.yaml` allowlist
