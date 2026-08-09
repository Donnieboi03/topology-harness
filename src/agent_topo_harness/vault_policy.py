"""Compatibility aliases for durable-memory policy.

Prefer ``agent_topo_harness.durable_memory``. Vault/Obsidian specifics live in
``adapters/hermes/vault-obsidian.md``.
"""
from __future__ import annotations

from typing import Any

from .durable_memory import (  # noqa: F401
    ALLOWED_WRITE_ROLE,
    assert_can_write,
    guarded_vault_call,
    guarded_write,
    normalize_role,
    vault_write_allowed,
    write_allowed,
)


def dual_write_reflection_as_topic_owner(**kwargs: Any) -> Any:
    """Virgil-only bridge: policy-gated ``src.vault_write.dual_write_reflection``.

    Lazy import so core harness does not require Virgil on the path.
    """
    assert_can_write("topic_owner")
    from src.vault_write import dual_write_reflection  # type: ignore

    return dual_write_reflection(**kwargs)
