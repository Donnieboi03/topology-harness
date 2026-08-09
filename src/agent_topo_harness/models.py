"""Load and validate agent-topo-harness model routing config."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_HARNESS_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG = _HARNESS_ROOT / "config" / "models.yaml"


def harness_root() -> Path:
    return _HARNESS_ROOT


def config_path() -> Path:
    return _DEFAULT_CONFIG


def load_models_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or config_path()
    if not cfg_path.is_file():
        raise FileNotFoundError(f"models config not found: {cfg_path}")
    text = cfg_path.read_text(encoding="utf-8")
    if yaml is None:
        raise RuntimeError("PyYAML required to load models.yaml (pip/uv install pyyaml)")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("models.yaml must be a mapping")
    allow = list(data.get("allowlist") or [])
    if not allow:
        raise ValueError("models.yaml allowlist must be non-empty")
    pref = data.get("preference") or {}
    for key in ("model", "delegation_model"):
        m = pref.get(key)
        if m and m not in allow:
            raise ValueError(f"preference.{key}={m!r} not in allowlist")
    for fb in data.get("fallbacks") or []:
        if fb not in allow:
            raise ValueError(f"fallback {fb!r} not in allowlist")
    for role, m in (data.get("roles") or {}).items():
        if m not in allow:
            raise ValueError(f"roles.{role}={m!r} not in allowlist")
    return data


def assert_allowed(model: str, *, path: Path | None = None) -> str:
    """Raise ValueError if model is outside the harness allowlist."""
    cfg = load_models_config(path)
    allow = set(cfg["allowlist"])
    mid = (model or "").strip()
    if mid not in allow:
        raise ValueError(
            f"model {mid!r} not in agent-topo-harness allowlist "
            f"({sorted(allow)}); refuse to use unbounded OpenRouter models"
        )
    return mid


def role_model(role: str, *, path: Path | None = None) -> str:
    cfg = load_models_config(path)
    roles = cfg.get("roles") or {}
    key = (role or "").strip().lower().replace("-", "_")
    aliases = {"to": "topic_owner", "owner": "topic_owner", "parent": "main"}
    key = aliases.get(key, key)
    if key not in roles:
        raise KeyError(f"unknown role {role!r}; known={sorted(roles)}")
    return assert_allowed(roles[key], path=path)


def hermes_model_block(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fragment for Hermes config.yaml model: / delegation: / fallback_providers."""
    data = cfg or load_models_config()
    pref = data["preference"]
    provider = data.get("provider") or "openrouter"
    base_url = data.get("base_url") or "https://openrouter.ai/api/v1"
    fallbacks = [
        {"provider": provider, "model": m} for m in (data.get("fallbacks") or [])
    ]
    secondary = data.get("secondary_provider") or {}
    if secondary.get("provider") and secondary.get("model"):
        fallbacks.append(
            {
                "provider": secondary["provider"],
                "model": secondary["model"],
            }
        )
    return {
        "model": {
            "default": pref["model"],
            "provider": provider,
            "base_url": base_url,
        },
        "delegation": {
            "model": pref["delegation_model"],
            "provider": provider,
            "base_url": base_url,
        },
        "fallback_providers": fallbacks,
    }
