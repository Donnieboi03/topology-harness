"""Unit tests for sticky idle TTL, TO-touch refresh, topics_for_main."""
from __future__ import annotations

import json
import time
from pathlib import Path

from topology_harness.sticky import (
    STICKY_IDLE_TTL_SECONDS,
    StickyRegistry,
    sticky_path_for_session,
)


def test_to_resume_refreshes_touched_at() -> None:
    reg = StickyRegistry(host_session_id="s")
    orch, _ = reg.get_or_create_to("alpha")
    assert orch.touched_at is not None
    first = orch.touched_at
    time.sleep(0.02)
    orch2, created = reg.get_or_create_to("alpha")
    assert not created and orch2 is orch
    assert orch.touched_at is not None and orch.touched_at > first


def test_tt_refreshes_parent_to_touched_at() -> None:
    reg = StickyRegistry(host_session_id="s")
    to, _ = reg.get_or_create_to("beta")
    to.touched_at = time.time() - 1000
    old = to.touched_at
    reg.get_or_create_tt("beta", "plane")
    assert to.touched_at is not None and to.touched_at > old


def test_bind_session_to_refreshes() -> None:
    reg = StickyRegistry(host_session_id="s")
    to, _ = reg.get_or_create_to("gamma")
    to.touched_at = time.time() - 500
    old = to.touched_at
    time.sleep(0.02)
    reg.bind_session(to, "child-1")
    assert to.touched_at is not None and to.touched_at > old


def test_touch_topic_helper() -> None:
    reg = StickyRegistry(host_session_id="s")
    to, _ = reg.get_or_create_to("delta")
    to.touched_at = 1.0
    assert reg.touch_topic("delta") is to
    assert to.touched_at is not None and to.touched_at > 1.0
    assert reg.touch_topic("missing") is None


def test_purge_idle_releases_stale_not_fresh() -> None:
    reg = StickyRegistry(host_session_id="s")
    fresh, _ = reg.get_or_create_to("fresh-topic")
    stale, _ = reg.get_or_create_to("stale-topic")
    now = time.time()
    fresh.touched_at = now
    stale.touched_at = now - (25 * 3600)
    released = reg.purge_idle(ttl_seconds=24 * 3600, now=now)
    assert released == ["stale-topic"]
    assert reg.get_orchestrator("fresh-topic") is not None
    assert reg.get_orchestrator("stale-topic") is None


def test_purge_idle_missing_touched_at_is_stale() -> None:
    reg = StickyRegistry(host_session_id="s")
    to, _ = reg.get_or_create_to("legacy")
    to.touched_at = None
    released = reg.purge_idle(ttl_seconds=24 * 3600, now=time.time())
    assert "legacy" in released
    assert reg.open_topics() == []


def test_topics_for_main_caps_to_most_recent() -> None:
    reg = StickyRegistry(host_session_id="s")
    a, _ = reg.get_or_create_to("older")
    b, _ = reg.get_or_create_to("newer")
    a.touched_at = 100.0
    b.touched_at = 200.0
    assert reg.topics_for_main(limit=1) == ["newer"]
    assert reg.topics_for_main(limit=2) == ["newer", "older"]


def test_touched_at_persists_roundtrip(tmp_path: Path) -> None:
    reg = StickyRegistry(host_session_id="sess")
    to, _ = reg.get_or_create_to("persist-me")
    assert to.touched_at is not None
    stamp = to.touched_at
    path = sticky_path_for_session(tmp_path, "sess")
    reg.save(path)
    loaded = StickyRegistry.load(path)
    h = loaded.get_orchestrator("persist-me")
    assert h is not None
    assert h.touched_at == stamp
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert "touched_at" in raw["orchestrators"]["persist-me"]


def test_default_idle_ttl_is_24h() -> None:
    assert STICKY_IDLE_TTL_SECONDS == 24 * 3600
