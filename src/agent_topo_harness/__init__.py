"""Deprecated alias for ``topology_harness``. Prefer ``import topology_harness``.

This shim re-exports the public API and submodules for one release so hosts
(Virgil/Hermes) can migrate imports without a hard break.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "agent_topo_harness is deprecated; use topology_harness",
    DeprecationWarning,
    stacklevel=2,
)

from topology_harness import *  # noqa: F403
from topology_harness import __all__, __version__  # noqa: F401

# Re-export submodule names for ``from agent_topo_harness import sticky`` style.
