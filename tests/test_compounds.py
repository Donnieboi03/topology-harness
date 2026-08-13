"""Unit tests for named compounds registry."""
from __future__ import annotations

from topology_harness.compounds import (
    COMPOUNDS,
    REFINE,
    composition_nodes,
    composition_steps,
    get_compound,
)


def test_compounds_registry() -> None:
    assert set(COMPOUNDS) == {
        "debug-compound",
        "research-build",
        "decide-then-audit",
        "verify-then-build",
        "parallel-build",
    }
    assert get_compound("research-build")["wiring"] == ["research-swarm", REFINE]
    assert composition_steps("research-build") == [
        "research-swarm",
        "cycle(plane, revise)",
    ]
    assert REFINE in get_compound("decide-then-audit")["optional"]


def test_parallel_build_compound_uses_shard() -> None:
    nodes = composition_nodes("parallel-build")
    assert nodes[0] == {"atom": "shard", "combinator": None, "transition": None}
    assert composition_nodes("parallel-build", include_optional=True)[-1] == {
        "atom": "plane",
        "combinator": "cycle",
        "transition": "revise",
    }
