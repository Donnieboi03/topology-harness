"""Tests for Task/Progress ledgers, StallPolicy, evidence.is_request_satisfied."""
from __future__ import annotations

from pathlib import Path

from agent_topo_harness.evidence import (
    CODE_GATES,
    is_request_satisfied,
    missing_gates,
)
from agent_topo_harness.ledgers import (
    ProgressLedger,
    ReasonedBool,
    StallPolicy,
    StallState,
    TaskLedger,
)
from agent_topo_harness.sticky import StickyRegistry, sticky_path_for_session


def test_task_ledger_round_trip() -> None:
    tl = TaskLedger(
        given_or_verified=["a"],
        facts_to_lookup=[{"fact": "b", "where": "docs"}],
        facts_to_derive=["c"],
        educated_guesses=[{"guess": "d", "reason": "prior"}],
        plan_bullets=[{"step": "scout", "owner_lane": "scout_a"}],
    )
    raw = tl.to_dict()
    back = TaskLedger.from_dict(raw)
    assert back.given_or_verified == ["a"]
    assert back.facts_to_lookup[0]["where"] == "docs"
    assert "verified=1" in back.summary_line()


def test_progress_ledger_round_trip() -> None:
    pl = ProgressLedger(
        is_request_satisfied=ReasonedBool(False, "gates open"),
        is_in_loop=ReasonedBool(True, "same fail"),
        is_progress_being_made=ReasonedBool(False, "no new evidence"),
        next_speaker="scout_a",
        instruction_or_question="re-check citations",
    )
    back = ProgressLedger.from_dict(pl.to_dict())
    assert back.is_in_loop.answer is True
    assert back.next_speaker == "scout_a"
    assert "loop=True" in back.summary_line()


def test_stall_policy_replan() -> None:
    policy = StallPolicy(max_stall=3, max_reset=2)
    state = StallState()
    stuck = ProgressLedger(
        is_progress_being_made=ReasonedBool(False, "noop"),
        is_in_loop=ReasonedBool(True, "loop"),
    )
    for _ in range(4):
        state = policy.note_round(state, stuck)
    assert state.stall_count == 4
    assert policy.should_replan(state)
    state = policy.mark_replan(state)
    assert state.stall_count == 0 and state.reset_count == 1
    state = policy.mark_replan(state)
    assert policy.should_escalate(state)

    moving = ProgressLedger(is_progress_being_made=ReasonedBool(True, "ok"))
    state2 = StallState(stall_count=2)
    state2 = policy.note_round(state2, moving)
    assert state2.stall_count == 1

    state3 = StallState()
    ok = ProgressLedger(is_progress_being_made=ReasonedBool(True, "ok"))
    state3 = policy.note_round(state3, ok, evidence_fail_streak=True)
    assert state3.stall_count == 1


def test_is_request_satisfied_requires_all_gates() -> None:
    full = {g: {"passed": True, "evidence": "ok"} for g in CODE_GATES}
    assert is_request_satisfied(full, required=CODE_GATES)
    assert not is_request_satisfied(
        {**full, "tests": {"passed": False}}, required=CODE_GATES
    )
    assert not is_request_satisfied({"tests": True}, required=CODE_GATES)
    assert missing_gates({"tests": True}, required=CODE_GATES)
    rows = [{"gate": g, "passed": True} for g in CODE_GATES]
    assert is_request_satisfied(rows)


def test_active_lane_and_ledger_meta_persist(tmp_path: Path) -> None:
    reg = StickyRegistry(host_session_id="s-meta")
    reg.get_or_create_to("cost-audit")
    assert reg.set_active_lane("cost-audit", "scout_schema") is not None
    assert reg.get_active_lane("cost-audit") == "scout_schema"

    tl = TaskLedger(given_or_verified=["x"], plan_bullets=[{"step": "y", "owner_lane": "z"}])
    reg.set_task_ledger("cost-audit", tl)
    pl = ProgressLedger(next_speaker="scout_schema")
    reg.set_progress_ledger("cost-audit", pl)
    reg.set_stall("cost-audit", StallState(stall_count=2, reset_count=1))

    path = sticky_path_for_session(tmp_path, "s-meta")
    reg.save(path)
    loaded = StickyRegistry.load(path)
    assert loaded.get_active_lane("cost-audit") == "scout_schema"
    assert loaded.get_task_ledger("cost-audit")["given_or_verified"] == ["x"]
    assert loaded.get_progress_ledger("cost-audit")["next_speaker"] == "scout_schema"
    assert loaded.get_stall("cost-audit")["stall_count"] == 2
