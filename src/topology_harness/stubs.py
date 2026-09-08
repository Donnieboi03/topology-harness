"""Worker stub format — short findings for Planner merge (not user-facing prose).

Workers (aliases: TT / leaf) extract; the Planner (alias: TO) transforms into
the brief / user answer.

When the Planner fans multiple Workers, each Worker MUST be an **orthogonal
partition**: disjoint domain or distinct outlook. Seed-only goals — never the
Planner's filled verdict.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any


# Back-compat export name
TT_STUB_INSTRUCTION = """You are a Worker (alias: TT / Topic Topology worker).
Do NOT write user-facing prose.
Investigate FIRST with your allowed tools, THEN return ONLY a compact stub
(JSON preferred, or ≤5 bullets under fixed headings).

JSON shape:
{
  "lane": "<lens id>",
  "bullets": ["…", "…"],
  "sources": ["…"],
  "open": ["…"],
  "confidence": "low|medium|high",
  "tools_used": ["skill_view|session_search|skills_list|…"]
}

Rules:
- Max 5 bullets; no greetings; no "Next Step" essays; facts/citations only.
- Never emit a stub from titles alone without at least one tool call this turn.
- ORTHOGONAL PARTITION: your lane is a disjoint domain or distinct outlook.
  Do not clone the Planner thesis. Do not converge for agreement.
- Seed-only: invent from your seed + tools — no answer-keys pasted by the Planner.
The Planner (alias TO) merges stubs into the brief and speaks to the user.
"""

WORKER_STUB_INSTRUCTION = TT_STUB_INSTRUCTION


@dataclass
class TTStub:
    lane: str
    bullets: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    open: list[str] = field(default_factory=list)
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# Alias
WorkerStub = TTStub


def format_tt_stub(
    lane: str,
    *,
    bullets: list[str],
    sources: list[str] | None = None,
    open_items: list[str] | None = None,
    confidence: str = "medium",
) -> TTStub:
    return TTStub(
        lane=lane,
        bullets=[b.strip() for b in bullets if b.strip()][:5],
        sources=[s.strip() for s in (sources or []) if s.strip()][:8],
        open=[o.strip() for o in (open_items or []) if o.strip()][:5],
        confidence=confidence if confidence in {"low", "medium", "high"} else "medium",
    )


format_worker_stub = format_tt_stub


def parse_tt_stub(text: str, *, default_lane: str = "unknown") -> TTStub:
    raw = (text or "").strip()
    if not raw:
        return TTStub(lane=default_lane, bullets=[], confidence="low")

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
                return format_tt_stub(
                    str(data.get("lane") or default_lane),
                    bullets=list(data.get("bullets") or []),
                    sources=list(data.get("sources") or []),
                    open_items=list(data.get("open") or []),
                    confidence=str(data.get("confidence") or "medium"),
                )
            except json.JSONDecodeError:
                pass

    lines = []
    for line in raw.splitlines():
        s = re.sub(r"^[\-\*\d\.\)\s]+", "", line).strip()
        if s:
            lines.append(s)
        if len(lines) >= 5:
            break
    return TTStub(lane=default_lane, bullets=lines, confidence="medium")


parse_worker_stub = parse_tt_stub


def stubs_to_brief_findings(stubs: list[TTStub]) -> str:
    """Markdown block the Planner can paste under Findings (merged)."""
    parts: list[str] = ["## Findings (from Worker stubs)", ""]
    for stub in stubs:
        parts.append(f"### {stub.lane} (confidence={stub.confidence})")
        for b in stub.bullets:
            parts.append(f"- {b}")
        if stub.sources:
            parts.append("- Sources: " + "; ".join(stub.sources))
        if stub.open:
            parts.append("- Open: " + "; ".join(stub.open))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"
