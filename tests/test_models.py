"""Models allowlist + host config fragment."""
from __future__ import annotations

import pytest

from agent_topo_harness.models import (
    assert_allowed,
    hermes_model_block,
    host_model_block,
    load_models_config,
    role_model,
)


def test_load_models_config_has_allowlist():
    cfg = load_models_config()
    assert cfg["provider"] == "openrouter"
    assert "google/gemini-3-flash-preview" in cfg["allowlist"]
    assert cfg["preference"]["model"] in cfg["allowlist"]
    assert cfg["preference"]["delegation_model"] in cfg["allowlist"]


def test_assert_allowed_rejects_unknown():
    with pytest.raises(ValueError, match="allowlist"):
        assert_allowed("openai/gpt-5-unbounded-fantasy")


def test_role_model_aliases():
    assert role_model("main") == "google/gemini-3-flash-preview"
    assert role_model("TO") == role_model("topic_owner")
    assert role_model("orchestrator") == role_model("topic_owner")


def test_host_model_block_shape():
    block = host_model_block()
    assert hermes_model_block() == block  # alias
    assert block["model"]["provider"] == "openrouter"
    assert block["model"]["default"] == "google/gemini-3-flash-preview"
    assert block["delegation"]["model"] == "google/gemini-3-flash-preview"
    assert isinstance(block["fallback_providers"], list)
    assert block["fallback_providers"][0]["provider"] == "openrouter"
    models = [f["model"] for f in block["fallback_providers"]]
    assert models[0] == "google/gemini-2.5-flash"
    assert block["fallback_providers"][-1]["provider"] == "gemini"
    assert block["fallback_providers"][-1]["model"] == "gemini-2.5-flash"


def test_roles_premium_only_gen_critiquer():
    cfg = load_models_config()
    assert cfg["roles"]["topic_owner"] == "google/gemini-3-flash-preview"
    assert cfg["roles"]["scout"] == "google/gemini-3-flash-preview"
    assert cfg["roles"]["generator"] == "google/gemini-3.5-flash"
    assert cfg["roles"]["critiquer"] == "google/gemini-3.5-flash"
    assert cfg["preference"]["delegation_model"] == "google/gemini-3-flash-preview"


def test_fallbacks_omit_flash_preview_as_first_when_default():
    """Main/delegation already on 3-flash — first failover is 2.5."""
    cfg = load_models_config()
    assert cfg["fallbacks"][0] == "google/gemini-2.5-flash"
    assert "google/gemini-3.5-flash" not in cfg["fallbacks"]
