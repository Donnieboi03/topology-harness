# Cursor adapter

**Solo by default.** This chat is Chat; Task sub-agents are Planner / Worker.

> **Aliases:** Chat = Main · Planner = TO · Worker = TT  
> Rule source of truth: [cursor-rule.mdc](cursor-rule.mdc)

## Role map

| Role | Cursor |
| :--- | :--- |
| **Chat** | This agent — Solo; pastes Planner briefs verbatim |
| **Planner** | `Task` `generalPurpose` — one topic; merges stubs; authors brief |
| **Worker** | `Task` `explore` / `generalPurpose` / `shell` — stubs only |

## Output style (ADHD)

Attribution: [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd).

1. Verdict / next action first; ≤5 bullets.
2. Number multi-step; one <2-min next step when work remains.
3. Errors: location, cause, fix. No closers.
4. Paste Planner briefs **verbatim** — do not rewrite.

## Modes

- **Solo** (default) — no Task fan
- **One helper** — one Worker dig; no Planner
- **Planner+workers** — only when fan criteria match

**Fan criteria:** multi-file/multi-surface implement; unknown-surface research;
user asks for multiple angles.

Route **internally** — never show `Route:` / route dumps to the user.

## Sticky

File: `.cursor/topology-sticky/registry.json`  
Resume the open Planner — do not cold re-fan. After load: `purge_idle()`.  
Done: `retire_topic` then `release_topic`. See [host-contracts.md](../host-contracts.md).

## Worker rules (when Planner fans)

- Inject `WORKER_STUB_INSTRUCTION` / `TT_STUB_INSTRUCTION`
- **Orthogonal partition** — disjoint domains / outlooks
- Seed-only goals (no answer keys)
- Planner merges → Chat pastes

## Spawn policy (intent)

Chat→Worker blocked for sticky-open / named topic / atom-compound fans.
One helper OK without topic when no fan tokens.

## Durable memory

Planner-only writes (`assert_can_write("planner")`).

## CLI

```bash
topology-harness cursor-map
topology-harness doctrine
topology-harness --doctor
```

Atoms/compounds: [advanced.md](../advanced.md).
