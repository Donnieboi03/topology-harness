# Critical escalation (portable)

Destructive, irreversible, or externally visible actions must not run on leaf say-so.

```text
Leaf  →  Topic Owner (filter / batch / veto)  →  Main  →  Host human-approval channel
```

The **ladder** is core doctrine. The **last mile** (Telegram, Slack, web UI, OS prompt, …) is a **host adapter**.

## What is critical (non-exhaustive)

- Destructive shell / git (`rm`, `reset --hard`, force-push), production deploys
- Sending email/posts/messages as the user; purchasing; credential changes
- Mass-delete or overwrite of durable canonical data (prefer human offline edit)
- Anything on the scope card `critical_watchlist`

## Roles

| Stage | Duty |
| :--- | :--- |
| **Leaf** | Detect; **pause**; package intent + risk; escalate to TO — do not execute |
| **Topic Owner** | Filter noise, **batch** related asks, veto unsafe/out-of-scope; escalate batch to Main |
| **Main** | Surface via the **host** approval channel; relay allow/deny |
| **Human** | Approve or deny |

## Deny / cancel

- **Deny** → cancel that action (and dependent steps); TO records outcome; do not retry quietly.
- Partial batch: execute only approved items; cancelled items stay cancelled.

## Payload shape (Main → host channel)

```text
critical_id: <ulid>
topic: <slug>
summary: <one line>
risk: <why critical>
proposed_command_or_action: <…>
requester_role: leaf|topic_owner
channel: <host-defined>   # e.g. telegram | slack | cli | web
```

Core helper: `agent_topo_harness.escalate.build_critical_approval_payload` (default `channel="host"`).

## Host mappings

| Host | Last mile |
| :--- | :--- |
| Hermes | [`adapters/hermes/critical-telegram.md`](../adapters/hermes/critical-telegram.md) |
| Other | Wire Main to your approval UI; keep the same ladder |
