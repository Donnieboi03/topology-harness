# Critical escalation (Telegram UI)

Destructive, irreversible, or externally visible actions must not run on leaf say-so. Path:

```text
Leaf  →  Topic Owner (filter / batch / veto)  →  Main  →  Hermes Telegram critical-command UI
```

Do **not** invent a new Virgil approval product. Do **not** treat “type yes in CLI” as the primary story. Use the existing Hermes gateway critical-command / approval surface (same family as chat approvals — see related skill **task-approvals** and the Hermes Telegram gateway).

## What is critical (non-exhaustive)

- `rm` / destructive git (`reset --hard`, force-push), production deploys
- Sending email/posts/messages as the user; purchasing; credential changes
- Vault mass-delete or overwrite of canonical notes (prefer human brain surgery)
- Anything on the scope card `critical_watchlist`

## Roles

| Stage | Duty |
| :--- | :--- |
| **Leaf** | Detect; **pause**; package intent + risk; escalate to TO — do not execute |
| **Topic Owner** | Filter noise, **batch** related asks, veto unsafe/out-of-scope; escalate batch to Main |
| **Main** | Surface via Hermes **Telegram** critical-command UI; relay allow/deny |
| **Human** | Approve or deny in Telegram |

## Deny / cancel

- **Deny** → cancel that action (and dependent steps); TO records outcome; do not retry quietly.
- Partial batch: execute only approved items; cancelled items stay cancelled.

## Payload shape (Main → gateway)

```text
critical_id: <ulid>
topic: <slug>
summary: <one line>
risk: <why critical>
proposed_command_or_action: <…>
requester_role: leaf|topic_owner
```

Main formats this for the Telegram critical-command UI the gateway already understands.

## Related

- Skill: `task-approvals` (Draft→Approved chat/Telegram pattern for Notion tasks — analogous mediation, not a substitute for critical-command on shell/actions)
- Gateway: Hermes Telegram critical-command / approval UI
