"""Models allowlist + atom defaults + down-only ladders."""
from __future__ import annotations

import pytest

from topology_harness.models import (
    assert_allowed,
    atom_model,
    fallback_entries_below,
    host_model_block,
    load_models_config,
    models_below,
    resolve_atom_key,
    resolve_child_model,
    role_model,
)


def test_load_models_config_has_allowlist_and_atoms():
    cfg = load_models_config()
    assert cfg["provider"] == "openrouter"
    assert "google/gemini-3.6-flash" in cfg["allowlist"]
    assert set(cfg["atoms"]) == {"swarm", "plane", "cove", "shard"}
    assert set(cfg["roles"]) == {"main", "topic_owner"}
    assert "generator" not in cfg["roles"]
    assert "scout" not in cfg["roles"]
    assert cfg["preference"]["model"] in cfg["allowlist"]


def test_assert_allowed_rejects_unknown():
    with pytest.raises(ValueError, match="allowlist"):
        assert_allowed("openai/gpt-5-unbounded-fantasy")


def test_role_model_control_plane_only():
    assert role_model("main") == "google/gemini-3.1-flash-lite"
    assert role_model("chat") == role_model("main")
    assert role_model("TO") == role_model("topic_owner")
    assert role_model("orchestrator") == "google/gemini-3.7-flash"
    assert role_model("planner") == role_model("topic_owner")


def test_legacy_skill_aliases_map_to_atoms():
    assert role_model("scout") == atom_model("swarm")
    assert role_model("generator") == atom_model("shard")
    assert role_model("critiquer") == atom_model("cove")


def test_atom_model_and_aliases():
    assert atom_model("swarm") == "google/gemini-3.5-flash-lite"
    assert atom_model("plane") == "google/gemini-3.5-flash-lite"
    assert atom_model("cove") == "google/gemini-3.1-flash-lite"
    assert atom_model("shard") == "google/gemini-3.7-flash"
    assert resolve_atom_key("plane-audit") == "plane"
    assert resolve_atom_key("verify-claims") == "cove"
    assert atom_model("research-swarm") == atom_model("swarm")


def test_resolve_child_model_priority():
    assert (
        resolve_child_model(
            explicit="google/gemini-3.6-flash",
            hermes_role="leaf",
            atom="swarm",
        )
        == "google/gemini-3.6-flash"
    )
    assert (
        resolve_child_model(hermes_role="orchestrator", atom="shard")
        == "google/gemini-3.7-flash"
    )
    assert (
        resolve_child_model(hermes_role="planner", atom="shard")
        == "google/gemini-3.7-flash"
    )
    assert (
        resolve_child_model(hermes_role="worker", atom="cove")
        == "google/gemini-3.1-flash-lite"
    )
    assert (
        resolve_child_model(hermes_role="leaf", atom="shard")
        == "google/gemini-3.7-flash"
    )
    assert (
        resolve_child_model(hermes_role="leaf", paradigm="cove")
        == "google/gemini-3.1-flash-lite"
    )


def test_host_model_block_main_down_only_ladder():
    block = host_model_block()
    assert block["model"]["default"] == "google/gemini-3.1-flash-lite"
    assert block["delegation"]["model"] == "google/gemini-3.7-flash"
    models = [f["model"] for f in block["fallback_providers"]]
    # Main starts at 3.1-lite → must NOT try anything above it on the ladder
    assert "google/gemini-3.7-flash" not in models
    assert "google/gemini-3.6-flash" not in models
    assert "google/gemini-3.5-flash" not in models
    assert "google/gemini-3-flash-preview" not in models
    assert "google/gemini-3.5-flash-lite" not in models
    assert "google/gemini-3.1-flash-lite" not in models
    assert models[0] == "google/gemini-2.5-flash"
    assert block["atoms"]["shard"] == "google/gemini-3.7-flash"
    # Secondary must be allowlisted (normalized); still subject to down-only.
    secondary_models = [
        f["model"]
        for f in block["fallback_providers"]
        if f.get("provider") == "gemini"
    ]
    for m in secondary_models:
        assert m in load_models_config()["allowlist"]


def test_secondary_provider_must_be_allowlisted(tmp_path: Path) -> None:
    from topology_harness.models import resolve_allowlisted_model

    assert (
        resolve_allowlisted_model(
            "gemini-2.5-flash",
            ["google/gemini-2.5-flash", "google/gemini-2.5-flash-lite"],
        )
        == "google/gemini-2.5-flash"
    )
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "provider: openrouter\n"
        "base_url: https://openrouter.ai/api/v1\n"
        "allowlist: [google/gemini-2.5-flash-lite]\n"
        "preference:\n"
        "  model: google/gemini-2.5-flash-lite\n"
        "  delegation_model: google/gemini-2.5-flash-lite\n"
        "roles:\n"
        "  main: google/gemini-2.5-flash-lite\n"
        "  topic_owner: google/gemini-2.5-flash-lite\n"
        "atoms:\n"
        "  swarm: google/gemini-2.5-flash-lite\n"
        "  plane: google/gemini-2.5-flash-lite\n"
        "  cove: google/gemini-2.5-flash-lite\n"
        "  shard: google/gemini-2.5-flash-lite\n"
        "ladder: [google/gemini-2.5-flash-lite]\n"
        "secondary_provider:\n"
        "  provider: gemini\n"
        "  model: totally-unbounded-model\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="secondary_provider"):
        load_models_config(bad)


def test_models_below_never_upgrades():
    below_main = models_below("google/gemini-3.1-flash-lite")
    assert "google/gemini-3.6-flash" not in below_main
    assert below_main[0] == "google/gemini-2.5-flash"
    below_gen = models_below("google/gemini-3.6-flash")
    assert below_gen[0] == "google/gemini-3.5-flash"
    entries = fallback_entries_below("google/gemini-3.5-flash-lite")
    assert entries[0]["model"] == "google/gemini-3.1-flash-lite"


def test_ladder_prefers_3x_before_2x():
    cfg = load_models_config()
    ladder = cfg["ladder"]
    assert ladder.index("google/gemini-2.5-flash") > ladder.index(
        "google/gemini-3.1-flash-lite"
    )
