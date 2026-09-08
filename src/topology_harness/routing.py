"""Intent routing for Chat: Solo by default; open a Planner only for complex fans.

No length / keyword heuristics. Hosts ask Chat (or a tiny router call) to emit
a :class:`RouteDecision`. Default: ``solo`` / ``main_only``. Follow-ups on an
open Planner topic: ``resume`` / ``to_only`` (not ``full_refan``).

Public aliases (normalized to canonical actions):
  solo → main_only
  helper → main_only (+ host may spawn One helper with allow_informal_leaf)
  planner / open_planner → open_topic
  resume → to_only
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RouteKind = Literal["chat", "topic"]
RouteAction = Literal[
    "main_only",
    "open_topic",
    "to_only",
    "lens_resume",
    "full_refan",
]

VALID_ACTIONS: frozenset[str] = frozenset(
    {"main_only", "open_topic", "to_only", "lens_resume", "full_refan"}
)

# Plain-language / ADHD-friendly aliases → canonical RouteAction
ACTION_ALIASES: dict[str, str] = {
    "solo": "main_only",
    "helper": "main_only",
    "one_helper": "main_only",
    "planner": "open_topic",
    "open_planner": "open_topic",
    "resume": "to_only",
    "resume_planner": "to_only",
}

ROUTER_SYSTEM_PROMPT = """You route Compound Topologies turns for Chat (alias: Main).
Return ONLY compact JSON (no markdown fences):
{
  "kind": "chat" | "topic",
  "topic": <kebab-slug|null>,
  "action": "solo" | "main_only" | "helper" | "planner" | "open_topic" | "resume" | "to_only" | "lens_resume" | "full_refan",
  "lenses": [],
  "reason": "<one short line>"
}

DEFAULT: solo / main_only. Most turns stay in Chat. Do NOT open a Planner for ordinary coding, one-file edits, opinions, or short explains.

Fan criteria (open_topic / planner) — ONLY when:
- multi-file or multi-surface implement, OR
- research with unknown surface area, OR
- user explicitly wants multiple angles / orthogonal lenses.

Rules (intent of the USER message — never use message length):
- solo / main_only / kind=chat: default. Chit-chat, meta, one-file work, Solo implement.
- helper: same as solo for routing; host may spawn One helper Worker (allow_informal_leaf).
- open_topic / planner: complex new work needing a Planner (and maybe Workers). Invent kebab slug.
- to_only / resume: continue an OPEN Planner topic WITHOUT re-running multi-lens Workers.
- lens_resume: user targets one/few Worker lenses; list those lane ids in "lenses".
- full_refan: user explicitly wants breadth re-research / ALL lenses again.
- Prefer resume/to_only over full_refan. Prefer solo over open_topic unless fan criteria match.
- Workers under a Planner must be orthogonally partitioned (disjoint domains or outlooks).
"""


@dataclass
class RouteDecision:
    kind: RouteKind
    action: RouteAction
    topic: str | None = None
    lenses: list[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_route_line(self) -> str:
        """One-line form Chat can emit before spawning/resuming."""
        topic = self.topic or "-"
        lenses = ",".join(self.lenses) if self.lenses else "-"
        return (
            f"route: {self.action} kind: {self.kind} "
            f"topic: {topic} lenses: {lenses}"
        )


def normalize_route_action(action: str) -> str:
    a = (action or "").strip().lower()
    return ACTION_ALIASES.get(a, a)


def parse_route_decision(text: str) -> RouteDecision:
    """Parse JSON or ``route:`` line from a model/Chat reply."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("empty route decision")

    # Try JSON object (possibly fenced)
    candidate = raw
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate)
        candidate = re.sub(r"\s*```$", "", candidate)
    if "{" in candidate:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(candidate[start : end + 1])
                return validate_route_decision(data)
            except json.JSONDecodeError:
                pass

    # route: to_only kind: topic topic: foo lenses: a,b
    m = re.search(
        r"route:\s*(?P<action>\w+)\s+kind:\s*(?P<kind>\w+)\s+"
        r"topic:\s*(?P<topic>[^\s]+)\s+lenses:\s*(?P<lenses>\S+)",
        raw,
        flags=re.I,
    )
    if m:
        lenses_raw = m.group("lenses")
        lenses = (
            []
            if lenses_raw in {"-", "none", "[]"}
            else [x.strip() for x in lenses_raw.split(",") if x.strip()]
        )
        topic = m.group("topic")
        return validate_route_decision(
            {
                "kind": m.group("kind").lower(),
                "action": m.group("action").lower(),
                "topic": None if topic in {"-", "none", "null"} else topic,
                "lenses": lenses,
                "reason": "parsed route line",
            }
        )

    raise ValueError(f"unrecognized route decision: {raw[:200]!r}")


