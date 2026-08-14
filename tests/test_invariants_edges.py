"""Edge cases + control-plane invariants (TTL, retire≠release, Main card, gates)."""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

import pytest

from topology_harness.durable_memory import (
    assert_can_write,
    guarded_write,
    write_allowed,
)
from topology_harness.escalate import build_critical_approval_payload
from topology_harness.routing import (
    RouteDecision,
    coerce_route_with_registry,
    parse_route_decision,
    validate_route_decision,
)
from topology_harness.scope import build_scope_card, format_scope_card_markdown
from topology_harness.spawn_policy import SpawnPolicyError, assert_spawn_policy
from topology_harness.sticky import (
    STICKY_IDLE_TTL_SECONDS,
    StickyRegistry,
    sticky_idle_ttl_seconds,
)
from topology_harness.stubs import parse_tt_stub


# ── Sticky TTL / Main surface (rational: no topic pile-up) ───────────────────


def test_sticky_idle_ttl_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOPOLOGY_HARNESS_STICKY_IDLE_TTL", "3600")
    assert sticky_idle_ttl_seconds() == 3600.0
    monkeypatch.setenv("TOPOLOGY_HARNESS_STICKY_IDLE_TTL", "not-a-number")
    assert sticky_idle_ttl_seconds() == float(24 * 3600)
    monkeypatch.delenv("TOPOLOGY_HARNESS_STICKY_IDLE_TTL", raising=False)
    assert sticky_idle_ttl_seconds() == float(24 * 3600)


def test_purge_idle_uses_default_ttl_when_none() -> None:
    """Default purge must release idle topics so Main's open set cannot pile up."""
    reg = StickyRegistry(host_session_id="inv")
    stale, _ = reg.get_or_create_to("stale")
    fresh, _ = reg.get_or_create_to("fresh")
    now = time.time()
    stale.touched_at = now - (STICKY_IDLE_TTL_SECONDS + 1)
    fresh.touched_at = now
    released = reg.purge_idle(ttl_seconds=None, now=now)
    assert released == ["stale"]
    assert reg.topics_for_main() == ["fresh"]
    assert len(reg.open_topics()) == 1


def test_invariant_topics_for_main_default_limit_is_one() -> None:
    reg = StickyRegistry(host_session_id="inv")
    a, _ = reg.get_or_create_to("a")
    b, _ = reg.get_or_create_to("b")
    a.touched_at = 1.0
    b.touched_at = 2.0
    assert reg.topics_for_main() == ["b"]


def test_invariant_default_ttl_is_24h_not_forever() -> None:
    assert STICKY_IDLE_TTL_SECONDS == 24 * 3600
    assert sticky_idle_ttl_seconds() == 24 * 3600


# ── Durable memory ───────────────────────────────────────────────────────────


def test_write_allowed_and_guarded_write() -> None:
    assert write_allowed("orchestrator") is True
    assert write_allowed("to") is True
    assert write_allowed("main") is False
    assert write_allowed("tt") is False
    assert write_allowed("leaf") is False

    assert guarded_write("orchestrator", lambda: 7) == 7
    with pytest.raises(PermissionError):
        guarded_write("main", lambda: 1)
    with pytest.raises(PermissionError):
        assert_can_write("leaf")


# ── Spawn policy edges ───────────────────────────────────────────────────────


def test_spawn_not_atomic_atom_raises_spawn_policy_error() -> None:
    with pytest.raises(SpawnPolicyError, match="NotAtomic|atomic|refine"):
        assert_spawn_policy(
            parent_depth=1,
            role="leaf",
            topic="t",
            atom="refine-loop",
            goal="run refine",
        )


def test_spawn_refuses_leaf_mint_when_atomic_requested() -> None:
    """If an atom was requested, refuse a resolved paradigm of ``leaf``."""
    with pytest.raises(SpawnPolicyError, match="refusing to mint topology:leaf"):
        assert_spawn_policy(
            parent_depth=1,
            role="leaf",
            topic="auth",
            atom="swarm",
            paradigm="leaf",  # explicit leaf override would mint leaf despite atom
            goal="scout",
        )


def test_informal_leaf_flag_allows_substantive_without_topic() -> None:
    """allow_informal_leaf is an explicit host opt-in escape hatch (documented)."""
    resolved = assert_spawn_policy(
        parent_depth=0,
        role="leaf",
        goal="please implement the fix",
        allow_informal_leaf=True,
    )
    assert resolved == "leaf"


# ── Escalate validation ──────────────────────────────────────────────────────


def test_critical_payload_requires_fields() -> None:
    with pytest.raises(ValueError, match="command"):
        build_critical_approval_payload("", "why", "t1")
    with pytest.raises(ValueError, match="rationale"):
        build_critical_approval_payload("rm -rf /tmp/x", "  ", "t1")
    with pytest.raises(ValueError, match="topic_id"):
        build_critical_approval_payload("echo hi", "why", "")


# ── Scope markdown ───────────────────────────────────────────────────────────


