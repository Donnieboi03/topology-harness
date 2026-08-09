"""TO-only vault write policy for Compound Topologies."""
from __future__ import annotations

from typing import Any, Callable, Literal, TypeVar

Role = Literal["main", "topic_owner", "leaf"]

ALLOWED_WRITE_ROLE: Role = "topic_owner"

T = TypeVar("T")


def assert_can_write(role: str) -> None:
    """Raise PermissionError unless ``role`` is topic_owner.

    Roles: main | topic_owner | leaf — only topic_owner may write the vault.
    """
    normalized = (role or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "to": "topic_owner",
        "topicowner": "topic_owner",
        "owner": "topic_owner",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized != ALLOWED_WRITE_ROLE:
        raise PermissionError(
            f"vault write forbidden for role={role!r}; "
            f"only {ALLOWED_WRITE_ROLE!r} may write (Main/leaves never)"
        )


def vault_write_allowed(role: str) -> bool:
    try:
        assert_can_write(role)
        return True
    except PermissionError:
        return False


def guarded_vault_call(
    role: str,
    fn: Callable[..., T],
    /,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Run ``fn`` only after ``assert_can_write(role)``.

    Thin wrapper documenting the pattern: check role, then call
    ``src.vault_write`` primitives (e.g. ``dual_write_reflection``).
    """
    assert_can_write(role)
    return fn(*args, **kwargs)


def dual_write_reflection_as_topic_owner(**kwargs: Any) -> Any:
    """Policy-gated call into ``src.vault_write.dual_write_reflection``.

    Always asserts ``role=topic_owner``. Import is lazy so harness modules
    that only need the gate do not pull config/dotenv.
    """
    assert_can_write("topic_owner")
    from src.vault_write import dual_write_reflection

    return dual_write_reflection(**kwargs)
