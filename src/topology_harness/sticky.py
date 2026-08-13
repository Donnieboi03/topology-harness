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
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

# TO = Topic Orchestrator (host role often ``orchestrator``).
# TT = Topic Topology worker under a TO (scout / plane / gen / …).
HandleKind = Literal["orchestrator", "tt"]

# Schema constants for host adapters / doctor
STICKY_HANDLE_KINDS: tuple[str, ...] = ("orchestrator", "tt")
STICKY_PERSIST_KEYS: tuple[str, ...] = (
    "host_session_id",
    "hermes_session_id",  # legacy alias accepted on load
    "orchestrators",
    "tts",
    "tos",  # legacy
    "leaves",  # legacy
)

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
    # Graph telemetry (sibling to URN; persisted with the handle)
    topology_urn: str | None = None
    composition: Any = None
    parent_run_id: str | None = None

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
        
        # Per-topic locking
        self._global_lock = threading.Lock()
        self._topic_locks: dict[str, threading.RLock] = {}
        
        # Background save state
        self._save_thread: threading.Thread | None = None
        self._save_path: Path | None = None
        self._save_pending = threading.Event()
        self._save_shutdown = False
        self._save_interval = 2.0  # Debounce interval

    def _get_topic_lock(self, topic: str) -> threading.RLock:
        t = _norm_topic(topic)
        with self._global_lock:
            if t not in self._topic_locks:
                self._topic_locks[t] = threading.RLock()
            return self._topic_locks[t]

    @property
    def hermes_session_id(self) -> str | None:
        """Alias for ``host_session_id`` (legacy keyword)."""
        return self.host_session_id

    @hermes_session_id.setter
    def hermes_session_id(self, value: str | None) -> None:
        self.host_session_id = value

    def get_orchestrator(self, topic: str) -> StickyHandle | None:
        with self._get_topic_lock(topic):
            return self._orchestrators.get(_norm_topic(topic))

    # Legacy name
    get_to = get_orchestrator

    def get_tt(self, topic: str, lane: str) -> StickyHandle | None:
        with self._get_topic_lock(topic):
            return self._tts.get((_norm_topic(topic), _norm_lane(lane)))

    def get_or_create_orchestrator(
        self,
        topic: str,
        *,
        session_id: str | None = None,
        meta: dict[str, Any] | None = None,
        topology_urn: str | None = None,
        composition: Any = None,
        parent_run_id: str | None = None,
    ) -> tuple[StickyHandle, bool]:
        """Return (handle, created)."""
        t = _norm_topic(topic)
        with self._get_topic_lock(t):
            existing = self._orchestrators.get(t)
            if existing is not None:
                if session_id and not existing.session_id:
                    existing.session_id = session_id
                if meta:
                    existing.meta.update(meta)
                _merge_telemetry(
                    existing,
                    topology_urn=topology_urn,
                    composition=composition,
                    parent_run_id=parent_run_id,
                )
                self._trigger_save()
                return existing, False
            handle = StickyHandle(
                kind="orchestrator",
                topic=t,
                session_id=session_id,
                meta=dict(meta or {}),
                topology_urn=topology_urn,
                composition=composition,
                parent_run_id=parent_run_id,
            )
            self._orchestrators[t] = handle
            self._trigger_save()
            return handle, True

    get_or_create_to = get_or_create_orchestrator

    def get_or_create_tt(
        self,
        topic: str,
        lane: str,
        *,
        session_id: str | None = None,
        meta: dict[str, Any] | None = None,
        topology_urn: str | None = None,
        composition: Any = None,
        parent_run_id: str | None = None,
    ) -> tuple[StickyHandle, bool]:
        t = _norm_topic(topic)
        lane_n = _norm_lane(lane)
        key = (t, lane_n)
        with self._get_topic_lock(t):
            existing = self._tts.get(key)
            if existing is not None:
                if session_id and not existing.session_id:
                    existing.session_id = session_id
                if meta:
                    existing.meta.update(meta)
                _merge_telemetry(
                    existing,
                    topology_urn=topology_urn,
                    composition=composition,
                    parent_run_id=parent_run_id,
                )
                self._trigger_save()
                return existing, False
            handle = StickyHandle(
                kind="tt",
                topic=t,
                lane=lane_n,
                session_id=session_id,
                meta=dict(meta or {}),
                topology_urn=topology_urn,
                composition=composition,
                parent_run_id=parent_run_id,
            )
            self._tts[key] = handle
            self._trigger_save()
            return handle, True

    def bind_session(
        self,
        handle: StickyHandle,
        session_id: str,
        *,
        topology_urn: str | None = None,
        composition: Any = None,
        parent_run_id: str | None = None,
    ) -> StickyHandle:
        with self._get_topic_lock(handle.topic):
            handle.session_id = session_id
            _merge_telemetry(
                handle,
                topology_urn=topology_urn,
                composition=composition,
                parent_run_id=parent_run_id,
            )
            self._trigger_save()
            return handle

    def release_topic(self, topic: str) -> None:
        t = _norm_topic(topic)
        with self._get_topic_lock(t):
            self._orchestrators.pop(t, None)
            for key in [k for k in self._tts if k[0] == t]:
                del self._tts[key]
            self._trigger_save()

    def set_active_lane(self, topic: str, lane: str) -> StickyHandle | None:
        """Persist ``meta['active_lane']`` on the TO handle (no snapshot schema break)."""
        t = _norm_topic(topic)
        lane_n = _norm_lane(lane)
        with self._get_topic_lock(t):
            handle = self._orchestrators.get(t)
            if handle is None:
                return None
            handle.meta["active_lane"] = lane_n
            self._trigger_save()
            return handle

    def get_active_lane(self, topic: str) -> str | None:
        handle = self.get_orchestrator(topic)
        if handle is None:
            return None
        raw = handle.meta.get("active_lane")
        return str(raw) if raw else None

    def set_task_ledger(self, topic: str, ledger: Any) -> StickyHandle | None:
        return self._set_to_meta_blob(topic, "task_ledger", _ledger_to_dict(ledger))

    def get_task_ledger(self, topic: str) -> dict[str, Any] | None:
        return self._get_to_meta_blob(topic, "task_ledger")

    def set_progress_ledger(self, topic: str, ledger: Any) -> StickyHandle | None:
        return self._set_to_meta_blob(topic, "progress_ledger", _ledger_to_dict(ledger))

    def get_progress_ledger(self, topic: str) -> dict[str, Any] | None:
        return self._get_to_meta_blob(topic, "progress_ledger")

    def set_stall(self, topic: str, stall: Any) -> StickyHandle | None:
        return self._set_to_meta_blob(topic, "stall", _ledger_to_dict(stall))

    def get_stall(self, topic: str) -> dict[str, Any] | None:
        return self._get_to_meta_blob(topic, "stall")

    def _set_to_meta_blob(
        self, topic: str, key: str, value: dict[str, Any] | None
    ) -> StickyHandle | None:
        t = _norm_topic(topic)
        with self._get_topic_lock(t):
            handle = self._orchestrators.get(t)
            if handle is None:
                return None
            if value is None:
                handle.meta.pop(key, None)
            else:
                handle.meta[key] = value
            self._trigger_save()
            return handle

    def _get_to_meta_blob(self, topic: str, key: str) -> dict[str, Any] | None:
        handle = self.get_orchestrator(topic)
        if handle is None:
            return None
        raw = handle.meta.get(key)
        return dict(raw) if isinstance(raw, dict) else None

    def release_all(self) -> None:
        with self._global_lock:
            # Simple global clear for release_all to avoid complex multi-locking
            self._orchestrators.clear()
            self._tts.clear()
            self._trigger_save()

    def open_topics(self) -> list[str]:
        with self._global_lock:
            return sorted(self._orchestrators)

    def lanes_for(self, topic: str) -> list[str]:
        t = _norm_topic(topic)
        with self._get_topic_lock(t):
            return sorted(lane for (top, lane) in self._tts if top == t)

    def snapshot(self) -> dict[str, Any]:
        with self._global_lock:
            return {
                "host_session_id": self.host_session_id,
                "orchestrators": {k: asdict(v) for k, v in self._orchestrators.items()},
                "tts": {
                    f"{t}/{lane}": asdict(h) for (t, lane), h in self._tts.items()
                },
            }

    def save(self, path: str | Path) -> None:
        """Synchronous save (legacy / explicit flush)."""
        self._save_path = Path(path)
        self._perform_save()

    def _trigger_save(self) -> None:
        if self._save_path:
            self._save_pending.set()
            if self._save_thread is None or not self._save_thread.is_alive():
                self._start_save_thread()

    def _start_save_thread(self) -> None:
        self._save_shutdown = False
        self._save_thread = threading.Thread(
            target=self._save_loop, 
            name="StickyRegistrySave",
            daemon=True
        )
        self._save_thread.start()

    def _save_loop(self) -> None:
        while not self._save_shutdown:
            if self._save_pending.wait(timeout=self._save_interval):
                self._save_pending.clear()
                self._perform_save()
            else:
                pass

    def _perform_save(self) -> None:
        if not self._save_path:
            return
        try:
            path = self._save_path
            path.parent.mkdir(parents=True, exist_ok=True)
            data = self.snapshot()
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            tmp.replace(path)
        except Exception:
            pass

    def shutdown(self) -> None:
        self._save_shutdown = True
        self._save_pending.set()
        if self._save_thread:
            self._save_thread.join(timeout=5)

    @classmethod
    def load(cls, path: str | Path) -> StickyRegistry:
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        sid = data.get("host_session_id") or data.get("hermes_session_id")
        reg = cls(host_session_id=sid)
        reg._save_path = path
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


