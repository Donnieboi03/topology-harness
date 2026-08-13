"""Durable knowledge blackboard (v0) — regioned JSONL store.

Regions: hypotheses, evidence, open_questions, conclusions, meta.

Write policy (TO-only via ``assert_can_write``):
- hypotheses / evidence — append-only
- open_questions — set-like upsert (dedupe by normalized text)
- conclusions — single-writer (TO); never raw TT stubs
- meta — topic lifecycle (retire / abandon)

Primary flush: ``retire_topic(role, topic, brief, *, abandoned=False)``.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

from .durable_memory import assert_can_write, normalize_role

Region = Literal[
    "hypotheses",
    "evidence",
    "open_questions",
    "conclusions",
    "meta",
]

REGIONS: tuple[Region, ...] = (
    "hypotheses",
    "evidence",
    "open_questions",
    "conclusions",
    "meta",
)

APPEND_ONLY_REGIONS: frozenset[str] = frozenset({"hypotheses", "evidence"})
SET_LIKE_REGIONS: frozenset[str] = frozenset({"open_questions"})
CONCLUSION_REGION: str = "conclusions"

# File lock map keyed by resolved path string
_PATH_LOCKS: dict[str, threading.RLock] = {}
_PATH_LOCKS_GUARD = threading.Lock()


def _lock_for(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _PATH_LOCKS_GUARD:
        if key not in _PATH_LOCKS:
            _PATH_LOCKS[key] = threading.RLock()
        return _PATH_LOCKS[key]


def _norm_topic(topic: str) -> str:
    return (topic or "").strip().lower().replace(" ", "-")


def _norm_question(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _is_raw_tt_stub(item: Any) -> bool:
    """True when payload looks like a TT stub (lane + bullets), not a gated conclusion."""
    if not isinstance(item, dict):
        return False
    keys = {str(k).lower() for k in item}
    if "lane" in keys and "bullets" in keys:
        return True
    if "bullets" in keys and "confidence" in keys and "text" not in keys:
        return True
    return False


def _gated_conclusion(item: Any) -> dict[str, Any] | None:
    """Accept only explicitly gated conclusions; reject stubs and ungated prose."""
    if _is_raw_tt_stub(item):
        return None
    # Bare strings cannot carry a gate — reject (do not invent PASS).
    if isinstance(item, str) or not isinstance(item, dict):
        return None
    text = str(item.get("text") or item.get("conclusion") or "").strip()
    if not text:
        return None
    if "gate" not in item or item.get("gate") is None or str(item.get("gate")).strip() == "":
        return None
    gate = str(item.get("gate")).strip().upper()
    if gate not in {"PASS", "PASSED", "OK", "TRUE"}:
        return None
    out = {"text": text, "gate": "PASS"}
    for k, v in item.items():
        if k not in out and k not in {"lane", "bullets", "confidence"}:
            out[k] = v
    return out


@dataclass
class BlackboardRecord:
    topic: str
    region: Region
    payload: dict[str, Any]
    ts: float = field(default_factory=time.time)
    writer_role: str = "orchestrator"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "topic": self.topic,
            "region": self.region,
            "writer_role": self.writer_role,
            "payload": self.payload,
        }


class Blackboard:
    """Append-oriented durable KB backed by a JSONL file."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def _append(self, record: BlackboardRecord) -> BlackboardRecord:
        line = json.dumps(record.to_dict(), ensure_ascii=False) + "\n"
        lock = _lock_for(self.path)
        with lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line)
                fh.flush()
        return record

    def _require_to(self, role: str) -> str:
        assert_can_write(role)
        return normalize_role(role)

    def iter_records(self, topic: str | None = None) -> list[dict[str, Any]]:
        lock = _lock_for(self.path)
        with lock:
            if not self.path.is_file():
                return []
            text = self.path.read_text(encoding="utf-8")
        out: list[dict[str, Any]] = []
        want = _norm_topic(topic) if topic else None
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if want and _norm_topic(str(row.get("topic") or "")) != want:
                continue
            out.append(row)
        return out

    def region_payloads(self, topic: str, region: Region) -> list[dict[str, Any]]:
        return [
            dict(r.get("payload") or {})
            for r in self.iter_records(topic)
            if r.get("region") == region
        ]

    def append_hypothesis(
        self, role: str, topic: str, hypothesis: dict[str, Any] | str
    ) -> BlackboardRecord:
        writer = self._require_to(role)
        t = _norm_topic(topic)
        payload = (
            {"text": hypothesis.strip()}
            if isinstance(hypothesis, str)
            else dict(hypothesis)
        )
        return self._append(
            BlackboardRecord(
                topic=t, region="hypotheses", payload=payload, writer_role=writer
            )
        )

    def append_evidence(
        self, role: str, topic: str, evidence: dict[str, Any] | str
    ) -> BlackboardRecord:
        """Mid-topic evidence append (TO-gated)."""
        writer = self._require_to(role)
        t = _norm_topic(topic)
        if isinstance(evidence, str):
            payload: dict[str, Any] = {"claim": evidence.strip()}
        else:
            payload = dict(evidence)
        return self._append(
            BlackboardRecord(
                topic=t, region="evidence", payload=payload, writer_role=writer
            )
        )

    def upsert_open_questions(
        self, role: str, topic: str, questions: Iterable[str]
    ) -> list[BlackboardRecord]:
        """Set-like upsert: skip questions already present for the topic."""
        writer = self._require_to(role)
        t = _norm_topic(topic)
        existing = {
            _norm_question(str((p.get("text") or p.get("question") or "")))
            for p in self.region_payloads(t, "open_questions")
        }
        written: list[BlackboardRecord] = []
        for q in questions:
            text = str(q).strip()
            if not text:
                continue
            key = _norm_question(text)
            if key in existing:
                continue
            existing.add(key)
            written.append(
                self._append(
                    BlackboardRecord(
                        topic=t,
                        region="open_questions",
                        payload={"text": text},
                        writer_role=writer,
                    )
                )
            )
        return written

    def write_conclusion(
        self, role: str, topic: str, conclusion: dict[str, Any] | str
    ) -> BlackboardRecord:
        writer = self._require_to(role)
        gated = _gated_conclusion(conclusion)
        if gated is None:
            raise ValueError(
                "conclusions must be gated TO findings; raw TT stubs are rejected"
            )
        return self._append(
            BlackboardRecord(
                topic=_norm_topic(topic),
                region="conclusions",
                payload=gated,
                writer_role=writer,
            )
        )

    def retire_topic(
        self,
        role: str,
        topic: str,
        brief: dict[str, Any],
        *,
        abandoned: bool = False,
    ) -> dict[str, Any]:
        """Primary flush: promote typed brief regions into the blackboard.

        If ``abandoned``, mark meta abandoned and skip conclusions promotion.
        Never promotes raw TT stubs into conclusions.
        """
        writer = self._require_to(role)
        t = _norm_topic(topic)
        brief = dict(brief or {})
        counts = {
            "hypotheses": 0,
            "evidence": 0,
            "open_questions": 0,
            "conclusions": 0,
            "meta": 0,
            "rejected_stub_conclusions": 0,
        }

        for item in brief.get("hypotheses") or []:
            self.append_hypothesis(writer, t, item)
            counts["hypotheses"] += 1

        for item in brief.get("evidence") or []:
            self.append_evidence(writer, t, item)
            counts["evidence"] += 1

        oq = brief.get("open_questions") or []
        written_q = self.upsert_open_questions(writer, t, oq)
        counts["open_questions"] = len(written_q)

        if not abandoned:
            for item in brief.get("conclusions") or []:
                if _is_raw_tt_stub(item):
                    counts["rejected_stub_conclusions"] += 1
                    continue
                try:
                    self.write_conclusion(writer, t, item)
                    counts["conclusions"] += 1
                except ValueError:
                    counts["rejected_stub_conclusions"] += 1

        meta_payload: dict[str, Any] = {
            "event": "abandoned" if abandoned else "retired",
            "abandoned": bool(abandoned),
            "composition": brief.get("composition"),
            "model_cast": brief.get("model_cast"),
        }
        self._append(
            BlackboardRecord(
                topic=t, region="meta", payload=meta_payload, writer_role=writer
            )
        )
        counts["meta"] = 1
        return {"topic": t, "abandoned": bool(abandoned), "counts": counts}


def retire_topic(
    role: str,
    topic: str,
    brief: dict[str, Any],
    *,
    path: Path | str,
    abandoned: bool = False,
) -> dict[str, Any]:
    """Module-level helper both hosts call on topic close."""
    return Blackboard(path).retire_topic(role, topic, brief, abandoned=abandoned)
