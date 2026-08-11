"""Unit tests for sticky registry, intent routing, and TT stubs."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_topo_harness.decorators import TopicNotOpenError, assert_topic_open, topo_gate
from agent_topo_harness.routing import (
    coerce_route_with_registry,
    parse_route_decision,
    scout_lanes_for_decision,
    should_fan_scouts,
    validate_route_decision,
)
from agent_topo_harness.sticky import StickyRegistry, sticky_path_for_session
from agent_topo_harness.stubs import (
    format_tt_stub,
    parse_tt_stub,
    stubs_to_brief_findings,
)


def test_sticky_get_or_create_and_persist(tmp_path: Path) -> None:
    reg = StickyRegistry(host_session_id="sess1")
    orch, created = reg.get_or_create_orchestrator(
        "Logging Logs DB",
        topology_urn="topology:topic:logging-logs-db--to:01A",
        composition="research-build",
        parent_run_id="fan-1",
    )
    assert created and orch.topic == "logging-logs-db" and orch.kind == "orchestrator"
    assert orch.topology_urn.endswith("--to:01A")
    assert orch.composition == "research-build"
    assert orch.parent_run_id == "fan-1"
    orch2, created2 = reg.get_or_create_to("logging-logs-db")  # alias
    assert not created2 and orch2 is orch
    tt, c3 = reg.get_or_create_tt(
        "logging-logs-db",
        "scout_schema",
        topology_urn="topology:swarm:logging-logs-db--scout-schema:01B",
        parent_run_id="fan-1",
    )
    assert c3 and tt.lane == "scout_schema" and tt.kind == "tt"
    assert tt.parent_run_id == "fan-1"
    reg.bind_session(orch, "child-orch-1")
    path = sticky_path_for_session(tmp_path, "sess1")
    reg.save(path)
    loaded = StickyRegistry.load(path)
    assert loaded.get_orchestrator("logging-logs-db").session_id == "child-orch-1"
    assert loaded.get_orchestrator("logging-logs-db").topology_urn == (
        "topology:topic:logging-logs-db--to:01A"
    )
    assert loaded.get_orchestrator("logging-logs-db").composition == "research-build"
    assert loaded.get_tt("logging-logs-db", "scout_schema") is not None
    assert loaded.get_tt("logging-logs-db", "scout_schema").parent_run_id == "fan-1"
    # legacy JSON shape still loads
    legacy = {
        "hermes_session_id": "legacy",
        "tos": {
            "cost-audit": {
                "kind": "topic_owner",
                "topic": "cost-audit",
                "lane": None,
                "session_id": "c1",
                "meta": {},
            }
        },
        "leaves": {
            "cost-audit/scout_a": {
                "kind": "leaf",
                "topic": "cost-audit",
                "lane": "scout_a",
                "session_id": "c2",
                "meta": {"topology_urn": "topology:leaf:cost-audit--scout-a:x"},
            }
        },
    }
    leg_path = tmp_path / "legacy.json"
    leg_path.write_text(json.dumps(legacy))
    leg = StickyRegistry.load(leg_path)
    assert leg.get_orchestrator("cost-audit").session_id == "c1"
    assert leg.get_tt("cost-audit", "scout_a").kind == "tt"
    assert leg.get_tt("cost-audit", "scout_a").topology_urn == (
        "topology:leaf:cost-audit--scout-a:x"
    )
    loaded.release_topic("logging-logs-db")
    assert loaded.get_orchestrator("logging-logs-db") is None
    assert loaded.lanes_for("logging-logs-db") == []


def test_route_parse_json_and_line() -> None:
    d = parse_route_decision(
        '{"kind":"topic","action":"to_only","topic":"cost-audit","lenses":[],"reason":"continue"}'
    )
    assert d.action == "to_only" and d.topic == "cost-audit"
    assert not should_fan_scouts(d)
    assert scout_lanes_for_decision(d, default_lanes=["a", "b"]) == []

    line = "route: full_refan kind: topic topic: cost-audit lenses: -"
    d2 = parse_route_decision(line)
    assert d2.action == "full_refan" and should_fan_scouts(d2)
    assert scout_lanes_for_decision(d2, default_lanes=["a", "b"]) == ["a", "b"]

    d3 = validate_route_decision(
        {
            "kind": "topic",
            "action": "lens_resume",
            "topic": "logging-logs-db",
            "lenses": ["scout_schema"],
            "reason": "schema only",
        }
    )
    assert scout_lanes_for_decision(d3, default_lanes=["a", "b", "c"]) == [
        "scout_schema"
    ]


def test_route_rejects_bad_refan_without_topic() -> None:
    with pytest.raises(ValueError):
        validate_route_decision(
            {"kind": "topic", "action": "to_only", "topic": None, "lenses": []}
        )


def test_tt_stub_parse_and_brief() -> None:
    stub = parse_tt_stub(
        json.dumps(
            {
                "lane": "scout_gaps",
                "bullets": ["no crash logs", "column is wrong shape"],
                "sources": ["PLAN.md"],
                "open": ["pick Logs DB schema"],
                "confidence": "high",
            }
        )
    )
    assert stub.lane == "scout_gaps" and len(stub.bullets) == 2
    markdown = stubs_to_brief_findings(
        [stub, format_tt_stub("scout_impl", bullets=["step 1", "step 2"])]
    )
    assert "scout_gaps" in markdown and "scout_impl" in markdown
    assert "Findings (from TT stubs)" in markdown


def test_coerce_open_topic_when_sticky() -> None:
    d = validate_route_decision(
        {
            "kind": "topic",
            "action": "open_topic",
            "topic": "cost-audit",
            "lenses": [],
            "reason": "new",
        }
    )
    coerced = coerce_route_with_registry(d, open_topics=["cost-audit"])
    assert coerced.action == "to_only"
    assert "coerced" in coerced.reason
    same = coerce_route_with_registry(d, open_topics=[])
    assert same.action == "open_topic"


def test_topo_gate_requires_open_topic() -> None:
    reg = StickyRegistry(host_session_id="gate")

    @topo_gate(reg)
    def spawn_tt(topic: str, lane: str) -> str:
        return f"{topic}/{lane}"

    with pytest.raises(TopicNotOpenError):
        spawn_tt("missing-topic", "scout")
    reg.get_or_create_orchestrator("missing-topic")
    assert spawn_tt("missing-topic", "scout") == "missing-topic/scout"
    assert_topic_open(reg, "missing-topic")
