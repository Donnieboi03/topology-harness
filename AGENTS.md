# Agent guidance

1. **Doctrine lives here** — Planner default for action; Solo for easy Q&A; Chat / Planner / Worker; sticky; routing; stubs; gates.
2. **Policy package, not a runtime** — hosts own spawn/resume/chat/tools.
3. **No invented host paths** — no product checkouts or personal session ids in defaults.
4. **Roles (plain first):** Chat → Planner → Worker.  
   Aliases: Chat=Main · Planner=TO/orchestrator/topic_owner · Worker=TT/leaf.
5. **Host helpers:** `host_model_block` / `for_host_telegram`. Sticky still accepts `hermes_session_id` on load.
