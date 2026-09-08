"""Load and validate topology-harness model routing config."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_PKG_DIR = Path(__file__).resolve().parent
_PACKAGED_CONFIG = _PKG_DIR / "config" / "models.yaml"
# Editable/src layout: …/topology-harness/src/topology_harness → parents[1] = checkout
_CHECKOUT_ROOT = _PKG_DIR.parents[1]
_CHECKOUT_CONFIG = _CHECKOUT_ROOT / "config" / "models.yaml"

# Atom name aliases → canonical atom key in models.yaml ``atoms``
_ATOM_ALIASES: dict[str, str] = {
    "swarm": "swarm",
    "research-swarm": "swarm",
    "research_swarm": "swarm",
    "plane": "plane",
    "plane-audit": "plane",
    "plane_audit": "plane",
    "cove": "cove",
    "verify-claims": "cove",
    "verify_claims": "cove",
    "shard": "shard",
    "build-shard": "shard",
    "build_shard": "shard",
    "parallel-build": "shard",
    "parallel_build": "shard",
}

# Skill-ish names → atom defaults (compat for hosts that still pass these)
_LEGACY_ROLE_TO_ATOM: dict[str, str] = {
    "scout": "swarm",
    "tt": "swarm",
    "leaf": "swarm",
    "generator": "shard",
    "gen": "shard",
    "critiquer": "cove",
    "critic": "cove",
}


def harness_root() -> Path:
    """Checkout root when present (SKILL/docs); else the installed package dir."""
    if (_CHECKOUT_ROOT / "SKILL.md").is_file():
        return _CHECKOUT_ROOT
    return _PKG_DIR


def config_path() -> Path:
    """Resolve models.yaml for checkout or wheel install.

    Order: ``TOPOLOGY_HARNESS_MODELS`` env → packaged data → checkout
    ``config/models.yaml`` (symlink or file).
    """
    env = (os.environ.get("TOPOLOGY_HARNESS_MODELS") or "").strip()
    if env:
        return Path(env)
    if _PACKAGED_CONFIG.is_file():
        return _PACKAGED_CONFIG
    if _CHECKOUT_CONFIG.is_file():
        return _CHECKOUT_CONFIG
    raise FileNotFoundError(
        "models.yaml not found (packaged config/models.yaml or checkout config/)"
    )


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
    ladder = list(data.get("ladder") or data.get("fallbacks") or [])
    for fb in ladder:
        if fb not in allow:
            raise ValueError(f"ladder/fallback {fb!r} not in allowlist")
    for fb in data.get("fallbacks") or []:
        if fb not in allow:
            raise ValueError(f"fallback {fb!r} not in allowlist")
    for role, m in (data.get("roles") or {}).items():
        if m not in allow:
            raise ValueError(f"roles.{role}={m!r} not in allowlist")
    for atom, m in (data.get("atoms") or {}).items():
        if m not in allow:
            raise ValueError(f"atoms.{atom}={m!r} not in allowlist")
    secondary = data.get("secondary_provider") or {}
    if isinstance(secondary, dict) and secondary.get("model"):
        sm = str(secondary.get("model") or "").strip()
        resolved = resolve_allowlisted_model(sm, allow)
        if not resolved:
            raise ValueError(
                f"secondary_provider.model={sm!r} not in allowlist "
                f"(or unresolved alias); refuse unbounded fallbacks"
            )
        # Normalize to the allowlisted id so hosts never see a side-channel id.
        secondary["model"] = resolved
        data["secondary_provider"] = secondary
    return data


def resolve_allowlisted_model(
    model: str, allow: list[str] | set[str] | None = None
) -> str | None:
    """Map a model id (or bare alias) onto an allowlist entry, or None."""
    mid = (model or "").strip()
    if not mid:
        return None
    allow_list = list(allow) if allow is not None else list(
        load_models_config().get("allowlist") or []
    )
    if mid in allow_list:
        return mid
    mid_l = mid.lower()
    for entry in allow_list:
        el = entry.lower()
        if el == mid_l or el.endswith("/" + mid_l) or el.split("/", 1)[-1] == mid_l:
            return entry
    return None


def assert_allowed(model: str, *, path: Path | None = None) -> str:
    """Raise ValueError if model is outside the harness allowlist."""
    cfg = load_models_config(path)
    allow = set(cfg["allowlist"])
    mid = (model or "").strip()
    if mid not in allow:
        raise ValueError(
            f"model {mid!r} not in topology-harness allowlist "
            f"({sorted(allow)}); refuse to use unbounded OpenRouter models"
        )
    return mid


def resolve_atom_key(atom: str | None) -> str | None:
    """Map atom / paradigm / compound alias → canonical atoms.* key, or None."""
    if not atom or not str(atom).strip():
        return None
    raw = str(atom).strip().lower().replace("_", "-")
    if raw in _ATOM_ALIASES:
        return _ATOM_ALIASES[raw]
    # try underscore form
    raw2 = str(atom).strip().lower().replace("-", "_")
    if raw2 in _ATOM_ALIASES:
        return _ATOM_ALIASES[raw2]
    # bare name already canonical?
    if raw in ("swarm", "plane", "cove", "shard"):
        return raw
    return None


def atom_model(atom: str, *, path: Path | None = None) -> str:
    """Default TT model for an atom type."""
    cfg = load_models_config(path)
    atoms = cfg.get("atoms") or {}
    key = resolve_atom_key(atom)
    if not key or key not in atoms:
        raise KeyError(
            f"unknown atom {atom!r}; known={sorted(atoms)} "
            f"(aliases={sorted(set(_ATOM_ALIASES.values()))})"
        )
    return assert_allowed(str(atoms[key]), path=path)


def role_model(role: str, *, path: Path | None = None) -> str:
    """Control-plane role model, or legacy skill alias → atom default."""
    cfg = load_models_config(path)
    roles = cfg.get("roles") or {}
    key = (role or "").strip().lower().replace("-", "_")
    aliases = {
        "to": "topic_owner",
        "owner": "topic_owner",
        "orchestrator": "topic_owner",
        "planner": "topic_owner",
        "parent": "main",
        "intent": "main",
        "route": "main",
        "router": "main",
        "chat": "main",
    }
    key = aliases.get(key, key)
    if key in roles:
        return assert_allowed(roles[key], path=path)
    # Legacy scout/gen/critic → atom defaults (skills removed from cast)
    atom = _LEGACY_ROLE_TO_ATOM.get(key)
    if atom:
        return atom_model(atom, path=path)
    raise KeyError(
        f"unknown role {role!r}; known roles={sorted(roles)} "
        f"atoms={sorted((cfg.get('atoms') or {}))} "
        f"legacy={sorted(_LEGACY_ROLE_TO_ATOM)}"
    )


def resolve_child_model(
    *,
    explicit: str | None = None,
    hermes_role: str = "tt",
    atom: str | None = None,
    paradigm: str | None = None,
    delegation_default: str | None = None,
    path: Path | None = None,
) -> str:
    """Pick the start model for a delegated child.

    Priority: explicit TO override → TO role → atom/paradigm default →
    delegation_default → swarm atom.

    ``hermes_role`` takes the canonical Compound Topologies names ``tt`` /
    ``to``; plain aliases ``planner`` / ``worker`` / ``chat`` and legacy
    Hermes spellings ``leaf`` / ``orchestrator`` are accepted.
    """
    if explicit and str(explicit).strip():
        return assert_allowed(str(explicit).strip(), path=path)
    role = (hermes_role or "tt").strip().lower().replace("-", "_")
    if role in {"orchestrator", "topic_owner", "to", "planner"}:
        return role_model("topic_owner", path=path)
    if role in {"chat", "main"}:
        return role_model("main", path=path)
    if role in {"worker", "tt", "leaf"}:
        # Fall through to atom / delegation defaults (Worker has no fixed role model).
        pass
    key = resolve_atom_key(atom) or resolve_atom_key(paradigm)
    if key:
        return atom_model(key, path=path)
    if delegation_default and str(delegation_default).strip():
        return assert_allowed(str(delegation_default).strip(), path=path)
    return atom_model("swarm", path=path)


def ladder_models(cfg: dict[str, Any] | None = None) -> list[str]:
    """High → low model ids used for down-only fallback slices."""
    data = cfg or load_models_config()
    ladder = list(data.get("ladder") or data.get("fallbacks") or [])
    return [str(m).strip() for m in ladder if str(m).strip()]


def models_below(start: str, cfg: dict[str, Any] | None = None) -> list[str]:
    """Return ladder entries strictly below ``start`` (never upgrades)."""
    data = cfg or load_models_config()
    ladder = ladder_models(data)
    mid = (start or "").strip()
    if not mid:
        return list(ladder)
    try:
        idx = ladder.index(mid)
    except ValueError:
        return [m for m in ladder if m != mid]
    return list(ladder[idx + 1 :])


def fallback_entries_below(
    start: str,
    cfg: dict[str, Any] | None = None,
    *,
    include_secondary: bool = True,
) -> list[dict[str, str]]:
    """OpenRouter-shaped fallback_providers entries for everything below ``start``."""
    data = cfg or load_models_config()
    provider = data.get("provider") or "openrouter"
    base_url = data.get("base_url") or "https://openrouter.ai/api/v1"
    below = models_below(start, data)
    entries = [
        {"provider": provider, "model": m, "base_url": base_url}
        for m in below
    ]
    if include_secondary:
        secondary = data.get("secondary_provider") or {}
        sp = secondary.get("provider")
        sm_raw = secondary.get("model")
        if sp and sm_raw:
            allow = list(data.get("allowlist") or [])
            sm = resolve_allowlisted_model(str(sm_raw), allow)
            if not sm:
                sm = None  # refuse non-allowlisted secondary
            else:
                # Down-only: if secondary maps onto the ladder, only keep it when
                # that ladder id is strictly below ``start``.
                ladder = [
                    str(x) for x in (data.get("ladder") or data.get("fallbacks") or [])
                ]
                if sm in ladder and sm not in below:
                    sm = None  # would be an upgrade — skip
            if sm:
                identity = (str(sp).lower(), sm.lower())
                if not any(
                    (e["provider"].lower(), e["model"].lower()) == identity
                    for e in entries
                ):
                    entries.append({"provider": str(sp), "model": sm})
    return entries


def role_fallback_entries(
    role: str,
    cfg: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
) -> list[dict[str, str]]:
    """Down-only fallback chain for a control-plane role or legacy alias."""
    start = role_model(role, path=path)
    data = cfg if cfg is not None else load_models_config(path)
    return fallback_entries_below(start, data)


def atom_fallback_entries(
    atom: str,
    cfg: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
) -> list[dict[str, str]]:
    """Down-only fallback chain for an atom's default TT model."""
    start = atom_model(atom, path=path)
    data = cfg if cfg is not None else load_models_config(path)
    return fallback_entries_below(start, data)


def host_model_block(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Host config fragment: Main down-only fallbacks + atom default map.

    Hermes ``fallback_providers`` is the Main slice only (walks from top on 429).
    Children get per-start-model chains via the nest patch + ``fallback_entries_below``.
    """
    data = cfg or load_models_config()
    pref = data["preference"]
    provider = data.get("provider") or "openrouter"
    base_url = data.get("base_url") or "https://openrouter.ai/api/v1"
    main_model = pref["model"]
    main_fallbacks = fallback_entries_below(main_model, data)
    atom_fbs = {
        atom: fallback_entries_below(model, data)
        for atom, model in (data.get("atoms") or {}).items()
    }
    role_fbs = {
        role: fallback_entries_below(model, data)
        for role, model in (data.get("roles") or {}).items()
    }
    return {
        "model": {
            "default": main_model,
            "provider": provider,
            "base_url": base_url,
        },
        "delegation": {
            "model": pref["delegation_model"],
            "provider": provider,
            "base_url": base_url,
        },
        "fallback_providers": main_fallbacks,
        "atoms": dict(data.get("atoms") or {}),
        "atom_fallbacks": atom_fbs,
        "role_fallbacks": role_fbs,
        "ladder": ladder_models(data),
    }
