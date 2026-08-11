"""CLI smoke for topology-harness entrypoint."""
from __future__ import annotations

from topology_harness.run import DOCTRINE, run_doctor, _helpers_ns


def test_doctor_ok() -> None:
    assert run_doctor() == 0


def test_doctrine_mentions_atomics() -> None:
    assert "swarm" in DOCTRINE
    assert "assert_spawn_policy" in DOCTRINE
    assert "Cursor host" in DOCTRINE


def test_cursor_map_mentions_task() -> None:
    from topology_harness.run import CURSOR_MAP

    assert "Task" in CURSOR_MAP
    assert "Main" in CURSOR_MAP
    assert "TO" in CURSOR_MAP


def test_helpers_ns_has_core() -> None:
    ns = _helpers_ns()
    assert "ATOMIC_PARADIGMS" in ns
    assert "assert_spawn_policy" in ns
    assert "TT_STUB_INSTRUCTION" in ns
