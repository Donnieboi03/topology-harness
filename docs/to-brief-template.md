# Planner brief template

Copy after Worker stubs return. Producers consume **this brief only** — not raw stubs.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT

Paste `stubs_to_brief_findings(...)` under Findings, then write Decisions / risks
in Planner voice.

## Brief

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
2. Chat pastes losslessly
3. Seed-only Worker goals; **orthogonal partition** on swarm/plane fans
4. Fail evidence → revise; don’t lower the bar
5. Done: `retire_topic(...)` then release sticky — see [durable-memory.md](durable-memory.md)
