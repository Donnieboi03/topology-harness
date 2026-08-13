"""Topic Orchestrator (TO)-only durable-memory write gate (host-agnostic).

Optional capability: when ``persist`` is enabled, only the TO
(``topic_owner`` / ``orchestrator`` role) may write the host's durable store.
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
        "topic_owner": "orchestrator",
        "topicowner": "orchestrator",
        "owner": "orchestrator",
        "orchestrator": "orchestrator",
        "leaf": "tt",
        "tt": "tt",
        "topic_topology": "tt",
    }
    return aliases.get(normalized, normalized)


def assert_can_write(role: str) -> None:
    """Raise PermissionError unless ``role`` is TO."""
    normalized = normalize_role(role)
    if normalized != ALLOWED_WRITE_ROLE:
        raise PermissionError(
            f"durable-memory write forbidden for role={role!r}; "
            f"only TO ({ALLOWED_WRITE_ROLE!r}) may write "
            f"(Main/TT never)"
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
