# Topic Owner brief template

Copy into the TO goal / artifact store after atom findings. Generator and other producers consume **this brief only** — not raw scout/plane dumps.

```markdown
# Brief: <topic-slug>

## Goal
<one paragraph: what done looks like>

## Scope
- In: …
- Out: …
- Caps: rounds=<n>, wall_clock=<…>, budget_hint=<…>

## Composition
- Hint from Main: <composition: … | none>
- Actual wiring: <compound-id or novel sequence>

## Findings (merged)
### Sources / citations
- …

### Decisions
- …

### Open risks
- …

## Evidence checklist (exit criteria)
- [ ] <tests / typecheck / lint / docs or atom analog>
- [ ] …

## Tooling allowlist
- Skills/tools permitted: …
- Forbidden: …

## Persist
- persist: none | durable | vault
- Durable notes (TO writes only if persist enabled): …

## Critical watchlist
- Commands/actions that require host human approval: …
```

**Rules**

1. TO writes the brief; leaves do not publish competing briefs to Main.
2. Refine-loop Generator input = brief + prior Generator artifact; Critiquer uses the evidence checklist.
3. Fail evidence → revise brief or another producer round — do not lower the bar.
