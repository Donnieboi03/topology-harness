"""Compound Topologies Hermes hook behavior."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_HOOK = (
    Path(__file__).resolve().parents[1]
    / "adapters"
    / "hermes"
    / "hooks"
    / "enforce_compound_topologies.py"
)


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("enforce_ct", _HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_blocks_main_vault_store(hook):
    out = hook.handle_pre_tool_call(
        {"tool_name": "vault_store_fact", "tool_input": {"fact": "x"}}
    )
    assert out and out["action"] == "block"
    assert "durable memory" in out["message"]


def test_allows_subagent_vault(hook):
    out = hook.handle_pre_tool_call(
        {
            "parent_session_id": "parent",
            "tool_name": "vault_store_fact",
            "tool_input": {"fact": "x"},
        }
    )
    assert out is None


def test_blocks_write_to_obsidian_path(hook):
    out = hook.handle_pre_tool_call(
        {
            "tool_name": "write_file",
            "args": {"path": "/vault/obsidian/people/foo.md", "content": "hi"},
        }
    )
    assert out and out["action"] == "block"


def test_pre_llm_injects_context(hook):
    out = hook.handle_pre_llm_call({})
    assert out and "COMPOUND TOPOLOGIES" in out["context"]


def test_cli_pre_tool_stdout(hook, monkeypatch, capsys):
    payload = json.dumps(
        {
            "hook_event_name": "pre_tool_call",
            "tool_name": "vault_store_fact",
            "tool_input": {},
        }
    )
    monkeypatch.setattr(
        "sys.stdin",
        type("S", (), {"read": staticmethod(lambda: payload)})(),
    )
    monkeypatch.setattr("sys.argv", ["enforce", "pre_tool_call"])
    assert hook.main() == 0
    printed = capsys.readouterr().out
    data = json.loads(printed)
    assert data["action"] == "block"
