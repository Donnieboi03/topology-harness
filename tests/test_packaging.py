"""Packaging / install-layout unit tests (no live network)."""
from __future__ import annotations

import os
from pathlib import Path

import topology_harness
from topology_harness.models import config_path, harness_root, load_models_config


def test_packaged_models_yaml_ships_with_package() -> None:
    packaged = Path(topology_harness.__file__).resolve().parent / "config" / "models.yaml"
    assert packaged.is_file(), "config/models.yaml must be package data"
    assert config_path().resolve() == packaged.resolve()
    cfg = load_models_config()
    assert cfg["roles"]["main"]


def test_harness_root_checkout_or_package() -> None:
    root = harness_root()
    pkg = Path(topology_harness.__file__).resolve().parent
    # Editable/checkout: SKILL.md at repo root; wheel: package dir.
    if (root / "SKILL.md").is_file():
        assert (root / "src" / "topology_harness" / "__init__.py").is_file()
        assert (root / "docs" / "adapters" / "cursor.md").is_file()
    else:
        assert root == pkg
        assert (pkg / "config" / "models.yaml").is_file()


def test_config_path_env_override(tmp_path: Path, monkeypatch) -> None:
    custom = tmp_path / "models.yaml"
    custom.write_text(
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
        "ladder: [google/gemini-2.5-flash-lite]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TOPOLOGY_HARNESS_MODELS", str(custom))
    assert config_path() == custom
    assert load_models_config()["preference"]["model"] == "google/gemini-2.5-flash-lite"
    monkeypatch.delenv("TOPOLOGY_HARNESS_MODELS", raising=False)
    # restore default resolution
    assert "TOPOLOGY_HARNESS_MODELS" not in os.environ
    assert config_path().name == "models.yaml"
    assert load_models_config()["preference"]["model"] == "google/gemini-3.1-flash-lite"
