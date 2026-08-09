"""Critical-command escalation payloads for Main → Hermes Telegram UI."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Sequence


def build_critical_approval_payload(
    command: str,
    rationale: str,
    topic_id: str,
    *,
    topic_title: str = "",
    risk: str = "critical",
    source_role: str = "topic_owner",
    batch_id: str | None = None,
    related_commands: Sequence[str] | None = None,
    deny_action: str = "cancel",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dict suitable for Main→Telegram critical-command mediation.

    Path: Leaf → TO (filter/batch/veto) → Main → Hermes Telegram critical UI.
    On deny, ``deny_action`` defaults to ``cancel`` (abort the pending work).
    """
    cmd = (command or "").strip()
    if not cmd:
        raise ValueError("command is required")
    if not (rationale or "").strip():
        raise ValueError("rationale is required")
    if not (topic_id or "").strip():
        raise ValueError("topic_id is required")

    payload: dict[str, Any] = {
        "kind": "critical_command_approval",
        "channel": "telegram",
        "harness": "agent-topo-harness",
        "command": cmd,
        "rationale": rationale.strip(),
        "topic_id": topic_id.strip(),
        "topic_title": (topic_title or "").strip(),
        "risk": risk,
        "source_role": source_role,
        "batch_id": batch_id,
        "related_commands": list(related_commands or []),
        "deny_action": deny_action,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": dict(metadata or {}),
    }
    return payload