def _merge_telemetry(
    handle: StickyHandle,
    *,
    topology_urn: str | None = None,
    composition: Any = None,
    parent_run_id: str | None = None,
) -> None:
    """Fill telemetry fields when provided (do not clear existing with None)."""
    if topology_urn:
        handle.topology_urn = topology_urn
    if composition is not None:
        handle.composition = composition
    if parent_run_id:
        handle.parent_run_id = parent_run_id


def _ledger_to_dict(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return dict(to_dict())
    if hasattr(value, "__dict__"):
        return {k: v for k, v in vars(value).items() if not k.startswith("_")}
    raise TypeError(f"cannot persist ledger-like value of type {type(value)!r}")


def _handle_from_dict(raw: dict[str, Any]) -> StickyHandle:
    kind_raw = str(raw.get("kind") or "tt").lower()
    kind = _KIND_ALIASES.get(kind_raw, "tt")
    if kind not in {"orchestrator", "tt"}:
        kind = "tt"
    meta = dict(raw.get("meta") or {})
    # Prefer first-class fields; fall back to meta keys from older writers.
    topology_urn = raw.get("topology_urn") or meta.get("topology_urn")
    composition = (
        raw["composition"]
        if "composition" in raw
        else meta.get("composition")
    )
    parent_run_id = raw.get("parent_run_id") or meta.get("parent_run_id")
    return StickyHandle(
        kind=kind,  # type: ignore[arg-type]
        topic=str(raw.get("topic") or ""),
        lane=raw.get("lane"),
        session_id=raw.get("session_id"),
        meta=meta,
        topology_urn=str(topology_urn) if topology_urn else None,
        composition=composition,
        parent_run_id=str(parent_run_id) if parent_run_id else None,
    )
