"""Critical-command escalation payloads (host-agnostic ladder).

Last-mile channel (telegram, slack, …) is set by the host adapter.
"""
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
    source_role: str = "orchestrator",
    batch_id: str | None = None,
    related_commands: Sequence[str] | None = None,
    deny_action: str = "cancel",
    channel: str = "host",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dict for Main → host human-approval channel.

    Path: TT → Orchestrator (filter/batch/veto) → Main → host channel.
    On deny, ``deny_action`` defaults to ``cancel``.
    """
    cmd = (command or "").strip()
    if not cmd:
        raise ValueError("command is required")
    if not (rationale or "").strip():
        raise ValueError("rationale is required")
    if not (topic_id or "").strip():
        raise ValueError("topic_id is required")

    return {
        "kind": "critical_command_approval",
        "channel": (channel or "host").strip().lower() or "host",
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


def for_host_channel(
    command: str,
    rationale: str,
    topic_id: str,
    *,
    channel: str = "telegram",
    **kwargs: Any,
) -> dict[str, Any]:
    """Build an approval payload for a specific host human channel."""
    kwargs.pop("channel", None)
    return build_critical_approval_payload(
        command,
        rationale,
        topic_id,
        channel=channel,
        **kwargs,
    )


def for_host_telegram(
    command: str,
    rationale: str,
    topic_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Convenience: ``for_host_channel(..., channel="telegram")``."""
    return for_host_channel(
        command, rationale, topic_id, channel="telegram", **kwargs
    )


# Alias kept for existing host call sites
for_hermes_telegram = for_host_telegram
