# Orchestrator brief template

Copy into the Orchestrator goal / artifact store after TT findings. Generator
and other producers consume **this brief only** — not raw scout/plane dumps.

TT inputs should be [stubs](tt-stubs.md) (JSON / ≤5 bullets). Paste
`stubs_to_brief_findings(...)` under Findings, then write Decisions / Open risks
in your own voice for Main/user.

## Brief

**Topic:** …
**Goal:** …
**Composition:** … (compound id or freeform)

### Findings
(from TT stubs)

### Decisions
…

### Open risks
…

### Evidence checklist
…

## Rules

1. Orchestrator writes the brief; TTs do not publish competing briefs to Main.
2. Refine-loop Generator input = brief + prior Generator artifact; Critiquer uses
   the evidence checklist.
3. Fail evidence → revise brief or another producer round — do not lower the bar.
