# Scope and tooling card (Main → Topic Owner)

Main attaches this envelope when spawning a Topic Owner. Keep it short; do not paste the full chat.

```markdown
## Scope + tooling card

topic: <kebab-slug>
goal: <one sentence>
in_scope: |
  - …
out_of_scope: |
  - …
composition: <compound-id | freeform hint | omit>
persist: <none | durable | vault>
tooling:
  allow:
    - <skill-or-tool>
  deny:
    - <…>
caps:
  max_rounds: <n>
  background: true
  model_hint: <optional>
critical_watchlist:
  - <actions that must escalate>
success: |
  - <observable done criteria>
```

## Field notes

| Field | Who sets | Binding? |
| :--- | :--- | :--- |
| `goal` / scope | Main | Yes |
| `composition` | Main hint | No — TO may rewire / invent novel compounds |
| `tooling.allow/deny` | Main | Yes — TO enforces on leaves |
| `persist` | Main | Yes — `none` (default) or `durable` (host may alias `vault`); only TO writes |
| `caps` | Main | Yes — TO stops at cap |
| `critical_watchlist` | Main (+ TO may add) | Yes — escalate via [critical-escalation](critical-escalation.md) → host channel |

## Trivial path (no card / no TO)

- In-chat one-shot on Main, **or**
- Single leaf with a minimal goal string.

Never spawn a Topic Owner for trivial work.
