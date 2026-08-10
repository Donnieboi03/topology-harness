# Critical escalation

Destructive, irreversible, or externally visible actions must not run on TT
say-so.

## Ladder

```
TT → Orchestrator (filter / batch / veto) → Main → host human channel
```

On deny: cancel (default). Helpers: `build_critical_approval_payload`.

## Payload sketch

```yaml
kind: critical_command_approval
command: …
rationale: …
topic_id: …
requester_role: tt|orchestrator
channel: host
deny_action: cancel
```

## Host mapping

The host maps `channel` to Telegram, Slack, CLI confirm, etc. This package stays
host-agnostic.
