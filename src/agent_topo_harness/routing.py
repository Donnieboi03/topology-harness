"""Intent routing for Main: when to stay in chat, open a TO, or re-fan.

No length / keyword heuristics. Hosts ask Main (or a tiny router call) to emit
a :class:`RouteDecision`. Default follow-up bias: ``to_only`` (resume sticky TO),
not ``full_refan``.
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

ROUTER_SYSTEM_PROMPT = """You route Compound Topologies follow-ups for Main.
Return ONLY compact JSON (no markdown fences):
{
  "kind": "chat" | "topic",
  "topic": <kebab-slug|null>,
  "action": "main_only" | "open_topic" | "to_only" | "lens_resume" | "full_refan",
  "lenses": [],
  "reason": "<one short line>"
}

Rules (intent of the USER message — never use message length):
- main_only / kind=chat: ONLY pure chit-chat, greetings, usage/status meta, or host system notes with no user work ask.
- open_topic: substantive new work when that topic is NOT already in open_topics (docs, bugs, features, audits, new skills). Invent a short kebab topic slug. Empty open_topics does NOT mean main_only.
- to_only: continue an OPEN topic via its Orchestrator WITHOUT re-running multi-lens TT research. Prefer this when open_topics is non-empty and the user is continuing that work.
- lens_resume: user targets one/few specific TT lenses; list those lane ids in "lenses".
- full_refan: user explicitly wants breadth re-research / re-check ALL TT lenses again.
- Prefer to_only over full_refan. Prefer open_topic over main_only for real work asks.
- Never refuse open_topic just because open_topics is empty — that is when open_topic is most common.
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
        """One-line form Main can emit before spawning/resuming."""
        topic = self.topic or "-"
        lenses = ",".join(self.lenses) if self.lenses else "-"
        return (
            f"route: {self.action} kind: {self.kind} "
            f"topic: {topic} lenses: {lenses}"
        )


def parse_route_decision(text: str) -> RouteDecision:
    """Parse JSON or ``route:`` line from a model/Main reply."""
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
    action = str(data.get("action") or "").strip().lower()
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
        if action != "lens_resume":
            # full_refan / to_only ignore stray lenses unless provided
            pass

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
