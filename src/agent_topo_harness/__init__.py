"""agent-topo-harness — Compound Topologies control-plane helpers.

Standalone, host-agnostic harness. Optional durable memory + critical channel
are contracts in docs/. Host adapters (spawn/resume, chat, tools) live in the
agent host — not in this package.
"""
from __future__ import annotations

from .compounds import COMPOUNDS, get_compound
from .cost import analyze_session_tree, cost_A, cost_B
from .durable_memory import assert_can_write, write_allowed
from .escalate import (
    build_critical_approval_payload,
    for_hermes_telegram,
    for_host_channel,
    for_host_telegram,
)
from .models import (
    assert_allowed,
    hermes_model_block,
    host_model_block,
    load_models_config,
    role_model,
)
from .routing import (
    ROUTER_SYSTEM_PROMPT,
    RouteDecision,
    parse_route_decision,
    should_fan_scouts,
)
from .scope import build_scope_card
from .sticky import StickyRegistry, sticky_path_for_session
from .stubs import (
    LEAF_STUB_INSTRUCTION,
    TT_STUB_INSTRUCTION,
    parse_leaf_stub,
    parse_tt_stub,
    stubs_to_brief_findings,
)
from .telemetry import (
    composition_field,
    make_topology_urn,
    paradigm_for_atom,
    resolve_paradigm,
    sibling_telemetry_fields,
    workflow_slug_for,
)

__all__ = [
    "COMPOUNDS",
    "LEAF_STUB_INSTRUCTION",
    "ROUTER_SYSTEM_PROMPT",
    "RouteDecision",
    "TT_STUB_INSTRUCTION",
    "StickyRegistry",
    "analyze_session_tree",
    "assert_allowed",
    "assert_can_write",
    "build_critical_approval_payload",
    "build_scope_card",
    "cost_A",
    "cost_B",
    "for_hermes_telegram",
    "for_host_channel",
    "for_host_telegram",
    "get_compound",
    "hermes_model_block",
    "host_model_block",
    "load_models_config",
    "composition_field",
    "make_topology_urn",
    "paradigm_for_atom",
    "parse_leaf_stub",
    "parse_route_decision",
    "parse_tt_stub",
    "resolve_paradigm",
    "role_model",
    "should_fan_scouts",
    "sibling_telemetry_fields",
    "sticky_path_for_session",
    "stubs_to_brief_findings",
    "workflow_slug_for",
    "write_allowed",
]

__version__ = "0.3.0"
