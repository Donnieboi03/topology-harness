"""Models allowlist + Hermes fragment."""
from __future__ import annotations

import pytest

from agent_topo_harness.models import (
    assert_allowed,
    hermes_model_block,
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


def test_hermes_model_block_shape():
    block = hermes_model_block()
    assert block["model"]["provider"] == "openrouter"
    assert block["delegation"]["model"] == "google/gemini-3.5-flash"
    assert isinstance(block["fallback_providers"], list)
    assert block["fallback_providers"][0]["provider"] == "openrouter"
    # secondary gemini at end
    assert block["fallback_providers"][-1]["provider"] == "gemini"
