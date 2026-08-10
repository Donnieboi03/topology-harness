"""Topology URN and composition telemetry helpers."""
from __future__ import annotations

import re
import time
import uuid
from typing import Any, Sequence

_SLUG_RE = re.compile(r"[^a-z0-9]+")

# Atom verb → paradigm segment (never use goal prose in the URN).
_ATOM_PARADIGM = {
    "research-swarm": "swarm",
    "refine-loop": "refine",
    "debate": "debate",
    "plane-audit": "planes",
    "verify-claims": "cove",
    "to-brief": "topic",
}

_ORCH_ROLES = frozenset({"orchestrator", "topic_owner", "to", "moa"})


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
) -> dict[str, Any]:
    """Telemetry ``composition`` / ``pattern_composition`` payload."""
    steps = list(atoms or [])
    return {
        "compound_id": compound_id,
        "atoms": steps,
        "novel": novel,
        "harness": "agent-topo-harness",
    }


def paradigm_for_atom(atom: str) -> str:
    """Map user-facing atom verb → short paradigm telemetry tag."""
    key = (atom or "").strip().lower()
    if key in _ATOM_PARADIGM:
        return _ATOM_PARADIGM[key]
    return _slug(atom, max_len=32)


def resolve_paradigm(
    *,
    paradigm: str | None = None,
    atom: str | None = None,
    role: str = "leaf",
    compound_id: str | None = None,
) -> str:
    """Resolve URN paradigm — never default ``leaf`` for named compounds / TOs.

    Priority: explicit paradigm → atom mapping → compound_id as novel tag →
    role (``topic``/``moa`` for TO) → ``leaf`` only for true Main→single informal TT.
    """
    if isinstance(paradigm, str) and paradigm.strip():
        return _slug(paradigm, max_len=32)
    if isinstance(atom, str) and atom.strip():
        return paradigm_for_atom(atom)
    if isinstance(compound_id, str) and compound_id.strip():
        # Named compound is not an informal leaf — tag as the compound slug
        # (composition sibling field carries the full wiring).
        return _slug(compound_id, max_len=32)
    role_n = (role or "").strip().lower()
    if role_n in _ORCH_ROLES:
        return "topic"  # TO; ``moa`` accepted as explicit paradigm override
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
) -> dict[str, Any]:
    """Sibling fields that must NOT be stuffed into the topology URN."""
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
    return out
