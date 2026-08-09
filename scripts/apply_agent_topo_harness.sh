#!/usr/bin/env bash
# Wire Compound Topologies enforcement + OpenRouter model bounds into Hermes.
#
# Updates $HERMES_HOME/config.yaml (default: ~/.hermes/profiles/virgil-executor):
#   - skills.external_dirs += this harness (+ $VIRGIL_ROOT/skills when set)
#   - model / delegation / fallback_providers from config/models.yaml
#   - prefill_messages_file → prompts/compound_topologies_prefill.json
#   - hooks → hooks/enforce_compound_topologies.py
#
# Usage:
#   ./scripts/apply_agent_topo_harness.sh
#   ./scripts/apply_agent_topo_harness.sh --dry-run
#   VIRGIL_ROOT=~/Desktop/Code/Virgil HERMES_HOME=~/.hermes/profiles/virgil-executor \
#     ./scripts/apply_agent_topo_harness.sh
set -euo pipefail

HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VIRGIL_ROOT="${VIRGIL_ROOT:-}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes/profiles/virgil-executor}"
CFG="${HERMES_HOME}/config.yaml"
DRY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

if [[ ! -f "$CFG" ]]; then
  echo "error: Hermes config not found: $CFG" >&2
  exit 1
fi
if [[ ! -f "$HARNESS/config/models.yaml" ]]; then
  echo "error: missing $HARNESS/config/models.yaml" >&2
  exit 1
fi

export PYTHONPATH="${HARNESS}/src${VIRGIL_ROOT:+:$VIRGIL_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
export VIRGIL_ROOT
export HARNESS_ROOT="$HARNESS"
export HERMES_CONFIG="$CFG"
export APPLY_DRY_RUN="$DRY"

if command -v uv >/dev/null 2>&1; then
  PY=(uv run --directory "$HARNESS" python)
else
  PY=(python3)
fi

"${PY[@]}" <<'PY'
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import yaml

harness = Path(os.environ["HARNESS_ROOT"])
cfg_path = Path(os.environ["HERMES_CONFIG"])
dry = os.environ.get("APPLY_DRY_RUN") == "1"
virgil = (os.environ.get("VIRGIL_ROOT") or "").strip()

sys.path.insert(0, str(harness / "src"))
from agent_topo_harness.models import hermes_model_block, load_models_config

models = load_models_config()
block = hermes_model_block(models)

text = cfg_path.read_text(encoding="utf-8")
data = yaml.safe_load(text) or {}

# --- external_dirs ---
skills = data.setdefault("skills", {})
ext = list(skills.get("external_dirs") or [])
harness_s = str(harness.resolve())
# Drop stale in-Virgil harness paths so only the standalone root remains
ext = [
    p
    for p in ext
    if "agent-topo-harness" not in Path(p).name
    and not str(p).endswith("/agent-topo-harness")
]
if harness_s not in ext:
    ext.append(harness_s)
if virgil:
    skills_s = str((Path(virgil) / "skills").resolve())
    if skills_s not in ext:
        ext.append(skills_s)
skills["external_dirs"] = ext

# --- models / openrouter ---
data["model"] = {
    **(data.get("model") or {}),
    **block["model"],
}
delegation = data.setdefault("delegation", {})
delegation["model"] = block["delegation"]["model"]
delegation["provider"] = block["delegation"]["provider"]
delegation["base_url"] = block["delegation"]["base_url"]
delegation["max_spawn_depth"] = max(int(delegation.get("max_spawn_depth") or 0), 2)
delegation["orchestrator_enabled"] = True

data["fallback_providers"] = block["fallback_providers"]
data["fallback_model"] = {
    "provider": block["model"]["provider"],
    "model": (models.get("fallbacks") or [block["model"]["default"]])[0],
}

# --- prefill ---
prefill = harness / "prompts" / "compound_topologies_prefill.json"
data["prefill_messages_file"] = str(prefill.resolve())

