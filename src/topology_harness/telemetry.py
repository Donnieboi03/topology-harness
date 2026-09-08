"""Topology URN and composition telemetry helpers."""
from __future__ import annotations

import re
import time
import uuid
from typing import Any, Sequence

_SLUG_RE = re.compile(r"[^a-z0-9]+")

# Atoms are instances of the generic fan `fan(partition, worker, merge)`,
# individuated by merge algebra. An atom partitions by content and keeps every
# output; anything that runs the same task N times and discards some is a
# combinator. See docs/advanced.md.
#
#   swarm  union                                plane  conjunction (AND-gate)
#   cove   per-claim three-valued adjudication  shard  assembly under contract
#
# Closed set: fail-closed via `assert_atomic_paradigm` / `paradigm_for_atom`.
ATOMIC_PARADIGMS = frozenset({"swarm", "plane", "cove", "shard"})

_ATOM_PARADIGM = {
    "research-swarm": "swarm",
    "swarm": "swarm",
    "plane-audit": "plane",
    "plane": "plane",
    "planes": "plane",  # legacy URN tag
    "verify-claims": "cove",
    "cove": "cove",
    "shard": "shard",
    "build-shard": "shard",
    "parallel-build": "shard",
}

# Public menu: only `revise`. Private aliases keep fail-closed parsing of older
# composition payloads that named partition/worker mutations.
TRANSITIONS = frozenset({"revise"})

_TRANSITION_ALIASES = {
    "revise": "revise",
}

# What the public transition mutates (subject). Host introspection / errors.
TRANSITION_MUTATES = {
    "revise": "subject",
}

# Public menu: only `cycle` (wraps an atom; carries state between rounds).
COMBINATORS = frozenset({"cycle"})

_COMBINATOR_ALIASES = {
    "cycle": "cycle",
    "loop": "cycle",
}

# Private bridge: refine-loop → cycle(plane, revise) for fail-closed composition.
_LEGACY_PATTERNS: dict[str, dict[str, str]] = {
    "refine-loop": {"atom": "plane", "combinator": "cycle", "transition": "revise"},
    "refine": {"atom": "plane", "combinator": "cycle", "transition": "revise"},
}

# Names that are roles or merge steps, never paradigms in their own right.
# `to-brief` is the merge operator of whichever atom preceded it, not a step.
_NON_ATOMIC_PATTERNS = frozenset(
    {
        "refine-loop",
        "refine",
        "debate",
        "to-brief",
        "generator",
        "critiquer",
        "consul",
    }
)

_ORCH_ROLES = frozenset({"orchestrator", "topic_owner", "to", "moa"})

# Bumped when the composition payload shape changes. v2 adds combinator /
# transition; v1 runs recorded refine-loop as a bare string in `composition`.
COMPOSITION_SCHEMA_VERSION = 2


class NotAtomicError(ValueError):
    """Raised when a non-atomic pattern is used as an atomic paradigm tag."""


class NotATransitionError(ValueError):
    """Raised when an unknown transition is used in a cycle."""


class NotACombinatorError(ValueError):
    """Raised when an unknown combinator is used to wrap an atom."""


def _slug(text: str, *, max_len: int = 80) -> str:
    s = _SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return (s[:max_len].rstrip("-") if s else "") or "untitled"


def _new_ulid_like() -> str:
    """Sortable unique id without requiring the ulid package.

    Format: 13-digit ms timestamp + 10 hex chars (Crockford-ish, not a true ULID).
    """
    ms = int(time.time() * 1000)
    return f"{ms:013d}{uuid.uuid4().hex[:10]}"


def workflow_slug_for(
    topic: str,
    lane: str | None = None,
    *,
    role: str = "tt",
) -> str:
    """Build workflow slug for URNs — never goal prose.

    - Topic Orchestrator: ``{topic}--to``
    - TT / leaf under a topic: ``{topic}--{lane}``
    """
    t = _slug(topic)
    role_n = (role or "").strip().lower()
    if role_n in _ORCH_ROLES:
        return f"{t}--to"
    lane_n = _slug(lane or "default", max_len=48)
    return f"{t}--{lane_n}"


