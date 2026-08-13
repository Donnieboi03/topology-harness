# Agent guidance

1. **Doctrine lives here** — atoms, compounds, sticky, routing, stubs, gates.
2. **This is a policy package, not a runtime** — hosts own spawn/resume/chat/tools.
3. **Do not invent host paths** — no product checkouts, home directories, or personal session ids in docs or code defaults.
4. **Roles:** Main → TO (Topic Orchestrator) → TT. Prefer **TO** / **TT** in prose; expand TO on first mention. `topic_owner` / `leaf` are API aliases only.
5. **Host helpers:** use `host_model_block` / `for_host_telegram` (no `hermes_*` aliases for those). Sticky still accepts `hermes_session_id` on load; `resolve_child_model` still takes `hermes_role` as a legacy kwarg.
