"""Tests for durable blackboard (KB v0) + retire_topic flush."""
from __future__ import annotations

import threading
from pathlib import Path

import pytest

from topology_harness.blackboard import Blackboard, retire_topic


def test_two_concurrent_tos_append(tmp_path: Path) -> None:
    path = tmp_path / "kb.jsonl"
    errors: list[BaseException] = []

    def writer(topic: str, n: int) -> None:
        try:
            bb = Blackboard(path)
            for i in range(n):
                bb.append_evidence(
                    "orchestrator",
                    topic,
                    {"claim": f"{topic}-{i}", "source": "test", "gate": "PASS"},
                )
        except BaseException as exc:  # noqa: BLE001 — collect for join
            errors.append(exc)

    t1 = threading.Thread(target=writer, args=("topic-a", 20))
    t2 = threading.Thread(target=writer, args=("topic-b", 20))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert not errors

    bb = Blackboard(path)
    a = bb.region_payloads("topic-a", "evidence")
    b = bb.region_payloads("topic-b", "evidence")
    assert len(a) == 20 and len(b) == 20
    assert all(p["claim"].startswith("topic-a-") for p in a)
    assert all(p["claim"].startswith("topic-b-") for p in b)


def test_main_cannot_write_conclusions(tmp_path: Path) -> None:
    bb = Blackboard(tmp_path / "kb.jsonl")
    with pytest.raises(PermissionError):
        bb.write_conclusion("main", "cost-audit", {"text": "done", "gate": "PASS"})
    with pytest.raises(PermissionError):
        bb.append_evidence("main", "cost-audit", {"claim": "x"})
    with pytest.raises(PermissionError):
        retire_topic(
            "main",
            "cost-audit",
            {"conclusions": [{"text": "nope", "gate": "PASS"}]},
            path=tmp_path / "kb.jsonl",
        )


def test_abandon_skips_conclusions(tmp_path: Path) -> None:
    path = tmp_path / "kb.jsonl"
    brief = {
        "hypotheses": [{"text": "H1"}],
        "evidence": [{"claim": "E1", "source": "doc", "gate": "PASS"}],
        "open_questions": ["Q1"],
        "conclusions": [{"text": "should not land", "gate": "PASS"}],
        "composition": "research-swarm",
        "model_cast": "flash",
    }
    result = retire_topic(
        "orchestrator", "abandon-me", brief, path=path, abandoned=True
    )
    assert result["abandoned"] is True
    assert result["counts"]["conclusions"] == 0
    assert result["counts"]["hypotheses"] == 1
    assert result["counts"]["evidence"] == 1

    bb = Blackboard(path)
    assert bb.region_payloads("abandon-me", "conclusions") == []
    meta = bb.region_payloads("abandon-me", "meta")
    assert len(meta) == 1
    assert meta[0]["abandoned"] is True
    assert meta[0]["event"] == "abandoned"
    assert meta[0]["composition"] == "research-swarm"


def test_retire_promotes_typed_regions(tmp_path: Path) -> None:
    path = tmp_path / "kb.jsonl"
    brief = {
        "hypotheses": [{"text": "logs schema wrong"}],
        "evidence": [
            {"claim": "column mistyped", "source": "PLAN.md", "gate": "PASS"}
        ],
        "open_questions": ["pick Logs DB schema", "pick Logs DB schema"],  # dedupe
        "conclusions": [{"text": "use jsonb payload", "gate": "PASS"}],
        "composition": "research-build",
        "model_cast": "tiered",
    }
    # Raw TT stub must not become a conclusion
    brief["conclusions"].append(
        {"lane": "scout", "bullets": ["raw stub"], "confidence": "high"}
    )

    result = retire_topic("to", "logging-logs-db", brief, path=path)
    assert result["abandoned"] is False
    assert result["counts"]["hypotheses"] == 1
    assert result["counts"]["evidence"] == 1
    assert result["counts"]["open_questions"] == 1  # deduped
    assert result["counts"]["conclusions"] == 1
    assert result["counts"]["rejected_stub_conclusions"] == 1

    bb = Blackboard(path)
    assert bb.region_payloads("logging-logs-db", "hypotheses")[0]["text"] == (
        "logs schema wrong"
    )
    assert bb.region_payloads("logging-logs-db", "evidence")[0]["claim"] == (
        "column mistyped"
    )
    oq = bb.region_payloads("logging-logs-db", "open_questions")
    assert len(oq) == 1 and oq[0]["text"] == "pick Logs DB schema"
    conclusions = bb.region_payloads("logging-logs-db", "conclusions")
    assert len(conclusions) == 1
    assert conclusions[0]["text"] == "use jsonb payload"
    assert conclusions[0]["gate"] == "PASS"
    meta = bb.region_payloads("logging-logs-db", "meta")[0]
    assert meta["event"] == "retired"
    assert meta["composition"] == "research-build"

    # Mid-topic helpers still TO-gated
    bb.append_evidence("orchestrator", "logging-logs-db", {"claim": "extra"})
    bb.upsert_open_questions("orchestrator", "logging-logs-db", ["new q"])
    assert len(bb.region_payloads("logging-logs-db", "evidence")) == 2


def test_ungated_conclusions_rejected(tmp_path: Path) -> None:
    path = tmp_path / "kb.jsonl"
    result = retire_topic(
        "orchestrator",
        "gate-required",
        {
            "conclusions": [
                "bare string must not PASS",
                {"text": "missing gate field"},
                {"text": "explicit fail", "gate": "FAIL"},
                {"text": "ok", "gate": "PASS"},
            ],
        },
        path=path,
    )
    assert result["counts"]["conclusions"] == 1
    assert result["counts"]["rejected_stub_conclusions"] >= 2
    bb = Blackboard(path)
    conclusions = bb.region_payloads("gate-required", "conclusions")
    assert len(conclusions) == 1
    assert conclusions[0]["text"] == "ok"
    assert conclusions[0]["gate"] == "PASS"