def make_topology_urn(
    paradigm: str,
    workflow_slug: str,
    ulid: str | None = None,
) -> str:
    """Build ``topology:<paradigm>:<workflow-slug>:<ulid>``."""
    para = _slug(paradigm, max_len=32)
    raw = (workflow_slug or "").strip()
    if "--" in raw:
        left, right = raw.split("--", 1)
        slug = f"{_slug(left)}--{_slug(right)}"
    else:
        slug = _slug(raw)
    uid = (ulid or "").strip() or _new_ulid_like()
    return f"topology:{para}:{slug}:{uid}"


def composition_field(
    compound_id: str | None = None,
    atoms: Sequence[str] | None = None,
    *,
    novel: bool = False,
    combinator: str | None = None,
    transition: str | None = None,
) -> dict[str, Any]:
    """Telemetry ``composition`` / ``pattern_composition`` payload.

    ``combinator`` / ``transition`` record a combinator application over the
    atom in the URN paradigm segment — e.g. a refine loop is
    ``atom=plane`` + ``combinator=cycle`` + ``transition=revise``. Both are
    validated fail-closed when set.
    """
    steps = list(atoms or [])
    comb = assert_combinator(combinator) if combinator else None
    trans = assert_transition(transition) if transition else None
    if trans and comb != "cycle":
        raise NotACombinatorError(
            f"transition {trans!r} requires combinator='cycle'; got {comb!r}. "
            "Only `cycle` carries state between rounds."
        )
    return {
        "compound_id": compound_id,
        "atoms": steps,
        "novel": novel,
        "combinator": comb,
        "transition": trans,
        "schema_version": COMPOSITION_SCHEMA_VERSION,
        "harness": "topology-harness",
    }


def is_atomic(name: str) -> bool:
    """True if ``name`` is one of the four atomics or a known alias."""
    key = (name or "").strip().lower()
    if key in ATOMIC_PARADIGMS:
        return True
    return key in _ATOM_PARADIGM


def resolve_legacy_pattern(name: str) -> dict[str, str] | None:
    """Map a legacy pattern name → ``{atom, combinator, transition}``.

    ``refine-loop`` was never a shape: it is ``cycle(plane, revise)`` where the
    Critiquer fills the evaluator atom seat and the Generator *is* the
    transition function. Returns ``None`` for names with no legacy mapping.
    """
    key = (name or "").strip().lower()
    mapped = _LEGACY_PATTERNS.get(key)
    return dict(mapped) if mapped else None


def _legacy_hint(name: str) -> str:
    """Actionable migration advice for a legacy pattern name."""
    mapped = resolve_legacy_pattern(name)
    if not mapped:
        return ""
    return (
        f" {name!r} is {mapped['combinator']}({mapped['atom']}, "
        f"{mapped['transition']}); pass atom={mapped['atom']!r}, "
        f"combinator={mapped['combinator']!r}, transition={mapped['transition']!r}."
    )


def paradigm_for_atom(atom: str) -> str:
    """Map atomic verb → URN paradigm tag. Fail-closed for non-atomics."""
    key = (atom or "").strip().lower()
    if key in _ATOM_PARADIGM:
        return _ATOM_PARADIGM[key]
    if key in _NON_ATOMIC_PATTERNS or key.startswith("refine"):
        hint = _legacy_hint(key)
        if not hint:
            hint = (
                " to-brief is the merge operator of the preceding atom, not a"
                " step; generator/critiquer are roles, not paradigms."
            )
        raise NotAtomicError(
            f"{atom!r} is not an atomic paradigm; atomics are "
            f"{sorted(ATOMIC_PARADIGMS)}.{hint}"
        )
    # Novel atom-like tags: only allow if they already resolve to a known atom
    slug = _slug(atom, max_len=32)
    if slug in ATOMIC_PARADIGMS:
        return slug
    raise NotAtomicError(
        f"{atom!r} is not an atomic paradigm; atomics are {sorted(ATOMIC_PARADIGMS)}"
    )


def assert_atomic_paradigm(paradigm: str) -> str:
    """Fail closed unless ``paradigm`` is swarm|plane|cove|shard (or alias)."""
    key = (paradigm or "").strip().lower()
    if key in _ATOM_PARADIGM:
        return _ATOM_PARADIGM[key]
    slug = _slug(paradigm, max_len=32)
    if slug in ATOMIC_PARADIGMS:
        return slug
    raise NotAtomicError(
        f"paradigm {paradigm!r} is not atomic; allowed={sorted(ATOMIC_PARADIGMS)}"
    )