def test_format_scope_card_markdown() -> None:
    card = build_scope_card(
        topic="auth",
        goal="Fix refresh",
        in_scope=["token path"],
        out_of_scope=["billing"],
        composition="debug-compound",
        persist="vault",
        notes="ship today",
    )
    assert card["persist"] == "durable"
    md = format_scope_card_markdown(card)
    assert "# Scope card: auth" in md
    assert "Fix refresh" in md
    assert "debug-compound" in md
    assert "persist: durable" in md
    assert "ship today" in md


# ── Stubs / routing edges ────────────────────────────────────────────────────


def test_parse_tt_stub_empty_and_truncated_bullets() -> None:
    empty = parse_tt_stub("", default_lane="scout")
    assert empty.lane == "scout" and empty.bullets == [] and empty.confidence == "low"

    bad_json = parse_tt_stub('{"lane": "x", "bullets": [', default_lane="scout")
    assert bad_json.lane == "scout"
    assert isinstance(bad_json.bullets, list)

    many = parse_tt_stub(
        "\n".join(f"- bullet {i}" for i in range(10)),
        default_lane="plane",
    )
    assert len(many.bullets) == 5


def test_validate_and_coerce_route_edges() -> None:
    with pytest.raises(ValueError, match="invalid action"):
        validate_route_decision({"kind": "topic", "action": "nope", "topic": "t"})
    with pytest.raises(ValueError, match="open_topic requires topic"):
        validate_route_decision({"kind": "topic", "action": "open_topic"})
    with pytest.raises(ValueError, match="lens_resume requires lenses"):
        validate_route_decision(
            {"kind": "topic", "action": "lens_resume", "topic": "t", "lenses": []}
        )

    d = RouteDecision(
        kind="topic", action="to_only", topic="cost-audit", lenses=[], reason=""
    )
    same = coerce_route_with_registry(d, open_topics=["cost-audit"])
    assert same.action == "to_only"  # non-open_topic passthrough

    open_d = parse_route_decision(
        '{"kind":"topic","action":"open_topic","topic":"new-one","lenses":[],"reason":"x"}'
    )
    still = coerce_route_with_registry(open_d, open_topics=["other"])
    assert still.action == "open_topic"


# ── CLI dispatch ─────────────────────────────────────────────────────────────


def test_cli_main_dispatch(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path) -> None:
    from topology_harness import run as run_mod

    monkeypatch.setattr(sys, "argv", ["topology-harness", "--help"])
    run_mod.main()
    assert "doctor" in capsys.readouterr().out.lower()

    monkeypatch.setattr(sys, "argv", ["topology-harness", "--version"])
    run_mod.main()
    assert capsys.readouterr().out.strip()

    monkeypatch.setattr(sys, "argv", ["topology-harness", "cursor-map"])
    run_mod.main()
    assert "Main" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["topology-harness", "compounds"])
    run_mod.main()
    out = capsys.readouterr().out
    assert "research-build" in out or "debug-compound" in out

    monkeypatch.setattr(sys, "argv", ["topology-harness", "doctrine"])
    run_mod.main()
    assert "swarm" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["topology-harness", "print(1+1)"])
    with pytest.raises(SystemExit) as exc:
        run_mod.main()
    assert exc.value.code == 0
    assert "2" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["topology-harness", "sticky"])
    with pytest.raises(SystemExit) as exc2:
        run_mod.main()
    assert exc2.value.code == 2

    # missing sticky session file → exit 1
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["topology-harness", "sticky", "no-such-session"])
    with pytest.raises(SystemExit) as exc3:
        run_mod.main()
    assert exc3.value.code == 1


# ── Docs / doctrine claim consistency ────────────────────────────────────────


def test_doctrine_mentions_sticky_hygiene_not_archive() -> None:
    from topology_harness.run import DOCTRINE, CURSOR_MAP

    # Durable writes TO-only remains; sticky resume is hygiene
    assert "assert_can_write" in DOCTRINE
    assert "to_only" in DOCTRINE
    assert "StickyRegistry" in CURSOR_MAP or "sticky" in CURSOR_MAP.lower()


def test_sticky_docs_agree_on_24h_ttl_and_retire_vs_release() -> None:
    """Repo claims must match the ephemeral sticky policy (not forever pile-up)."""
    root = Path(__file__).resolve().parents[1]
    sticky_doc = (root / "docs" / "sticky-registry.md").read_text(encoding="utf-8")
    host_doc = (root / "docs" / "host-contracts.md").read_text(encoding="utf-8")
    topo_doc = (root / "docs" / "agent-topologies.md").read_text(encoding="utf-8")

    for text in (sticky_doc, host_doc):
        assert "24h" in text or "24 h" in text.lower() or "86400" in text
        assert "retire" in text.lower() and "release" in text.lower()
        assert "topics_for_main" in text

    # Must not claim sticky lives only until session end without TTL
    assert "idle TTL" in topo_doc or "24h" in topo_doc or "purge_idle" in topo_doc
    assert "knowledge archive" not in sticky_doc.lower() or "not a knowledge" in sticky_doc.lower()
