# Scope and tooling card

Main → TO envelope. Pass as structured fields on spawn (host-specific
encoding).

## Fields

| Field | Set by | Binding |
| :--- | :--- | :--- |
| `topic` | Main | Yes — one TO = one topic |
| `goal` | Main | Yes |
| `composition` | Main hint | No — TO may rewire / invent compounds |
| `tooling.allow/deny` | Main | Host-optional. Current hosts often **inherit parent tools** on children (narrow toolsets disabled). Reintroduce with fail-closed validation later. |
| `persist` | Main | Yes — `none` or `durable` (`vault` alias); only TO writes. Prefer `durable`/`vault` on topic opens that should compound. |
| `caps` | Main | Yes — TO stops at cap |
| `critical_watchlist` | Main (+ TO may add) | Yes — escalate via [critical-escalation](critical-escalation.md) → host channel |

## Minimal

- Single TT with a minimal goal string (trivial work).
- Or TO + `composition:` hint for multi-TT work.
