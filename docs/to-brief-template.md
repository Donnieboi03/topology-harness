# Planner brief template

Copy after Worker stubs return. Two layers — do not mix them.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

1. **User card** — the only operator-facing text. ADHD-shaped. Chat publishes this.
2. **Host brief** — Findings / Decisions / ledgers for Chat+Planner. Chat must **not** dump this unless the operator asked for the full brief.

Paste `stubs_to_brief_findings(...)` under Findings, then write Decisions / risks
in Planner voice.

## User card (operator-facing — required)

Chat’s message to the human **is** this card (ADHD). Do not wrap it in host headings.

```
**Verdict:** one sentence — what is true or what to do.
1. …
2. …
3. …          ← cap 5
**Next:** one step doable in under two minutes (if work remains).
```

Facts must match Decisions. No Task ledger, Progress ledger, composition/atom ids, or Worker JSON.

## Host brief (internal)

**Topic:** …  
**Goal:** …  
**Composition:** … (compound id or freeform)

### Findings
(from Worker stubs — orthogonal lanes)

### Decisions
…

### Open risks
…

### Evidence checklist
…

## Task ledger (`meta.task_ledger`)

| Bucket | Contents |
| :--- | :--- |
| `given_or_verified` | Confirmed facts |
| `facts_to_lookup` | `{fact, where}` → Worker lane |
| `facts_to_derive` | Inferences still needed |
| `educated_guesses` | `{guess, reason}` — labeled |
| `plan_bullets` | `{step, owner_lane}` |

## Progress (`meta.progress_ledger`)

1. `is_request_satisfied` — true only when evidence helpers PASS
2. `is_in_loop` — same work, no new evidence
3. `is_progress_being_made`
4. `next_speaker` — lane or `planner` / `chat`
5. `instruction_or_question` — bounded ask

Stall defaults: `max_stall=3`, `max_reset=2` → replan brief; escalate to Chat after max.

## Rules

1. Planner authors; Workers don’t publish competing briefs
2. Chat publishes the **User card** only — do not dump Host brief / ledgers
3. Chat must not invent or invert Planner facts (no new thesis)
4. Seed-only Worker goals; **orthogonal partition** on swarm/plane fans
5. Fail evidence → revise; don’t lower the bar
6. Done: `retire_topic(...)` then release sticky — see [durable-memory.md](durable-memory.md)
