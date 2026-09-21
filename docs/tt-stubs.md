# Worker stubs

Workers **extract**. Planner **merges** into the Host brief and authors the
**User card**. Chat **publishes the User card** to the operator (ADHD) — not
stub JSON and not the Host ledger.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

## Rules

1. Inject `WORKER_STUB_INSTRUCTION` (= `TT_STUB_INSTRUCTION`)
2. ≤5 bullets; JSON preferred; no user essays
3. **Orthogonal partition** — disjoint domain or distinct outlook; no Planner-thesis clones
4. Seed-only goals — no answer keys / filled verdicts in Worker prompts

## Shape

```json
{
  "lane": "scout_schema",
  "bullets": ["…"],
  "sources": ["…"],
  "open": ["…"],
  "confidence": "medium"
}
```

## Helpers

`parse_tt_stub` / `parse_worker_stub`, `format_tt_stub` / `format_worker_stub`,
`stubs_to_brief_findings`.

Planner then fills [to-brief-template.md](to-brief-template.md).
