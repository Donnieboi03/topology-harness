"""Host-agnostic sticky TO / TT registry.

Compound Topologies assume one TO handle per topic and one TT
handle per ``(topic, lane)`` until the host chat session ends (or Main /
TO releases).

This module is the portable registry. Hosts store ``session_id`` (or any
opaque handle) on each entry and map it to their spawn/resume primitive.
"""
from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

# TO = Topic Orchestrator (host role often ``orchestrator``).
# TT = Topic Topology worker under a TO (scout / plane / gen / …).
HandleKind = Literal["orchestrator", "tt"]

# Persistence aliases accepted on load
_KIND_ALIASES = {
    "orchestrator": "orchestrator",
    "topic_owner": "orchestrator",
    "to": "orchestrator",
    "tt": "tt",
    "leaf": "tt",
}


@dataclass
class StickyHandle:
    kind: HandleKind
    topic: str
    lane: str | None = None
    session_id: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        if self.kind == "orchestrator":
            return f"orch:{self.topic}"
        return f"tt:{self.topic}/{self.lane or ''}"


class StickyRegistry:
    """In-memory sticky map; optional JSON persistence for host adapters."""

    def __init__(self, *, host_session_id: str | None = None, hermes_session_id: str | None = None) -> None:
        # hermes_session_id kept as keyword alias for older call sites
        self.host_session_id = host_session_id or hermes_session_id
        self._orchestrators: dict[str, StickyHandle] = {}
        self._tts: dict[tuple[str, str], StickyHandle] = {}
        self._lock = threading.RLock()

    @property
    def hermes_session_id(self) -> str | None:
        """Alias for ``host_session_id`` (legacy keyword)."""
        return self.host_session_id

    @hermes_session_id.setter
    def hermes_session_id(self, value: str | None) -> None:
        self.host_session_id = value

    def get_orchestrator(self, topic: str) -> StickyHandle | None:
        with self._lock:
            return self._orchestrators.get(_norm_topic(topic))

    # Legacy name
    get_to = get_orchestrator

    def get_tt(self, topic: str, lane: str) -> StickyHandle | None:
        with self._lock:
            return self._tts.get((_norm_topic(topic), _norm_lane(lane)))

    get_leaf = get_tt

    def get_or_create_orchestrator(
        self,
        topic: str,
        *,
        session_id: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> tuple[StickyHandle, bool]:
        """Return (handle, created)."""
        t = _norm_topic(topic)
        with self._lock:
            existing = self._orchestrators.get(t)
            if existing is not None:
                if session_id and not existing.session_id:
                    existing.session_id = session_id
                if meta:
                    existing.meta.update(meta)
                return existing, False
            handle = StickyHandle(
                kind="orchestrator",
                topic=t,
                session_id=session_id,
                meta=dict(meta or {}),
            )
            self._orchestrators[t] = handle
            return handle, True

    get_or_create_to = get_or_create_orchestrator

    def get_or_create_tt(
        self,
        topic: str,
        lane: str,
        *,
        session_id: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> tuple[StickyHandle, bool]:
        t = _norm_topic(topic)
        lane_n = _norm_lane(lane)
        key = (t, lane_n)
        with self._lock:
            existing = self._tts.get(key)
            if existing is not None:
                if session_id and not existing.session_id:
                    existing.session_id = session_id
                if meta:
                    existing.meta.update(meta)
                return existing, False
            handle = StickyHandle(
                kind="tt",
                topic=t,
                lane=lane_n,
                session_id=session_id,
                meta=dict(meta or {}),
            )
            self._tts[key] = handle
            return handle, True

    get_or_create_leaf = get_or_create_tt

    def bind_session(self, handle: StickyHandle, session_id: str) -> StickyHandle:
        with self._lock:
            handle.session_id = session_id
            return handle

    def release_topic(self, topic: str) -> None:
        t = _norm_topic(topic)
        with self._lock:
            self._orchestrators.pop(t, None)
            for key in [k for k in self._tts if k[0] == t]:
                del self._tts[key]

    def release_all(self) -> None:
        with self._lock:
            self._orchestrators.clear()
            self._tts.clear()

    def open_topics(self) -> list[str]:
        with self._lock:
            return sorted(self._orchestrators)

    def lanes_for(self, topic: str) -> list[str]:
        t = _norm_topic(topic)
        with self._lock:
            return sorted(lane for (top, lane) in self._tts if top == t)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "host_session_id": self.host_session_id,
                "orchestrators": {k: asdict(v) for k, v in self._orchestrators.items()},
                "tts": {
                    f"{t}/{lane}": asdict(h) for (t, lane), h in self._tts.items()
                },
            }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.snapshot(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> StickyRegistry:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        sid = data.get("host_session_id") or data.get("hermes_session_id")
        reg = cls(host_session_id=sid)
        orch_raw = data.get("orchestrators") or data.get("tos") or {}
        for topic, raw in orch_raw.items():
            reg._orchestrators[_norm_topic(topic)] = _handle_from_dict(raw)
        tt_raw = data.get("tts") or data.get("leaves") or {}
        for key, raw in tt_raw.items():
            h = _handle_from_dict(raw)
            lane = h.lane or (key.split("/", 1)[1] if "/" in key else "")
            reg._tts[(_norm_topic(h.topic), _norm_lane(lane))] = h
        return reg


def sticky_path_for_session(
    state_dir: str | Path,
    host_session_id: str,
) -> Path:
    """Conventional host path: ``<state_dir>/sticky/<session_id>.json``."""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in host_session_id)
    return Path(state_dir) / "sticky" / f"{safe}.json"


def _norm_topic(topic: str) -> str:
    t = (topic or "").strip().lower().replace(" ", "-")
    if not t:
        raise ValueError("topic is required")
    return t


def _norm_lane(lane: str) -> str:
    lane_n = (lane or "").strip().lower().replace(" ", "_")
    if not lane_n:
        raise ValueError("lane is required for TT handles")
    return lane_n


def _handle_from_dict(raw: dict[str, Any]) -> StickyHandle:
    kind_raw = str(raw.get("kind") or "tt").lower()
    kind = _KIND_ALIASES.get(kind_raw, "tt")
    if kind not in {"orchestrator", "tt"}:
        kind = "tt"
    return StickyHandle(
        kind=kind,  # type: ignore[arg-type]
        topic=str(raw.get("topic") or ""),
        lane=raw.get("lane"),
        session_id=raw.get("session_id"),
        meta=dict(raw.get("meta") or {}),
    )
