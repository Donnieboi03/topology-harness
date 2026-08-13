"""Atom taxonomy: four atoms, public cycle/revise, refine-loop bridge.

Covers the model in docs/atom-theory.md — closed primitives, open composition.
"""
from __future__ import annotations

import pytest

from topology_harness.compounds import render_node, validate_node
from topology_harness.evidence import SHARD_GATES, gates_for
from topology_harness.telemetry import (
    ATOMIC_PARADIGMS,
    COMBINATORS,
    COMPOSITION_SCHEMA_VERSION,
    TRANSITION_MUTATES,
    TRANSITIONS,
    NotACombinatorError,
    NotAtomicError,
    NotATransitionError,
    assert_atomic_paradigm,
    assert_combinator,
    assert_transition,
    composition_field,
    is_atomic,
    paradigm_for_atom,
    resolve_legacy_pattern,
    resolve_paradigm,
    sibling_telemetry_fields,
)


# --- atoms -----------------------------------------------------------------


def test_atom_set_is_four_and_closed() -> None:
    assert ATOMIC_PARADIGMS == {"swarm", "plane", "cove", "shard"}


@pytest.mark.parametrize(
    "verb,expected",
    [
        ("shard", "shard"),
        ("build-shard", "shard"),
        ("parallel-build", "shard"),
        ("research-swarm", "swarm"),
        ("plane-audit", "plane"),
        ("planes", "plane"),  # URN tag alias
        ("verify-claims", "cove"),
    ],
)
def test_atom_verbs_resolve(verb: str, expected: str) -> None:
    assert paradigm_for_atom(verb) == expected
    assert assert_atomic_paradigm(expected) == expected
    assert is_atomic(verb)


def test_unknown_atom_fails_closed() -> None:
    with pytest.raises(NotAtomicError):
        paradigm_for_atom("mesh")
    with pytest.raises(NotAtomicError):
        assert_atomic_paradigm("mesh")


def test_shard_resolves_through_spawn_and_urn_path() -> None:
    assert resolve_paradigm(atom="shard") == "shard"
    assert resolve_paradigm(atom="parallel-build") == "shard"


# --- transitions -----------------------------------------------------------


def test_transition_public_menu_is_revise_only() -> None:
    assert TRANSITIONS == {"revise"}
    assert TRANSITION_MUTATES == {"revise": "subject"}


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("revise", "revise"),
        ("REVISE", "revise"),
    ],
)
def test_transition_aliases(raw: str, expected: str) -> None:
    assert assert_transition(raw) == expected


def test_unknown_transition_fails_closed() -> None:
    with pytest.raises(NotATransitionError):
        assert_transition("mutate-everything")
    with pytest.raises(NotATransitionError):
        assert_transition("re-scope")
    with pytest.raises(NotATransitionError):
        assert_transition("swap")
    with pytest.raises(NotATransitionError):
        assert_transition("")


# --- combinators -----------------------------------------------------------


def test_combinator_public_menu_is_cycle_only() -> None:
    assert COMBINATORS == {"cycle"}
    assert assert_combinator("cycle") == "cycle"
    assert assert_combinator("loop") == "cycle"


def test_unknown_combinator_fails_closed() -> None:
    with pytest.raises(NotACombinatorError):
        assert_combinator("gossip")
    with pytest.raises(NotACombinatorError):
        assert_combinator("poll")
    with pytest.raises(NotACombinatorError):
        assert_combinator("best_of")


# --- refine-loop bridge ----------------------------------------------------


def test_refine_loop_bridges_to_cycle_plane_revise() -> None:
    assert resolve_legacy_pattern("refine-loop") == {
        "atom": "plane",
        "combinator": "cycle",
        "transition": "revise",
    }
    assert resolve_legacy_pattern("refine") == resolve_legacy_pattern("refine-loop")
    assert resolve_legacy_pattern("deepen") is None
    assert resolve_legacy_pattern("not-a-pattern") is None


def test_refine_loop_error_carries_migration_advice() -> None:
    with pytest.raises(NotAtomicError) as exc:
        paradigm_for_atom("refine-loop")
    msg = str(exc.value)
    assert "cycle(plane, revise)" in msg
    assert "transition='revise'" in msg
    assert "composition" not in msg


def test_to_brief_error_says_it_is_a_merge_operator() -> None:
    with pytest.raises(NotAtomicError) as exc:
        paradigm_for_atom("to-brief")
    assert "merge operator" in str(exc.value)


# --- telemetry payloads ----------------------------------------------------


def test_composition_field_round_trips_combinator_and_transition() -> None:
    payload = composition_field(
        "debug-compound",
        ["plane"],
        combinator="cycle",
        transition="revise",
    )
    assert payload["combinator"] == "cycle"
    assert payload["transition"] == "revise"
    assert payload["schema_version"] == COMPOSITION_SCHEMA_VERSION


def test_composition_field_defaults_stay_v1_shaped() -> None:
    payload = composition_field("debug-compound", ["plane"])
    assert payload["combinator"] is None
    assert payload["transition"] is None
    assert payload["compound_id"] == "debug-compound"


def test_composition_field_validates_fail_closed() -> None:
    with pytest.raises(NotACombinatorError):
        composition_field("x", combinator="gossip")
    with pytest.raises(NotATransitionError):
        composition_field("x", combinator="cycle", transition="teleport")


def test_sibling_fields_carry_combinator_not_urn() -> None:
    sib = sibling_telemetry_fields(
        composition="debug-compound",
        role="orchestrator",
        topic="auth-refresh",
        combinator="cycle",
        transition="revise",
    )
    assert sib["combinator"] == "cycle"
    assert sib["transition"] == "revise"
    # omitted entirely when unset, so v1 consumers see no new keys
    plain = sibling_telemetry_fields(role="tt", topic="auth-refresh")
    assert "combinator" not in plain
    assert "transition" not in plain


# --- gates -----------------------------------------------------------------


def test_shard_gates_are_domain_neutral() -> None:
    assert SHARD_GATES == (
        "interfaces_agree",
        "no_overlapping_writes",
        "assembles_clean",
    )
    assert gates_for("shard") == SHARD_GATES
    assert gates_for("parallel-build") == SHARD_GATES


# --- wiring nodes ----------------------------------------------------------


def test_render_and_validate_wiring_nodes() -> None:
    assert render_node("plane-audit") == "plane-audit"
    assert render_node(
        {"atom": "plane", "combinator": "cycle", "transition": "revise"}
    ) == "cycle(plane, revise)"
    assert validate_node("plane-audit") == {
        "atom": "plane",
        "combinator": None,
        "transition": None,
    }
    with pytest.raises(NotATransitionError):
        validate_node({"atom": "plane", "combinator": "cycle", "transition": "nope"})
