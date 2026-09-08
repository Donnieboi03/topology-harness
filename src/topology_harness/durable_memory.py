"""Planner-only durable-memory write gate (host-agnostic).

Optional capability: when ``persist`` is enabled, only the Planner
(``planner`` / ``topic_owner`` / ``orchestrator`` / ``to``) may write the
host's durable store. Chat and Workers never write.
Host-specific backends (files, vaults, DBs) are configured by the host — not
by this harness.
"""
from __future__ import annotations

from typing import Any, Callable, Literal, TypeVar

Role = Literal["main", "orchestrator", "tt"]

ALLOWED_WRITE_ROLE = "orchestrator"

T = TypeVar("T")


def normalize_role(role: str) -> str:
    normalized = (role or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "to": "orchestrator",
        "planner": "orchestrator",
        "topic_owner": "orchestrator",
        "topicowner": "orchestrator",
        "owner": "orchestrator",
        "orchestrator": "orchestrator",
        "leaf": "tt",
        "tt": "tt",
        "worker": "tt",
        "topic_topology": "tt",
        "chat": "main",
        "main": "main",
    }
    return aliases.get(normalized, normalized)


def assert_can_write(role: str) -> None:
    """Raise PermissionError unless ``role`` is Planner (alias TO)."""
    normalized = normalize_role(role)
    if normalized != ALLOWED_WRITE_ROLE:
        raise PermissionError(
            f"durable-memory write forbidden for role={role!r}; "
            f"only Planner ({ALLOWED_WRITE_ROLE!r}; aliases to/orchestrator) "
            f"may write (Chat/Worker never)"
        )


def write_allowed(role: str) -> bool:
    try:
        assert_can_write(role)
        return True
    except PermissionError:
        return False


def guarded_write(
    role: str,
    fn: Callable[..., T],
    /,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Run ``fn`` only after ``assert_can_write(role)``."""
    assert_can_write(role)
    return fn(*args, **kwargs)
