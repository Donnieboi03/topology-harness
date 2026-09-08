"""Unit tests for spawn policy, scope, telemetry, durable memory, escalate."""
from __future__ import annotations

import pytest

from topology_harness.durable_memory import assert_can_write
from topology_harness.escalate import build_critical_approval_payload, for_host_telegram
from topology_harness.evidence import CODE_GATES, all_gates_passed, missing_gates
from topology_harness.scope import build_scope_card
from topology_harness.spawn_policy import SpawnPolicyError, assert_spawn_policy
from topology_harness.telemetry import (
    NotAtomicError,
    make_topology_urn,
    paradigm_for_atom,
    resolve_paradigm,
    sibling_telemetry_fields,
    workflow_slug_for,
)


def test_scope_card_and_urn() -> None:
    card = build_scope_card(
        topic="auth-refresh",
        goal="Fix token refresh",
        composition="debug-compound",
        persist="vault",
    )
    assert card["composition"] == "debug-compound"
    assert card["persist"] == "durable"
    card2 = build_scope_card(topic="t", goal="g", persist="none")
    assert card2["persist"] == "none"
    urn = make_topology_urn("plane", "auth-refresh--implementation", ulid="01TEST")
    assert urn == "topology:plane:auth-refresh--implementation:01TEST"


def test_workflow_slug_and_paradigm_rules() -> None:
    assert workflow_slug_for("auth-refresh", role="orchestrator") == (
        "auth-refresh--to"
    )
    assert workflow_slug_for("auth-refresh", "implementation") == (
        "auth-refresh--implementation"
    )
    assert paradigm_for_atom("plane-audit") == "plane"
    assert paradigm_for_atom("research-swarm") == "swarm"
    assert paradigm_for_atom("verify-claims") == "cove"
    assert paradigm_for_atom("shard") == "shard"
    assert paradigm_for_atom("parallel-build") == "shard"
    with pytest.raises(NotAtomicError):
        paradigm_for_atom("refine-loop")
    with pytest.raises(NotAtomicError):
        resolve_paradigm(atom="refine-loop")
    assert resolve_paradigm(compound_id="debug-compound") == "debug-compound"
    assert resolve_paradigm(role="orchestrator") == "topic"
    assert resolve_paradigm(role="leaf") == "leaf"
    sib = sibling_telemetry_fields(
        composition="debug-compound",
        role="orchestrator",
        topic="auth-refresh",
        persist="vault",
        parent_run_id="run-1",
        sticky=True,
    )
    assert sib["control_plane"] == "orchestrator"
    assert sib["durable_writer"] == "orchestrator"
    assert sib["persist"] == "durable"
    assert sib["parent_run_id"] == "run-1"
    urn = make_topology_urn(
        resolve_paradigm(atom="plane-audit"),
        workflow_slug_for("auth-refresh", "security"),
        ulid="01TEST",
    )
    assert urn == "topology:plane:auth-refresh--security:01TEST"


def test_spawn_policy_blocks_main_leaf_for_topic_work() -> None:
    with pytest.raises(SpawnPolicyError):
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            topic="harness-audit",
            paradigm="cove",
            goal="Formalize paradigms in code and create HANDOFF.md.",
            open_topics=["harness-audit"],
        )
    with pytest.raises(SpawnPolicyError):
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            topic="auth-refresh",
            goal="Implement priority codebase fixes",
            open_topics=[],
        )
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="orchestrator",
            topic="auth-refresh",
            goal="Implement priority codebase fixes",
            open_topics=[],
        )
        == "topic"
    )
    assert (
        assert_spawn_policy(
            parent_depth=1,
            role="leaf",
            topic="auth-refresh",
            lane="security",
            atom="plane-audit",
            goal="Security plane",
        )
        == "plane"
    )
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            goal="What time is it?",
            allow_informal_leaf=True,
        )
        == "leaf"
    )


def test_spawn_policy_everyday_fix_not_substantive() -> None:
    """Everyday 'fix' is not in the fan-required bag (FP closed)."""
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            goal="please fix the typo in the README",
            open_topics=[],
        )
        == "leaf"
    )


def test_spawn_policy_implement_solo_helper_without_topic() -> None:
    """Implement without a named topic is One-helper OK (Solo does not spawn)."""
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="worker",
            goal="Implement priority codebase fixes",
            open_topics=[],
        )
        == "leaf"
    )


def test_spawn_policy_planner_role_alias() -> None:
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="planner",
            topic="auth-refresh",
            goal="Implement priority codebase fixes",
            open_topics=[],
        )
        == "topic"
    )


def test_spawn_policy_compound_token_still_blocks_main_leaf() -> None:
    with pytest.raises(SpawnPolicyError):
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            goal="run a research-swarm on auth",
            open_topics=[],
        )
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            goal="run a research-swarm on auth",
            open_topics=[],
            allow_informal_leaf=True,
        )
        == "leaf"
    )


def test_durable_can_write_planner_alias() -> None:
    assert_can_write("planner")
    with pytest.raises(PermissionError):
        assert_can_write("worker")
    with pytest.raises(PermissionError):
        assert_can_write("chat")

    assert_can_write("orchestrator")
    assert_can_write("topic_owner")
    with pytest.raises(PermissionError):
        assert_can_write("main")
    with pytest.raises(PermissionError):
        assert_can_write("tt")
    with pytest.raises(PermissionError):
        assert_can_write("leaf")
    assert CODE_GATES == ("tests", "typecheck", "lint_syntax", "docs")
    assert all_gates_passed({"tests": True, "typecheck": True})
    assert missing_gates({"tests": True}) == ["typecheck", "lint_syntax", "docs"]


def test_critical_payload() -> None:
    payload = build_critical_approval_payload(
        "rm -rf /tmp/x",
        "cleanup scratch",
        "topic-1",
        topic_title="Cleanup",
    )
    assert payload["kind"] == "critical_command_approval"
    assert payload["channel"] == "host"
    assert payload["command"] == "rm -rf /tmp/x"
    assert payload["status"] == "pending"
    tg = for_host_telegram("rm -rf /tmp/x", "cleanup", "topic-1")
    assert tg["channel"] == "telegram"
