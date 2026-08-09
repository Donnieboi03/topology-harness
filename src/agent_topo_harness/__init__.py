"""agent-topo-harness — Compound Topologies control-plane helpers.

Standalone harness (browser-harness-style). Hosts such as Virgil symlink or
path-depend on this checkout; Hermes glue lives under adapters/hermes/.
"""
from __future__ import annotations

from .compounds import COMPOUNDS, get_compound
from .cost import analyze_session_tree, cost_A, cost_B
from .escalate import build_critical_approval_payload
from .models import assert_allowed, hermes_model_block, load_models_config, role_model
from .scope import build_scope_card
from .telemetry import make_topology_urn
from .vault_policy import assert_can_write

__all__ = [
    "COMPOUNDS",
    "analyze_session_tree",
    "assert_allowed",
    "assert_can_write",
    "build_critical_approval_payload",
    "build_scope_card",
    "cost_A",
    "cost_B",
    "get_compound",
    "hermes_model_block",
    "load_models_config",
    "make_topology_urn",
    "role_model",
]

__version__ = "0.1.0"
