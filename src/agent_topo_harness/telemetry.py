"""Topology URN and composition telemetry helpers."""
from __future__ import annotations

import re
import time
import uuid
from typing import Any, Sequence

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(text: str) -> str:
    s = _SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return s[:80] or "untitled"


def _new_ulid_like() -> str:
    """Sortable unique id without requiring the ulid package.

    Format: 13-digit ms timestamp + 10 hex chars (Crockford-ish, not a true ULID).
    """
    ms = int(time.time() * 1000)
    return f"{ms:013d}{uuid.uuid4().hex[:10]}"


def make_topology_urn(
    paradigm: str,
    workflow_slug: str,
    ulid: str | None = None,
) -> str:
    """Build ``topology:<paradigm>:<workflow-slug>:<ulid>``."""
    para = _slug(paradigm)
    slug = _slug(workflow_slug)
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
    mapping = {
        "research-swarm": "swarm",
        "refine-loop": "refine",
        "debate": "debate",
        "plane-audit": "planes",
        "verify-claims": "cove",
        "to-brief": "topic",
    }
    return mapping.get(atom, _slug(atom))
