"""Unit tests for topology-harness cost smoke and core helpers."""
from __future__ import annotations

import pytest

from topology_harness.compounds import COMPOUNDS, get_compound
from topology_harness.cost import cost_A, cost_B
from topology_harness.cost_smoke import FAT_C0, run_smoke
from topology_harness.escalate import build_critical_approval_payload
from topology_harness.evidence import CODE_GATES, all_gates_passed, missing_gates
from topology_harness.scope import build_scope_card
from topology_harness.telemetry import (
    make_topology_urn,
    paradigm_for_atom,
    resolve_paradigm,
    sibling_telemetry_fields,
    workflow_slug_for,
)
from topology_harness.templates import docs_dir, load_template
from topology_harness.vault_policy import assert_can_write


def test_cost_smoke_passes() -> None:
    figures = run_smoke()
    assert figures["trivial_main"] < figures["trivial_forced_to"]
    assert figures["cost_A_one_turn_one_retry"] > 0
    assert figures["cost_B_one_turn_one_retry"] > 0


def test_fair_one_turn_one_retry_defaults() -> None:
    """Same turn/retry knobs; one-shot often has A ≤ B (graph overhead)."""
    a = cost_A(FAT_C0, T_A=1, N_retries=1)
    b = cost_B(FAT_C0, T_A=1, N_retries=1)
    assert a > 0 and b > 0



def test_compounds_registry() -> None:
    assert set(COMPOUNDS) == {
        "debug-compound",
        "research-build",
        "decide-then-audit",
        "verify-then-build",
    }
    assert get_compound("research-build")["wiring"] == [
        "research-swarm",
        "to-brief",
        "refine-loop",
    ]
    assert "refine-loop" in get_compound("decide-then-audit")["optional"]


def test_scope_card_and_urn() -> None:
    card = build_scope_card(
        topic="auth-refresh",
        goal="Fix token refresh",
        composition="debug-compound",
        persist="vault",
    )
    assert card["composition"] == "debug-compound"
    assert card["persist"] == "durable"  # vault alias
    card2 = build_scope_card(topic="t", goal="g", persist="none")
    assert card2["persist"] == "none"
    urn = make_topology_urn("plane", "auth-refresh--implementation", ulid="01TEST")
    assert urn == "topology:plane:auth-refresh--implementation:01TEST"


def test_workflow_slug_and_paradigm_rules() -> None:
    from topology_harness.telemetry import NotAtomicError

    assert workflow_slug_for("auth-refresh", role="orchestrator") == (
        "auth-refresh--to"
    )
    assert workflow_slug_for("auth-refresh", "implementation") == (
        "auth-refresh--implementation"
    )
    assert paradigm_for_atom("plane-audit") == "plane"
    assert paradigm_for_atom("research-swarm") == "swarm"
    assert paradigm_for_atom("verify-claims") == "cove"
    # refine-loop is compound wiring, not an atomic paradigm
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
    from topology_harness.spawn_policy import SpawnPolicyError, assert_spawn_policy

    with pytest.raises(SpawnPolicyError):
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            topic="agent-topo-audit",
            paradigm="cove",
            goal="Formalize Trinity paradigms in code and create HANDOFF.md.",
            open_topics=["agent-topo-audit"],
        )
    with pytest.raises(SpawnPolicyError):
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            topic="auth-refresh",
            goal="Implement priority codebase fixes",
            open_topics=[],
        )
    # TO path OK
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
    # TT under TO with atomic OK
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
    # Trivial informal leaf OK
    assert (
        assert_spawn_policy(
            parent_depth=0,
            role="leaf",
            goal="What time is it?",
            allow_informal_leaf=True,
        )
        == "leaf"
    )


def test_vault_policy_and_evidence() -> None:
    assert_can_write("orchestrator")
    assert_can_write("topic_owner")  # alias
    with pytest.raises(PermissionError):
        assert_can_write("main")
    with pytest.raises(PermissionError):
        assert_can_write("tt")
    with pytest.raises(PermissionError):
        assert_can_write("leaf")  # alias → tt
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
    from topology_harness.escalate import for_host_telegram, for_hermes_telegram

    tg = for_host_telegram("rm -rf /tmp/x", "cleanup", "topic-1")
    assert tg["channel"] == "telegram"
    assert for_hermes_telegram("rm -rf /tmp/x", "cleanup", "topic-1")["channel"] == (
        "telegram"
    )


def test_docs_templates_live_in_harness() -> None:
    assert docs_dir().is_dir()
    text = load_template("compounds")
    assert "debug-compound" in text
