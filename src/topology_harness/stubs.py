"""TT stub format — short findings for TO merge (not user-facing prose).

TTs (Topic Topology workers) extract; the TO transforms into the
brief / user answer.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any


TT_STUB_INSTRUCTION = """You are a Topic Topology worker (TT: scout/plane/verifier/…).
Do NOT write user-facing prose.
Return ONLY a compact stub (JSON preferred, or ≤5 bullets under fixed headings).

JSON shape:
{
  "lane": "<lens id>",
  "bullets": ["…", "…"],
  "sources": ["…"],
  "open": ["…"],
  "confidence": "low|medium|high"
}

Rules: max 5 bullets; no greetings; no "Next Step" essays; facts/citations only.
Report your lane's angle even when it diverges from the obvious/majority reading; do not converge for agreement.
The TO will merge stubs into the brief and speak to the user.
"""


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


def stubs_to_brief_findings(stubs: list[TTStub]) -> str:
    """Markdown block the TO can paste under Findings (merged)."""
    parts: list[str] = ["## Findings (from TT stubs)", ""]
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