def assert_transition(transition: str) -> str:
    """Fail closed unless ``transition`` is the public menu item ``revise``."""
    key = (transition or "").strip().lower()
    resolved = _TRANSITION_ALIASES.get(key)
    if resolved:
        return resolved
    raise NotATransitionError(
        f"transition {transition!r} is not known; allowed={sorted(TRANSITIONS)} "
        f"(mutating {TRANSITION_MUTATES['revise']})"
    )


def assert_combinator(combinator: str) -> str:
    """Fail closed unless ``combinator`` is in the registry (or an alias)."""
    key = (combinator or "").strip().lower()
    resolved = _COMBINATOR_ALIASES.get(key)
    if resolved:
        return resolved
    raise NotACombinatorError(
        f"combinator {combinator!r} is not known; allowed={sorted(COMBINATORS)}"
    )


def resolve_paradigm(
    *,
    paradigm: str | None = None,
    atom: str | None = None,
    role: str = "leaf",
    compound_id: str | None = None,
) -> str:
    """Resolve URN paradigm.

    Priority: explicit paradigm (must be atomic if set as atom-like) →
    atomic ``atom`` mapping → ``compound_id`` slug (composition identity) →
    role (``topic`` for TO) → ``leaf`` only for informal Main→TT.

    Non-atomic patterns (``refine-loop``, ``debate``, …) must not be passed as
    ``atom``; use ``compound_id`` / composition siblings instead.
    """
    if isinstance(paradigm, str) and paradigm.strip():
        # Explicit override: allow TO tags + leaf + atomics; reject refine etc.
        raw = paradigm.strip().lower()
        if raw in {"leaf", "topic", "moa"} or raw in _ORCH_ROLES:
            return "topic" if raw in _ORCH_ROLES or raw == "moa" else _slug(raw, max_len=32)
        if raw == "topic":
            return "topic"
        try:
            return assert_atomic_paradigm(paradigm)
        except NotAtomicError:
            # Named freeform compound tags allowed via paradigm only when they
            # are not known non-atomic pattern names. The URN paradigm segment
            # carries the *atom*; a combinator application records the atom here
            # and rides `combinator` / `transition` as siblings.
            if raw in _NON_ATOMIC_PATTERNS or raw.startswith("refine"):
                raise NotAtomicError(
                    f"paradigm {paradigm!r} is not atomic; allowed="
                    f"{sorted(ATOMIC_PARADIGMS)}.{_legacy_hint(raw)}"
                ) from None
            return _slug(paradigm, max_len=32)
    if isinstance(atom, str) and atom.strip():
        return paradigm_for_atom(atom)
    if isinstance(compound_id, str) and compound_id.strip():
        return _slug(compound_id, max_len=32)
    role_n = (role or "").strip().lower()
    if role_n in _ORCH_ROLES:
        return "topic"
    return "leaf"


def control_plane_for_role(role: str) -> str:
    """Normalize role → control_plane telemetry: ``main | orchestrator | tt``."""
    r = (role or "").strip().lower()
    if r in {"main", "chat"}:
        return "main"
    if r in _ORCH_ROLES:
        return "orchestrator"
    return "tt"


def sibling_telemetry_fields(
    *,
    composition: Any = None,
    control_plane: str | None = None,
    role: str | None = None,
    topic: str | None = None,
    lane: str | None = None,
    sticky: bool | None = None,
    durable_writer: str | None = None,
    persist: str | None = None,
    parent_run_id: str | None = None,
    combinator: str | None = None,
    transition: str | None = None,
) -> dict[str, Any]:
    """Sibling fields that must NOT be stuffed into the topology URN.

    ``combinator`` / ``transition`` ride here rather than in the URN because a
    combinator is a *modifier on an atom tag*, not a parallel tag namespace —
    every pre-existing URN stays valid.
    """
    cp = control_plane or (control_plane_for_role(role) if role else None)
    persist_n = (persist or "").strip().lower() or None
    if persist_n == "vault":
        persist_n = "durable"
    writer = durable_writer
    if writer is None and persist_n == "durable" and cp == "orchestrator":
        writer = "orchestrator"
    out: dict[str, Any] = {
        "composition": composition,
        "control_plane": cp,
        "topic": topic,
        "lane": lane,
        "sticky": sticky,
        "durable_writer": writer,
        "parent_run_id": parent_run_id,
    }
    if persist_n is not None:
        out["persist"] = persist_n
    if combinator is not None:
        out["combinator"] = assert_combinator(combinator)
    if transition is not None:
        out["transition"] = assert_transition(transition)
    return out
