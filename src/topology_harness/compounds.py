"""Named compound recipes for Compound Topologies.

Wiring lists match agent-topologies/references/compounds.md.
``to-brief`` is a TO merge step (not a TT atom).
"""
from __future__ import annotations

from typing import Any

COMPOUNDS: dict[str, dict[str, Any]] = {
    "debug-compound": {
        "id": "debug-compound",
        "intent": "Isolate failure dimensions, then fix under evidence.",
        "wiring": ["plane-audit", "to-brief", "refine-loop"],
        "optional": [],
        "when": "Bugs, regressions, multi-cause failures.",
    },
    "research-build": {
        "id": "research-build",
        "intent": "Breadth-first research, then implement from one brief.",
        "wiring": ["research-swarm", "to-brief", "refine-loop"],
        "optional": [],
        "when": "New feature / integration with unknown surface area.",
    },
    "decide-then-audit": {
        "id": "decide-then-audit",
        "intent": "Settle trade-offs, then risk-lens the chosen path; optionally build.",
        "wiring": ["debate", "plane-audit"],
        "optional": ["refine-loop"],
        "when": "Architecture / roadmap choices needing debate + catastrophic-dimension audits.",
    },
    "verify-then-build": {
        "id": "verify-then-build",
        "intent": "Ground claims before any producer work.",
        "wiring": ["verify-claims", "to-brief", "refine-loop"],
        "optional": [],
        "when": "Factual / legal / financial deliverables that then need an artifact.",
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


def composition_steps(compound_id: str, *, include_optional: bool = False) -> list[str]:
    """Flatten wiring (+ optional) for telemetry / planning."""
    recipe = get_compound(compound_id)
    steps = list(recipe["wiring"])
    if include_optional:
        steps.extend(recipe.get("optional") or [])
    return steps
