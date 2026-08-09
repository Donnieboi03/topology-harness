"""agent-topo-harness — Compound Topologies control-plane helpers.

Standalone, host-agnostic harness. Optional durable memory + critical channel
are contracts in docs/; Hermes/Virgil mappings live under adapters/hermes/.
"""
from __future__ import annotations

from .compounds import COMPOUNDS, get_compound
from .cost import analyze_session_tree, cost_A, cost_B
from .durable_memory import assert_can_write, write_allowed
from .escalate import build_critical_approval_payload, for_hermes_telegram
from .models import assert_allowed, hermes_model_block, load_models_config, role_model
from .scope import build_scope_card
from .telemetry import make_topology_urn

__all__ = [
    "COMPOUNDS",
    "analyze_session_tree",
    "assert_allowed",
    "assert_can_write",
    "build_critical_approval_payload",
    "build_scope_card",
    "cost_A",
    "cost_B",
    "for_hermes_telegram",
    "get_compound",
    "hermes_model_block",
    "load_models_config",
    "make_topology_urn",
    "role_model",
    "write_allowed",
]

__version__ = "0.2.0"