def validate_route_decision(data: dict[str, Any]) -> RouteDecision:
    kind = str(data.get("kind") or "").strip().lower()
    action = normalize_route_action(str(data.get("action") or ""))
    if kind not in {"chat", "topic"}:
        raise ValueError(f"invalid kind: {kind!r}")
    if action not in VALID_ACTIONS:
        raise ValueError(f"invalid action: {action!r}")

    topic = data.get("topic")
    if topic is not None:
        topic = str(topic).strip() or None
        if topic in {"null", "none", "-"}:
            topic = None

    lenses_raw = data.get("lenses") or []
    if isinstance(lenses_raw, str):
        lenses = [x.strip() for x in lenses_raw.split(",") if x.strip()]
    else:
        lenses = [str(x).strip() for x in lenses_raw if str(x).strip()]

    if action == "main_only":
        kind = "chat"
        topic = None
        lenses = []
    elif action == "open_topic":
        kind = "topic"
        if not topic:
            raise ValueError("open_topic requires topic")
    elif action in {"to_only", "lens_resume", "full_refan"}:
        kind = "topic"
        if not topic:
            raise ValueError(f"{action} requires topic")
        if action == "lens_resume" and not lenses:
            raise ValueError("lens_resume requires lenses")

    if action == "lens_resume":
        keep_lenses = lenses
    elif action == "full_refan":
        keep_lenses = lenses  # optional override; empty → host default lanes
    else:
        keep_lenses = []

    return RouteDecision(
        kind=kind,  # type: ignore[arg-type]
        action=action,  # type: ignore[arg-type]
        topic=topic,
        lenses=keep_lenses,
        reason=str(data.get("reason") or ""),
    )


def should_fan_scouts(decision: RouteDecision) -> bool:
    """True only for first open or explicit full re-fan / targeted lens resume."""
    return decision.action in {"open_topic", "full_refan", "lens_resume"}


def scout_lanes_for_decision(
    decision: RouteDecision,
    *,
    default_lanes: list[str],
) -> list[str]:
    if decision.action == "to_only" or decision.action == "main_only":
        return []
    if decision.action == "lens_resume":
        return list(decision.lenses)
    # open_topic / full_refan
    return list(default_lanes)


def coerce_route_with_registry(
    decision: RouteDecision,
    *,
    open_topics: set[str] | frozenset[str] | list[str],
) -> RouteDecision:
    """Fail-soft coerce: ``open_topic`` → ``to_only`` when topic already sticky-open.

    Hosts should call this after ``validate_route_decision`` / ``parse_route_decision``
    and before spawning. Uses an explicit open-topic set (usually
    ``registry.open_topics()``) so the harness stays free of hidden globals.
    """
    if decision.action != "open_topic" or not decision.topic:
        return decision
    opened = {str(t).strip().lower() for t in open_topics if str(t).strip()}
    if decision.topic.strip().lower() not in opened:
        return decision
    reason = decision.reason or ""
    suffix = (
        "COERCED open_topic→to_only: topic slug already sticky-open — "
        "resume the existing Planner (alias TO); invent a new kebab slug if "
        "this is a different topic (slug collision)"
    )
    return RouteDecision(
        kind="topic",
        action="to_only",
        topic=decision.topic,
        lenses=[],
        reason=f"{reason}; {suffix}".strip("; ").strip(),
    )
