"""Compatibility aliases for durable-memory policy.

Prefer ``agent_topo_harness.durable_memory``. Vault/Obsidian specifics live in
``adapters/hermes/vault-obsidian.md``. Virgil ``dual_write`` bridge:
``adapters/hermes/virgil_bridge.py``.
"""
from __future__ import annotations

from .durable_memory import (  # noqa: F401
    ALLOWED_WRITE_ROLE,
    assert_can_write,
    guarded_vault_call,
    guarded_write,
    normalize_role,
    vault_write_allowed,
    write_allowed,
)
