"""agent-topo-harness — Compound Topologies control-plane helpers.

Standalone, host-agnostic harness. Optional durable memory + critical channel
are contracts in docs/. Host adapters (spawn/resume, chat, tools) live in the
agent host — not in this package.
"""
from __future__ import annotations

from .compounds import COMPOUNDS, get_compound
from .cost import analyze_session_tree, cost_A, cost_B
from .decorators import TopicNotOpenError, assert_topic_open, topo_gate
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
    coerce_route_with_registry,
    parse_route_decision,
    should_fan_scouts,
    validate_route_decision,
)
from .scope import build_scope_card
from .spawn_policy import SpawnPolicyError, assert_spawn_policy
from .evidence import (
    ATOM_GATES,
    CODE_GATES,
    all_gates_passed,
    checklist,
    gates_for,
    is_request_satisfied,
    missing_gates,
)
from .ledgers import ProgressLedger, StallPolicy, StallState, TaskLedger
from .sticky import StickyRegistry, sticky_path_for_session
from .stubs import (
    LEAF_STUB_INSTRUCTION,
    TT_STUB_INSTRUCTION,
    parse_leaf_stub,
    parse_tt_stub,
    stubs_to_brief_findings,
)
from .telemetry import (
    ATOMIC_PARADIGMS,
    NotAtomicError,
    assert_atomic_paradigm,
    composition_field,
    is_atomic,
    make_topology_urn,
    paradigm_for_atom,
    resolve_paradigm,
    sibling_telemetry_fields,
    workflow_slug_for,
)

__all__ = [
    "ATOMIC_PARADIGMS",
    "ATOM_GATES",
    "CODE_GATES",
    "COMPOUNDS",
    "LEAF_STUB_INSTRUCTION",
    "NotAtomicError",
    "ProgressLedger",
    "ROUTER_SYSTEM_PROMPT",
    "RouteDecision",
    "SpawnPolicyError",
    "StallPolicy",
    "StallState",
    "TT_STUB_INSTRUCTION",
    "TaskLedger",
    "TopicNotOpenError",
    "StickyRegistry",
    "all_gates_passed",
    "analyze_session_tree",
    "assert_allowed",
    "assert_atomic_paradigm",
    "assert_can_write",
    "assert_spawn_policy",
    "assert_topic_open",
    "build_critical_approval_payload",
    "build_scope_card",
    "checklist",
    "coerce_route_with_registry",
    "composition_field",
    "cost_A",
    "cost_B",
    "for_hermes_telegram",
    "for_host_channel",
    "for_host_telegram",
    "gates_for",
    "get_compound",
    "hermes_model_block",
    "host_model_block",
    "is_atomic",
    "is_request_satisfied",
    "load_models_config",
    "make_topology_urn",
    "missing_gates",
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
    "topo_gate",
    "validate_route_decision",
    "workflow_slug_for",
    "write_allowed",
]

__version__ = "0.3.3"
