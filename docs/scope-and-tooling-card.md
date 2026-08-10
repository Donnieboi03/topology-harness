# Scope and tooling card

Main → Orchestrator envelope. Pass as structured fields on spawn (host-specific
encoding).

## Fields

| Field | Set by | Binding |
| :--- | :--- | :--- |
| `topic` | Main | Yes — one Orchestrator = one topic |
| `goal` | Main | Yes |
| `composition` | Main hint | No — Orchestrator may rewire / invent compounds |
| `tooling.allow/deny` | Main | Yes — Orchestrator enforces on TTs |
| `persist` | Main | Yes — `none` (default) or `durable`; only Orchestrator writes |
| `caps` | Main | Yes — Orchestrator stops at cap |
| `critical_watchlist` | Main (+ Orchestrator may add) | Yes — escalate via [critical-escalation](critical-escalation.md) → host channel |

## Minimal

- Single TT with a minimal goal string (trivial work).
- Or Orchestrator + `composition:` hint for multi-TT work.
