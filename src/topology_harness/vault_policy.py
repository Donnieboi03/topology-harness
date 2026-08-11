"""Compatibility aliases for durable-memory policy.

Prefer ``topology_harness.durable_memory``. Host-specific durable backends
(file vaults, DBs, etc.) are configured by the agent host — not this package.
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
