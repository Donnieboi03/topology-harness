# TT stubs

TTs **extract**; the TO **merges** into the brief and is the voice
toward Main/user.

## Instruction

Use `TT_STUB_INSTRUCTION` (`topology_harness.stubs`) in the TT system or goal.

JSON shape:

```json
{
  "lane": "scout_schema",
  "bullets": ["…"],
  "sources": ["…"],
  "open": ["…"],
  "confidence": "medium"
}
```

Rules: ≤5 bullets; no user-facing essays; facts/citations only.
Report your lane's angle even when it diverges from the obvious/majority
reading; do not converge for agreement.

## Helpers

`TT_STUB_INSTRUCTION`, `parse_tt_stub`, `format_tt_stub`, `stubs_to_brief_findings`.

## TO brief

After stubs return, the TO writes/updates
[to-brief-template.md](to-brief-template.md) (Findings from
`stubs_to_brief_findings`) and produces the **single** user-facing answer.
Downstream producer steps consume the brief only — not raw TT dumps.
