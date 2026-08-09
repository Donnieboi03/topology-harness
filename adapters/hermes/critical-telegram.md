# Hermes — Telegram critical-command channel

Maps core [critical-escalation](../../docs/critical-escalation.md) onto Hermes gateway Telegram UI.

```text
Leaf → TO → Main → Hermes Telegram critical-command / approval UI
```

Do **not** invent a separate Virgil approval product. Do **not** treat “type yes in CLI” as the primary story for this host.

## Main duty

Surface the portable payload with `channel: telegram` (see `build_critical_approval_payload(..., channel="telegram")` or `for_hermes_telegram(...)`).

Related: Hermes **task-approvals** skill (Draft→Approved for Notion tasks) is analogous mediation, not a substitute for critical-command on shell/actions.
