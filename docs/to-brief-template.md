# Topic Orchestrator (TO) brief template

Copy into the TO goal / artifact store after TT findings. Generator
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

## Task Ledger (TO-owned, persist on sticky TO `meta.task_ledger`)

Survey before / while fanning TTs. Keep buckets short.

| Bucket | Contents |
| :--- | :--- |
| `given_or_verified` | Facts already confirmed (user, prior brief, evidence PASS) |
| `facts_to_lookup` | `{fact, where}` — assign a lane / tool surface |
| `facts_to_derive` | Inferences still needed |
| `educated_guesses` | `{guess, reason}` — label clearly; do not treat as verified |
| `plan_bullets` | `{step, owner_lane}` — next actions |

## Progress Ledger (per inner round, `meta.progress_ledger`)

Each field is `{reason, answer}` except speaker/instruction strings:

1. `is_request_satisfied` — **only** true when evidence gates PASS
   (`topology_harness.is_request_satisfied(...)`). Never declare done on vibe.
2. `is_in_loop` — repeating the same TT work / same failure without new evidence.
3. `is_progress_being_made` — forward motion this round.
4. `next_speaker` — sticky lane name or `to` / `main`.
5. `instruction_or_question` — bounded ask for that speaker.

## Stall rules (`meta.stall` + `StallPolicy`)

- Defaults: `max_stall=3`, `max_reset=2`.
- Evidence FAIL streak counts as stall (no extra LLM call).
- On `should_replan()`: **revise Task Ledger / TO brief**; do **not** wipe sticky
  Gen/Critiquer (or other TT) sessions.
- After `max_reset` replans without satisfaction → escalate to Main / critical channel.

## Rules

1. TO writes the brief; TTs do not publish competing briefs to Main.
2. Refine-loop Generator input = brief + prior Generator artifact; Critiquer uses
   the evidence checklist.
3. Fail evidence → revise brief or another producer round — do not lower the bar.
4. Main→TO is **handoff** (ownership of the topic). TO→TT is **as_tool** (bounded
   turns, stub-only return). Prefer `to_only` / `lens_resume` using `active_lane`
   on follow-ups.
