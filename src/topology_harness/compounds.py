"""Named compound recipes for Compound Topologies.

Wiring lists match docs/compounds.md.

A wiring entry is either a plain atom verb (``"plane-audit"``) or a structured
node describing a combinator application::

    {"atom": "plane", "combinator": "cycle", "transition": "revise"}

``to-brief`` is **not** a wiring step: it is the merge operator of whichever
atom precedes it, so it is absorbed into that atom rather than listed. See
docs/atom-theory.md.
"""
from __future__ import annotations

from typing import Any

from .telemetry import assert_combinator, assert_transition, paradigm_for_atom

# A refine loop is `cycle(plane, revise)` — the Critiquer fills the evaluator
# atom seat, the Generator *is* the transition function.
REFINE: dict[str, str] = {
    "atom": "plane",
    "combinator": "cycle",
    "transition": "revise",
}

COMPOUNDS: dict[str, dict[str, Any]] = {
    "debug-compound": {
        "id": "debug-compound",
        "intent": "Isolate failure dimensions, then fix under evidence.",
        "wiring": ["plane-audit", REFINE],
        "optional": [],
        "when": "Bugs, regressions, multi-cause failures.",
    },
    "research-build": {
        "id": "research-build",
        "intent": "Breadth-first research, then implement from one brief.",
        "wiring": ["research-swarm", REFINE],
        "optional": [],
        "when": "New feature / integration with unknown surface area.",
    },
    "decide-then-audit": {
        "id": "decide-then-audit",
        "intent": "Settle trade-offs, then risk-lens the chosen path; optionally build.",
        "wiring": [
            {"atom": "swarm", "combinator": "cycle", "transition": "revise"},
            "plane-audit",
        ],
        "optional": [REFINE],
        "when": "Architecture / roadmap choices needing debate + catastrophic-dimension audits.",
    },
    "verify-then-build": {
        "id": "verify-then-build",
        "intent": "Ground claims before any producer work.",
        "wiring": ["verify-claims", REFINE],
        "optional": [],
        "when": "Factual / legal / financial deliverables that then need an artifact.",
    },
    "parallel-build": {
        "id": "parallel-build",
        "intent": "Build interlocking pieces in parallel under one interface contract.",
        "wiring": ["shard"],
        "optional": [REFINE],
        "when": (
            "The deliverable decomposes into pieces that must fit: multi-file "
            "code, chapters of one document, service configs sharing a port map. "
            "Requires the TO to settle the contract before the fan."
        ),
    },
}


def get_compound(compound_id: str) -> dict[str, Any]:
    """Return a compound recipe or raise KeyError."""
    try:
        return COMPOUNDS[compound_id]
    except KeyError as exc:
        known = ", ".join(sorted(COMPOUNDS))
        raise KeyError(f"Unknown compound {compound_id!r}; known: {known}") from exc


def list_compound_ids() -> list[str]:
    return sorted(COMPOUNDS)


def render_node(node: str | dict[str, Any]) -> str:
    """Render a wiring node as a stable label.

    Plain verbs pass through; structured nodes render as
    ``combinator(atom, transition)`` — e.g. ``cycle(plane, revise)``.
    """
    if isinstance(node, str):
        return node
    atom = node.get("atom") or ""
    combinator = node.get("combinator")
    transition = node.get("transition")
    if not combinator:
        return str(atom)
    inner = f"{atom}, {transition}" if transition else str(atom)
    return f"{combinator}({inner})"


def validate_node(node: str | dict[str, Any]) -> dict[str, Any]:
    """Normalize + fail-closed validate one wiring node.

    Returns ``{atom, combinator, transition}`` with the atom resolved to its
    URN paradigm tag.
    """
    if isinstance(node, str):
        return {"atom": paradigm_for_atom(node), "combinator": None, "transition": None}
    atom = paradigm_for_atom(node.get("atom") or "")
    combinator = node.get("combinator")
    transition = node.get("transition")
    return {
        "atom": atom,
        "combinator": assert_combinator(combinator) if combinator else None,
        "transition": assert_transition(transition) if transition else None,
    }


def composition_steps(compound_id: str, *, include_optional: bool = False) -> list[str]:
    """Flatten wiring (+ optional) for telemetry / planning."""
    recipe = get_compound(compound_id)
    nodes = list(recipe["wiring"])
    if include_optional:
        nodes.extend(recipe.get("optional") or [])
    return [render_node(n) for n in nodes]


def composition_nodes(
    compound_id: str, *, include_optional: bool = False
) -> list[dict[str, Any]]:
    """Validated structured nodes for a compound, in wiring order."""
    recipe = get_compound(compound_id)
    nodes = list(recipe["wiring"])
    if include_optional:
        nodes.extend(recipe.get("optional") or [])
    return [validate_node(n) for n in nodes]
