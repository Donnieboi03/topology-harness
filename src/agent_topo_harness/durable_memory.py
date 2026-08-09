"""TO-only durable-memory write gate (host-agnostic).

Optional capability: when ``persist`` is enabled, only ``topic_owner`` may
write the host's durable store. Vault/Obsidian is a Hermes/Virgil mapping —
see the host's ``docs/compound-topologies/vault-obsidian.md`` (Virgil).
"""
from __future__ import annotations

from typing import Any, Callable, Literal, TypeVar

Role = Literal["main", "topic_owner", "leaf"]

ALLOWED_WRITE_ROLE: Role = "topic_owner"

T = TypeVar("T")


def normalize_role(role: str) -> str:
    normalized = (role or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "to": "topic_owner",
        "topicowner": "topic_owner",
        "owner": "topic_owner",
    }
    return aliases.get(normalized, normalized)


def assert_can_write(role: str) -> None:
    """Raise PermissionError unless ``role`` is topic_owner."""
    normalized = normalize_role(role)
    if normalized != ALLOWED_WRITE_ROLE:
        raise PermissionError(
            f"durable-memory write forbidden for role={role!r}; "
            f"only {ALLOWED_WRITE_ROLE!r} may write (Main/leaves never)"
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


# Back-compat names
vault_write_allowed = write_allowed
guarded_vault_call = guarded_write
