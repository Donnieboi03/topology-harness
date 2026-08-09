"""Virgil-only bridges (not part of the portable Python package).

Import from a Virgil checkout that has ``src.vault_write`` on PYTHONPATH::

    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path("~/Developer/agent-topo-harness/adapters/hermes").expanduser()))
    from virgil_bridge import dual_write_reflection_as_topic_owner

Or copy this helper into Virgil. Core ``agent_topo_harness.vault_policy`` no
longer owns this import.
"""
from __future__ import annotations

from typing import Any


def dual_write_reflection_as_topic_owner(**kwargs: Any) -> Any:
    """Policy-gated call into Virgil ``src.vault_write.dual_write_reflection``."""
    from agent_topo_harness.durable_memory import assert_can_write

    assert_can_write("topic_owner")
    from src.vault_write import dual_write_reflection  # type: ignore

    return dual_write_reflection(**kwargs)
