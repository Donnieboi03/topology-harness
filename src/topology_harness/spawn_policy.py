"""Fail-closed spawn / delegate topology policy.

Hosts call :func:`assert_spawn_policy` before minting a child. This closes the
escape hatch where Main spawns an informal ``leaf`` for substantive topic work
(implement / formalize / compound) and still claims an atomic paradigm.
"""
from __future__ import annotations

import re
from typing import Any, Sequence

from .telemetry import (
    ATOMIC_PARADIGMS,
    NotAtomicError,
    resolve_paradigm,
)

_ORCH = frozenset({"orchestrator", "topic_owner", "to", "moa"})
_LEAF = frozenset({"leaf", "tt", ""})

# Goals that must not run as Main → informal leaf.
_SUBSTANTIVE_RE = re.compile(
    r"\b("
    r"implement|formalize|refactor|rewrite|fix|patch|commit|"
    r"audit|compound|topology|orchestrat|swarm|plane|cove|"
    r"generator|critiqu|refine-loop|research-swarm|plane-audit|"
    r"verify-claims|handoff|registry|sticky"
    r")\b",
    re.I,
)


class SpawnPolicyError(PermissionError):
    """Delegate spawn violates Compound Topologies control-plane policy."""


def _norm_role(role: str | None) -> str:
    r = (role or "leaf").strip().lower()
    if r in _ORCH:
        return "orchestrator"
    if r in {"leaf", "tt"}:
        return "leaf"
    return r or "leaf"


def _topic_open(topic: str | None, open_topics: Sequence[str] | None) -> bool:
    if not topic or not open_topics:
        return False
    t = topic.strip().lower()
    return t in {str(x).strip().lower() for x in open_topics if str(x).strip()}


def assert_spawn_policy(
    *,
    parent_depth: int,
    role: str | None,
    topic: str | None = None,
    lane: str | None = None,
    paradigm: str | None = None,
    atom: str | None = None,
    composition: Any = None,
    compound_id: str | None = None,
    goal: str = "",
    open_topics: Sequence[str] | None = None,
    allow_informal_leaf: bool = False,
) -> str:
    """Validate a proposed spawn; return the resolved URN paradigm.

    Rules (account for Main→leaf “formalize” failure):

    1. Main (``parent_depth == 0``) must not spawn ``leaf`` when the topic is
       already sticky-open — resume the TO (``to_only``) instead.
    2. Main must not spawn ``leaf`` for substantive goals, or when
       ``atom`` / ``composition`` / ``compound_id`` / atomic ``paradigm`` is
       set — open/resume a Topic Orchestrator first.
    3. Informal Main→leaf is allowed only when ``allow_informal_leaf=True``
       **or** the ask is trivial (no topic, no atom/composition, goal does not
       match substantive patterns).
    4. Resolved paradigm must honor ``atom`` / atomic ``paradigm``; never mint
       ``leaf`` when an atomic was requested.
    5. Under a TO (``parent_depth >= 1``), ``leaf``/TT is expected; atomics OK.

    Returns the paradigm string that must be used in the Topology URN.
    """
    depth = int(parent_depth)
    role_n = _norm_role(role)
    topic_n = (topic or "").strip() or None
    goal_s = goal or ""
    has_composition = bool(
        composition
        or (isinstance(compound_id, str) and compound_id.strip())
    )
    has_atom = bool(isinstance(atom, str) and atom.strip())
    atomic_paradigm = False
    if isinstance(paradigm, str) and paradigm.strip():
        raw = paradigm.strip().lower()
        if raw in ATOMIC_PARADIGMS or raw in {
            "research-swarm",
            "plane-audit",
            "planes",
            "verify-claims",
        }:
            atomic_paradigm = True

    substantive = bool(_SUBSTANTIVE_RE.search(goal_s)) or has_atom or has_composition or atomic_paradigm

    if depth <= 0 and role_n == "leaf":
        if _topic_open(topic_n, open_topics):
            raise SpawnPolicyError(
                f"topic {topic_n!r} is already sticky-open — do not spawn a "
                f"Main→leaf worker. Emit to_only / resume the Topic Orchestrator "
                f"(role=orchestrator) and let the TO spawn TTs."
            )
        if not allow_informal_leaf and (topic_n or substantive):
            raise SpawnPolicyError(
                "Main→leaf blocked for topic/substantive/atomic work. "
                "Spawn role=orchestrator (Topic Orchestrator) first, or set "
                "allow_informal_leaf only for true throwaway Q&A. "
                f"(topic={topic_n!r}, atom={atom!r}, composition={bool(has_composition)})"
            )

    # Resolve paradigm — fail closed for non-atomic atom= tags
    try:
        resolved = resolve_paradigm(
            paradigm=paradigm,
            atom=atom,
            role=role_n,
            compound_id=compound_id
            or (
                composition.get("compound_id")
                if isinstance(composition, dict)
                else (composition if isinstance(composition, str) else None)
            ),
        )
    except NotAtomicError as exc:
        raise SpawnPolicyError(str(exc)) from exc

    if (has_atom or atomic_paradigm) and resolved == "leaf":
        raise SpawnPolicyError(
            f"refusing to mint topology:leaf when atom/paradigm requested "
            f"(atom={atom!r}, paradigm={paradigm!r})"
        )

    if role_n == "orchestrator" and resolved == "leaf":
        resolved = "topic"

    del lane  # reserved for host logging; slug built separately
    return resolved
