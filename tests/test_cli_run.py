"""CLI smoke for topology-harness entrypoint."""
from __future__ import annotations

from topology_harness.run import DOCTRINE, run_doctor, _helpers_ns


def test_doctor_ok() -> None:
    assert run_doctor() == 0


def test_doctrine_mentions_atomics() -> None:
    assert "swarm" in DOCTRINE
    assert "assert_spawn_policy" in DOCTRINE
    assert "Solo" in DOCTRINE
    assert "Planner" in DOCTRINE
    assert "Cursor" in DOCTRINE


def test_cursor_map_mentions_task() -> None:
    from topology_harness.run import CURSOR_MAP

    assert "Task" in CURSOR_MAP
    assert "Chat" in CURSOR_MAP or "Main" in CURSOR_MAP
    assert "Planner" in CURSOR_MAP or "TO" in CURSOR_MAP
    assert "Solo" in CURSOR_MAP


def test_doctrine_chat_publishes_user_card_not_host_ledger() -> None:
    from topology_harness.run import CURSOR_MAP

    assert "User card" in DOCTRINE
    assert "Host ledger" in DOCTRINE
    assert "verbatim" not in DOCTRINE.lower()
    assert "User card" in CURSOR_MAP
    assert "verbatim" not in CURSOR_MAP.lower()
    assert "ADHD-rewrite" not in CURSOR_MAP


def test_helpers_ns_has_core() -> None:
    ns = _helpers_ns()
    assert "ATOMIC_PARADIGMS" in ns
    assert "assert_spawn_policy" in ns
    assert "TT_STUB_INSTRUCTION" in ns
