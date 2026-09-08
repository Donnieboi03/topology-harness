"""Fail-closed spawn / delegate topology policy.

Hosts call :func:`assert_spawn_policy` before minting a child.

Solo work happens in Chat **without spawning** — this gate only runs when a
host actually mints a child. Chat may spawn **One helper** (single Worker)
for a throwaway dig. Multi-lens / atom / compound fans require a **Planner**
first (aliases: TO / orchestrator / topic_owner).
"""
from __future__ import annotations

import re
from typing import Any, Sequence

from .telemetry import (
    ATOMIC_PARADIGMS,
    NotAtomicError,
    resolve_paradigm,
)

# Planner aliases (TO / orchestrator / topic_owner / …)
_ORCH = frozenset(
    {
        "orchestrator",
        "topic_owner",
        "to",
        "moa",
        "planner",
    }
)
# Worker aliases (TT / leaf / …)
_LEAF = frozenset({"leaf", "tt", "worker", ""})

# Goals that force Chat → Planner (not One helper) when spawning a Worker.
# Compound/atom/topology tokens only — NOT everyday implement/fix/refactor
# (Solo handles those in-chat without spawning).
_FAN_REQUIRED_RE = re.compile(
    r"\b("
    r"audit|compound|topology|orchestrat|swarm|plane|cove|shard|"
    r"generator|critiqu|refine-loop|research-swarm|plane-audit|"
    r"parallel-build|build-shard|"
    r"cycle|revise|re-scope|rescope|swap|"
    r"verify-claims|handoff|registry|sticky|"
    r"multi[- ]?lens|orthogonal|full[_-]?refan"
    r")\b",
    re.I,
)

# Back-compat name used in older docs/tests
_SUBSTANTIVE_RE = _FAN_REQUIRED_RE


class SpawnPolicyError(PermissionError):
    """Delegate spawn violates Compound Topologies control-plane policy."""


def _norm_role(role: str | None) -> str:
    r = (role or "leaf").strip().lower().replace("-", "_")
    if r in {"chat", "main"}:
        # Depth-0 parent identity — not a child role; treat as leaf denial path
        # only when misused as child role (hosts should pass planner/worker).
        return "leaf"
    if r in _ORCH:
        return "orchestrator"
    if r in _LEAF or r in {"leaf", "tt", "worker"}:
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

    Rules:

    1. Sticky-open topic → Chat must not spawn a Worker; resume the Planner
       (``to_only`` / ``resume``).
    2. Atom / composition / compound / fan-required goal tokens → Chat must
       spawn a Planner first (not a Worker pile).
    3. **One helper:** Chat→single Worker is allowed when
       ``allow_informal_leaf=True``, **or** there is no sticky topic, no
       atom/composition, and the goal is not a fan-required pattern.
    4. Named topic without sticky still requires Planner before Workers
       (topic work is Planner-owned once named).
    5. Under a Planner (``parent_depth >= 1``), Workers + orthogonal atoms OK.

    Role aliases: ``planner``→orchestrator, ``worker``→leaf
    (also ``to``/``tt``/``topic_owner``).
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
            "build-shard",
            "parallel-build",
        }:
            atomic_paradigm = True

    fan_required = (
        bool(_FAN_REQUIRED_RE.search(goal_s))
        or has_atom
        or has_composition
        or atomic_paradigm
    )
    # Named topic (even if not yet sticky) → Workers go under Planner
    needs_planner = bool(topic_n) or fan_required

    if depth <= 0 and role_n == "leaf":
        if _topic_open(topic_n, open_topics):
            raise SpawnPolicyError(
                f"topic {topic_n!r} is already sticky-open — do not spawn a "
                f"Chat→Worker. Emit resume/to_only and resume the Planner "
                f"(role=planner|to|orchestrator); let the Planner spawn Workers "
                f"(aliases: TO/TT)."
            )
        if not allow_informal_leaf and needs_planner:
            raise SpawnPolicyError(
                "Chat→Worker blocked for named-topic / fan / atomic work. "
                "Spawn role=planner (Planner; alias TO) first, or set "
                "allow_informal_leaf for One-helper throwaway digs. "
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
