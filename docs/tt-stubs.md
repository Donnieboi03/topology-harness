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

## Helpers

`TT_STUB_INSTRUCTION`, `parse_tt_stub`, `format_tt_stub`, `stubs_to_brief_findings`.

Legacy names `LEAF_STUB_*` / `parse_leaf_stub` remain as aliases.

## TO brief

After stubs return, the TO writes/updates
[to-brief-template.md](to-brief-template.md) (Findings from
`stubs_to_brief_findings`) and produces the **single** user-facing answer.
Generator consumes the brief only — not raw TT dumps.