# --- hooks ---
hook_py = harness / "hooks" / "enforce_compound_topologies.py"
hooks = data.setdefault("hooks", {})
enforce_pre_tool = {
    "command": f"{hook_py.resolve()} pre_tool_call",
    "timeout": 5,
}
enforce_pre_llm = {
    "command": f"{hook_py.resolve()} pre_llm_call",
    "timeout": 5,
}
audit_path = cfg_path.parent / "hooks" / "audit_tool_call.py"
audit = {"command": str(audit_path), "timeout": 5}


def _merge_hooks(existing: list, extra: dict) -> list:
    out = []
    seen = set()
    for item in list(existing or []) + [extra]:
        if not isinstance(item, dict):
            continue
        cmd = str(item.get("command") or "")
        # Drop stale enforce hooks pointing at old paths
        if "enforce_compound_topologies.py" in cmd and cmd != extra.get("command"):
            continue
        if cmd in seen:
            continue
        seen.add(cmd)
        out.append(item)
    return out


pre_tool = list(hooks.get("pre_tool_call") or [])
if audit_path.is_file():
    pre_tool = _merge_hooks([audit], enforce_pre_tool)
    for item in hooks.get("pre_tool_call") or []:
        if isinstance(item, dict) and "enforce_compound_topologies" not in str(
            item.get("command") or ""
        ):
            pre_tool = _merge_hooks(pre_tool, item)
else:
    pre_tool = _merge_hooks(pre_tool, enforce_pre_tool)

hooks["pre_tool_call"] = pre_tool
hooks["pre_llm_call"] = _merge_hooks([], enforce_pre_llm)
if "post_tool_call" not in hooks and audit_path.is_file():
    hooks["post_tool_call"] = [audit]

out_text = yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
if dry:
    print(out_text)
    print("--- dry-run: no write ---", file=sys.stderr)
else:
    bak = cfg_path.with_suffix(".yaml.virgil-topo.bak")
    if not bak.exists():
        shutil.copy2(cfg_path, bak)
    cfg_path.write_text(out_text, encoding="utf-8")
    print(f"updated {cfg_path}")
    print(f"  external_dirs: {skills['external_dirs']}")
    print(f"  model: {data['model']}")
    print(f"  delegation.model: {delegation['model']}")
    print(f"  fallback_providers: {len(data['fallback_providers'])} entries")
    print(f"  prefill: {data['prefill_messages_file']}")
    print("  hooks: pre_tool_call + pre_llm_call enforce_compound_topologies")

    home = cfg_path.parent
    os.environ.setdefault("HERMES_HOME", str(home))
    os.environ["HERMES_ACCEPT_HOOKS"] = "1"
    try:
        from hermes_cli.config import load_config
        from agent import shell_hooks

        cfg2 = load_config()
        cfg2["hooks_auto_accept"] = True
        shell_hooks.register_from_config(cfg2, accept_hooks=True)
        print("  hooks: allowlisted via HERMES_ACCEPT_HOOKS")
    except Exception as exc:
        print(
            "  warn: could not auto-allowlist hooks "
            f"({exc}); use HERMES_ACCEPT_HOOKS=1 hermes hooks doctor"
        )

    auth = home / "auth.json"
    or_ok = False
    if auth.is_file():
        try:
            adata = json.loads(auth.read_text(encoding="utf-8"))
            pool = (adata.get("credential_pool") or {}).get("openrouter") or []
            or_ok = any(
                isinstance(e, dict)
                and str(e.get("api_key") or e.get("key") or "").strip()
                for e in pool
            )
            providers = adata.get("providers") or {}
            or_prov = providers.get("openrouter")
            if isinstance(or_prov, dict):
                or_ok = or_ok or bool(
                    str(or_prov.get("api_key") or or_prov.get("key") or "").strip()
                )
            elif or_prov:
                or_ok = or_ok or bool(str(or_prov).strip())
        except Exception:
            pass
    if not or_ok and not os.environ.get("OPENROUTER_API_KEY"):
        print(
            "  WARN: OpenRouter credentials empty — model.provider is openrouter "
            "but credential_pool.openrouter has no key. Add OPENROUTER_API_KEY "
            "or fill auth.json before expecting Gemini-via-OpenRouter failover."
        )
    print("Restart Hermes gateway for changes to take effect.")
PY
