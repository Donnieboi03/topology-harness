#!/usr/bin/env python3
"""Enforce Compound Topologies on Hermes pre_tool_call / pre_llm_call.

pre_tool_call: block Main vault writes (and obvious vault upsert tools).
pre_llm_call: inject mandatory Compound Topologies context every turn.

Stdout JSON only (Hermes shell-hook contract). Empty stdout = allow/no-op.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parents[2]  # adapters/hermes/hooks → repo root
_CONTEXT_FILE = (
    Path(__file__).resolve().parents[1] / "prompts" / "compound_topologies_context.txt"
)

# Tools / path signals that mean durable vault write from Main chat
_VAULT_WRITE_TOOLS = {
    "vault_store_fact",
    "vault_upsert",
    "vault_write",
    "store_fact",
}
_VAULT_WRITE_SUBSTR = (
    "vault_store",
    "obsidian/people",
    "obsidian/orgs",
    "obsidian/reflections",
)


def _load_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _tool_name(event: dict) -> str:
    for key in ("tool_name", "tool", "name"):
        v = event.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _tool_input(event: dict) -> dict:
    for key in ("tool_input", "input", "arguments", "args"):
        v = event.get(key)
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    extra = event.get("extra")
    if isinstance(extra, dict):
        for key in ("tool_input", "args", "input"):
            v = extra.get(key)
            if isinstance(v, dict):
                return v
    return {}


def _is_subagent(event: dict) -> bool:
    """Best-effort: child sessions often carry parent_session_id or depth>0."""
    if event.get("parent_session_id") or event.get("is_subagent"):
        return True
    depth = event.get("depth") or event.get("spawn_depth")
    try:
        if depth is not None and int(depth) > 0:
            return True
    except (TypeError, ValueError):
        pass
    # Hermes may set agent_role
    role = str(event.get("agent_role") or event.get("role") or "").lower()
    if role in {"leaf", "orchestrator", "topic_owner", "subagent", "worker"}:
        return True
    return False


def _looks_like_vault_write(tool: str, tool_input: dict) -> bool:
    t = tool.lower()
    if t in _VAULT_WRITE_TOOLS or any(s in t for s in ("vault_store", "store_fact")):
        return True
    blob = json.dumps(tool_input, ensure_ascii=False).lower()
    if any(s in blob for s in _VAULT_WRITE_SUBSTR):
        # file/write tools targeting vault paths
        if t in {"write_file", "file_write", "write", "create_file", "edit_file", "str_replace"}:
            return True
        if "path" in tool_input or "file_path" in tool_input or "filepath" in tool_input:
            return True
    # terminal writing into obsidian vault
    if t in {"terminal", "run_terminal_cmd", "shell"}:
        cmd = str(tool_input.get("command") or "").lower()
        if "obsidian/" in cmd and any(
            x in cmd for x in (">>", "tee ", "cat >", "printf ", "mv ", "cp ")
        ):
            return True
    return False


def handle_pre_tool_call(event: dict) -> dict | None:
    if _is_subagent(event):
        # Topic Owner may write; leaf writes are policy-enforced by toolsets.
        # Only hard-block Main (depth 0 / no parent).
        return None
    tool = _tool_name(event)
    inp = _tool_input(event)
    if _looks_like_vault_write(tool, inp):
        return {
            "action": "block",
            "message": (
                "COMPOUND TOPOLOGIES: Main must not write durable memory (Obsidian vault). "
                "Spawn a Topic Owner with persist: vault|durable (role=orchestrator) to upsert. "
                f"Blocked tool={tool!r}."
            ),
        }
    return None


def handle_pre_llm_call(_event: dict) -> dict | None:
    try:
        text = _CONTEXT_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        text = "COMPOUND TOPOLOGIES ENFORCED (agent-topo-harness)."
    if not text:
        return None
    return {"context": text}


def main() -> int:
    event = _load_event()
    # Hermes may pass event name in the payload
    name = str(
        event.get("event")
        or event.get("hook_event_name")
        or event.get("type")
        or os.environ.get("HERMES_HOOK_EVENT", "")
    ).lower()

    # Infer from argv: enforce_compound_topologies.py pre_tool_call|pre_llm_call
    if len(sys.argv) > 1:
        name = sys.argv[1].strip().lower() or name

    out: dict | None = None
    if "pre_llm" in name or name == "pre_llm_call":
        out = handle_pre_llm_call(event)
    else:
        # default pre_tool_call
        out = handle_pre_tool_call(event)

    if out:
        sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Never break the agent on hook failure
        raise SystemExit(0)
