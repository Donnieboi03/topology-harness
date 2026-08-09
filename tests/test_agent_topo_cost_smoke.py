"""Unit tests for agent-topo-harness cost smoke and core helpers."""
from __future__ import annotations

import pytest

from agent_topo_harness.compounds import COMPOUNDS, get_compound
from agent_topo_harness.cost import cost_A, cost_B
from agent_topo_harness.cost_smoke import FAT_C0, run_smoke
from agent_topo_harness.escalate import build_critical_approval_payload
from agent_topo_harness.evidence import CODE_GATES, all_gates_passed, missing_gates
from agent_topo_harness.scope import build_scope_card
from agent_topo_harness.telemetry import make_topology_urn
from agent_topo_harness.templates import docs_dir, load_template
from agent_topo_harness.vault_policy import assert_can_write


def test_cost_smoke_passes() -> None:
    figures = run_smoke()
    assert figures["cost_B_fat"] < figures["cost_A_fat"]
    assert figures["trivial_main"] < figures["trivial_forced_to"]


def test_fat_c0_b_cheaper_than_a() -> None:
    assert cost_B(FAT_C0, N_retries=1) < cost_A(FAT_C0, N_retries=4)


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
    urn = make_topology_urn("planes", "auth-refresh", ulid="01TEST")
    assert urn == "topology:planes:auth-refresh:01TEST"


def test_vault_policy_and_evidence() -> None:
    assert_can_write("topic_owner")
    with pytest.raises(PermissionError):
        assert_can_write("main")
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
    from agent_topo_harness.escalate import for_hermes_telegram

    tg = for_hermes_telegram("rm -rf /tmp/x", "cleanup", "topic-1")
    assert tg["channel"] == "telegram"


def test_docs_templates_live_in_harness() -> None:
    assert docs_dir().is_dir()
    text = load_template("compounds")
    assert "debug-compound" in text
