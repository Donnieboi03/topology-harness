"""Main → Topic Owner scope + tooling card builder."""
from __future__ import annotations

from typing import Any, Iterable, Sequence


def build_scope_card(
    *,
    topic: str,
    goal: str,
    in_scope: Sequence[str] | None = None,
    out_of_scope: Sequence[str] | None = None,
    composition: str | None = None,
    tooling_allowlist: Sequence[str] | None = None,
    tooling_forbidden: Sequence[str] | None = None,
    caps: dict[str, Any] | None = None,
    persist: str = "none",
    critical_watchlist: Sequence[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Build the structured Main→TO envelope.

    ``composition`` is a non-binding hint (compound id or freeform).
    ``persist`` is ``vault`` or ``none``.
    """
    persist_norm = (persist or "none").strip().lower()
    if persist_norm not in {"vault", "none"}:
        raise ValueError("persist must be 'vault' or 'none'")

    card: dict[str, Any] = {
        "topic": topic.strip(),
        "goal": goal.strip(),
        "scope": {
            "in": list(in_scope or []),
            "out": list(out_of_scope or []),
        },
        "composition": (composition or "").strip() or None,
        "tooling": {
            "allowlist": list(tooling_allowlist or []),
            "forbidden": list(tooling_forbidden or []),
        },
        "caps": dict(caps or {}),
        "persist": persist_norm,
        "critical_watchlist": list(critical_watchlist or []),
        "notes": notes.strip(),
    }
    return card


def format_scope_card_markdown(card: dict[str, Any]) -> str:
    """Render a scope card as markdown for TO goal/context."""
    comp = card.get("composition") or "none"
    caps = card.get("caps") or {}
    caps_bits = ", ".join(f"{k}={v}" for k, v in caps.items()) or "none"
    tooling = card.get("tooling") or {}
    allow = ", ".join(tooling.get("allowlist") or []) or "default"
    forbid = ", ".join(tooling.get("forbidden") or []) or "none"
    scope = card.get("scope") or {}
    in_items = _bullets(scope.get("in") or [])
    out_items = _bullets(scope.get("out") or [])
    critical = _bullets(card.get("critical_watchlist") or [])
    notes = (card.get("notes") or "").strip()

    lines = [
        f"# Scope card: {card.get('topic', '')}",
        "",
        "## Goal",
        card.get("goal", ""),
        "",
        "## Scope",
        "### In",
        in_items,
        "### Out",
        out_items,
        "",
        f"## Composition hint",
        f"composition: {comp}",
        "",
        "## Caps",
        caps_bits,
        "",
        "## Tooling",
        f"- Allowlist: {allow}",
        f"- Forbidden: {forbid}",
        "",
        f"## Persist",
        f"persist: {card.get('persist', 'none')}",
        "",
        "## Critical watchlist",
        critical,
    ]
    if notes:
        lines.extend(["", "## Notes", notes])
    return "\n".join(lines).rstrip() + "\n"


def _bullets(items: Iterable[str]) -> str:
    seq = [str(x).strip() for x in items if str(x).strip()]
    if not seq:
        return "- (none)"
    return "\n".join(f"- {x}" for x in seq)
