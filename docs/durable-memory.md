# Durable memory

Optional. When Chat sets `persist: durable` (host alias `vault`):

1. **Planner is the sole agent writer** (`assert_can_write("planner")`)
2. Chat never writes
3. Workers read-only if allowlisted
4. Retrieve → reconcile in brief → selective upsert

> **Aliases:** Chat = Main · Planner = TO / orchestrator / topic_owner · Worker = TT

## Blackboard (regioned JSONL)

`Blackboard` / `retire_topic(...)`. Path is host-configurable.

| Region | Policy |
| :--- | :--- |
| `hypotheses` / `evidence` | Append-only |
| `open_questions` | Upsert by normalized text |
| `conclusions` | Planner-only; **gated** only — raw Worker stubs rejected |
| `meta` | `retired` / `abandoned` + composition |

```python
{
  "hypotheses": [{"text": "..."}],
  "evidence": [{"claim": "...", "source": "...", "gate": "PASS"}],
  "open_questions": ["..."],
  "conclusions": [{"text": "...", "gate": "PASS"}],
  "composition": "...",
}
```

- Normal retire: promote regions; `meta.event=retired`
- `abandoned=True`: skip conclusions
- Never dump Worker stubs into conclusions

See [host-contracts.md](host-contracts.md).
