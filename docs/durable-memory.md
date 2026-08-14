# Durable memory (optional)

Not a topology. When Main sets `persist: durable` (host alias `vault`):

1. **TO is the sole agent writer.**
2. Main never writes.
3. TTs are read-only (if allowlisted).
4. Prefer retrieve → reconcile in the brief → selective upsert.
5. Human corrects the store offline when needed.

Gate: `assert_can_write("orchestrator")` (`topic_owner` alias accepted).

Telemetry: `durable_writer` — always TO when writes occur.

## Blackboard v0 (regioned JSONL)

Portable durable KB: `topology_harness.blackboard.Blackboard` (also
`retire_topic(...)`). Append-only JSONL; path is host-configurable.

### Regions

| Region | Policy |
| :--- | :--- |
| `hypotheses` | Append-only |
| `evidence` | Append-only |
| `open_questions` | Set-like upsert (dedupe by normalized text) |
| `conclusions` | TO-only single-writer; **gated** findings only — raw TT stubs rejected |
| `meta` | Lifecycle (`retired` / `abandoned`) + `composition` / `model_cast` |

### Retire-flush contract

Primary flush is **`retire_topic(role, topic, brief, *, abandoned=False)`**
(or `Blackboard(...).retire_topic(...)`). Both Cursor and Hermes hosts should
call this when a topic closes, then release sticky handles.

Brief payload shape:

```python
{
  "hypotheses": [{"text": "..."}],
  "evidence": [{"claim": "...", "source": "...", "gate": "PASS"}],
  "open_questions": ["..."],
  "conclusions": [{"text": "...", "gate": "PASS"}],  # only gated
  "composition": "...",
  "model_cast": "...",
}
```

- Normal retire: promote typed regions; write `meta.event=retired`.
- `abandoned=True`: still promote hypotheses / evidence / open_questions; **skip
  conclusions**; write `meta.event=abandoned`.
- Mid-topic (still TO-gated): `append_evidence`, `upsert_open_questions`.

Never accept raw TT stubs (`lane` + `bullets`) as conclusions — the TO must
transform stubs into gated brief conclusions first.

## Host mapping

Compound Topologies do not assume every agent has a durable store —
`persist: durable` is optional. The host maps it to a concrete backend
(files, DB, vault). Gate: `assert_can_write`. See
[host-contracts.md](host-contracts.md).

**Recommendation:** Topic work that should compound in durable memory should
open with `persist: durable` (or host alias `vault`). Throwaway Main→leaf
paths stay `persist: none`. Hosts may default TO opens to durable when omitted.
