"""topology-harness CLI — doctrine card, doctor, cost smoke, Python REPL.

Mirrors browser-harness ergonomics so agents can invoke a single PATH tool:

  topology-harness <<'PY'
  print(ATOMIC_PARADIGMS)
  PY

  topology-harness --doctor
  topology-harness doctrine
"""
from __future__ import annotations

import importlib.metadata
import os
import sys
import traceback
from pathlib import Path
from typing import Any

HELP = """topology-harness — Compound Topologies control-plane helpers

Read SKILL.md for doctrine. This CLI is for agents and hosts.

Typical usage (helpers pre-imported):
  topology-harness <<'PY'
  print(ATOMIC_PARADIGMS)
  print(assert_spawn_policy.__name__)
  PY

Commands:
  topology-harness --help | -h       this help
  topology-harness --version         package version
  topology-harness --doctor | doctor diagnose install + imports + smoke
  topology-harness doctrine | card   print compact control-plane card
  topology-harness cursor-map        print how Main/TO/TT map onto Cursor Tasks
  topology-harness compounds         list named compounds
  topology-harness cost-smoke        run synthetic A/B cost smoke
  topology-harness sticky <session>  load sticky JSON for a session id
                                     (HERMES_HOME state or pass absolute via env)
"""

USAGE = """Usage:
  topology-harness <<'PY'
  # helpers pre-imported from topology_harness
  PY
"""

DOCTRINE = """# Compound Topologies — control plane (topology-harness)

Main
  └── TO(s)     ← flat only (no TO→TO); one topic per TO
        └── TT workers    ← compounds / atoms; stubs only; no further spawn

Hard rules
- Main gates TOs; follow-ups default to_only (sticky resume), not auto re-fan
- Main→leaf blocked for sticky-open / substantive / atomic work (assert_spawn_policy)
- Atom URN paradigms ONLY: swarm | plane | cove (NotAtomicError otherwise)
- refine-loop / debate are composition wiring, NOT atomics
- Durable writes: assert_can_write — TO only (Main/TT blocked)
- Spawn TT under TO: assert_topic_open / topo_gate
- After parse: coerce_route_with_registry(... open_topics=reg.open_topics())
- TTs emit TT_STUB_INSTRUCTION stubs; TO merges / speaks to the user

Cursor host (when using Cursor Rules): this chat = Main; Task sub-agents = TO/TT.
See docs/adapters/cursor.md.

This package is policy — the active host owns spawn/resume/chat/tools.
Docs: topology-harness/docs/  SKILL: topology-harness/SKILL.md
"""

CURSOR_MAP = """# Cursor host map (Compound Topologies)

Main  = this Cursor chat agent (routes; trivial answers in-thread)
TO    = Task generalPurpose — one per topic; merges TT stubs; user voice
TT    = Task explore|generalPurpose|shell — one lens/atom; stubs only

Route autonomously: main_only | open_topic | to_only | lens_resume | full_refan
Sticky file: .cursor/topology-sticky/registry.json  (StickyRegistry)
TT prompts: include TT_STUB_INSTRUCTION
Main must not fan informal leaf Tasks for substantive/sticky work — open TO first

Full adapter: docs/adapters/cursor.md
"""


def _version() -> str:
    try:
        return importlib.metadata.version("topology-harness")
    except importlib.metadata.PackageNotFoundError:
        return "0.4.0-dev"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _helpers_ns() -> dict[str, Any]:
    """Namespace for REPL — public API + common submodules."""
    import topology_harness as th
    from topology_harness import (  # noqa: F401
        ATOMIC_PARADIGMS,
        COMPOUNDS,
        ROUTER_SYSTEM_PROMPT,
        StickyRegistry,
        TT_STUB_INSTRUCTION,
        assert_can_write,
        assert_spawn_policy,
        assert_topic_open,
        coerce_route_with_registry,
        make_topology_urn,
        parse_route_decision,
        parse_tt_stub,
        topo_gate,
    )

    ns: dict[str, Any] = {
        "th": th,
        "topology_harness": th,
        "ATOMIC_PARADIGMS": ATOMIC_PARADIGMS,
        "COMPOUNDS": COMPOUNDS,
        "ROUTER_SYSTEM_PROMPT": ROUTER_SYSTEM_PROMPT,
        "StickyRegistry": StickyRegistry,
        "TT_STUB_INSTRUCTION": TT_STUB_INSTRUCTION,
        "assert_can_write": assert_can_write,
        "assert_spawn_policy": assert_spawn_policy,
        "assert_topic_open": assert_topic_open,
        "coerce_route_with_registry": coerce_route_with_registry,
        "make_topology_urn": make_topology_urn,
        "parse_route_decision": parse_route_decision,
        "parse_tt_stub": parse_tt_stub,
        "topo_gate": topo_gate,
        "Path": Path,
        "os": os,
    }
    # Re-export __all__ symbols
    for name in getattr(th, "__all__", []):
        if hasattr(th, name):
            ns[name] = getattr(th, name)
    return ns


def run_doctor() -> int:
    root = _repo_root()
    print(f"topology-harness doctor  version={_version()}")
    print(f"  repo: {root}")
    print(f"  skill: {root / 'SKILL.md'}  exists={ (root / 'SKILL.md').is_file() }")
    print(f"  docs:  {root / 'docs'}  exists={ (root / 'docs').is_dir() }")

    ok = True
    try:
        import topology_harness as th

        print(f"  import topology_harness OK  file={th.__file__}")
    except Exception as exc:
        print(f"  import topology_harness FAIL: {exc}")
        ok = False

    try:
        import agent_topo_harness  # noqa: F401

        print("  import agent_topo_harness OK (deprecated shim)")
    except Exception as exc:
        print(f"  import agent_topo_harness FAIL: {exc}")
        # shim optional for doctor green if topology_harness works

    try:
        from topology_harness.cost_smoke import run_smoke

        figs = run_smoke()
        print(
            "  cost_smoke OK  "
            f"A={figs['cost_A_one_turn_one_retry']:.4f}  "
            f"B={figs['cost_B_one_turn_one_retry']:.4f}"
        )
    except Exception as exc:
        print(f"  cost_smoke FAIL: {exc}")
        ok = False

    cursor_rule = Path.home() / ".cursor" / "rules" / "topology-harness.mdc"
    cursor_skill = Path.home() / ".cursor" / "skills" / "topology-harness" / "SKILL.md"
    cursor_adapter = root / "docs" / "adapters" / "cursor.md"
    print(f"  cursor rule:  {cursor_rule}  exists={cursor_rule.is_file()}")
    print(f"  cursor skill: {cursor_skill}  exists={cursor_skill.is_file()}")
    print(f"  cursor adapter doc: {cursor_adapter}  exists={cursor_adapter.is_file()}")
    if cursor_rule.is_file():
        text = cursor_rule.read_text(encoding="utf-8")
        if "Cursor session is the Compound Topologies host" in text or (
            "Cursor binding" in text and "Task" in text
        ):
            print("  cursor rule: OK (Cursor chat = Main, Task = TO/TT)")
        else:
            print("  cursor rule: present (check docs/adapters/cursor.md for expected map)")
    bin_path = Path.home() / ".local" / "bin" / "topology-harness"
    print(f"  PATH bin:     {bin_path}  exists={bin_path.exists()}")

    if ok:
        print("doctor: OK")
        return 0
    print("doctor: FAIL")
    return 1


def _print_doctrine() -> None:
    print(DOCTRINE.strip())


def _print_compounds() -> None:
    from topology_harness import COMPOUNDS

    for cid, c in sorted(COMPOUNDS.items()):
        if isinstance(c, dict):
            intent = c.get("intent") or ""
            wiring = c.get("wiring") or []
            when = c.get("when") or ""
            print(f"{cid}")
            if intent:
                print(f"  intent: {intent}")
            if wiring:
                print(f"  wiring: {wiring}")
            if when:
                print(f"  when: {when}")
        else:
            print(f"{cid}: {c}")


def _sticky_session(session_id: str) -> int:
    from topology_harness import StickyRegistry, sticky_path_for_session

    home = os.environ.get("HERMES_HOME") or str(
        Path.home() / ".hermes/profiles/virgil-executor"
    )
    state = Path(home) / "state"
    path = sticky_path_for_session(state, session_id)
    print(f"sticky path: {path}")
    if not path.is_file():
        print("(missing — empty registry)")
        return 1
    reg = StickyRegistry.load(path)
    snap = reg.snapshot()
    import json

    print(json.dumps(snap, indent=2, default=str))
    return 0


def _run_code(source: str) -> int:
    ns = _helpers_ns()
    try:
        compiled = compile(source, "<topology-harness>", "exec")
        exec(compiled, ns, ns)  # noqa: S102 — intentional agent REPL
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else (0 if code is None else 1)
    except Exception:
        traceback.print_exc()
        return 1
    return 0


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] in {"-h", "--help"}:
        print(HELP)
        return
    if args and args[0] == "--version":
        print(_version())
        return
    if args and args[0] in {"--doctor", "doctor"}:
        raise SystemExit(run_doctor())
    if args and args[0] in {"doctrine", "card"}:
        _print_doctrine()
        return
    if args and args[0] in {"cursor-map", "cursor_map"}:
        print(CURSOR_MAP.strip())
        return
    if args and args[0] == "compounds":
        _print_compounds()
        return
    if args and args[0] in {"cost-smoke", "cost_smoke"}:
        from topology_harness.cost_smoke import main as smoke_main

        smoke_main()
        return
    if args and args[0] == "sticky":
        if len(args) < 2:
            print("usage: topology-harness sticky <session_id>", file=sys.stderr)
            raise SystemExit(2)
        raise SystemExit(_sticky_session(args[1]))

    if args:
        # Treat remaining args as a one-liner
        raise SystemExit(_run_code(" ".join(args)))

    if not sys.stdin.isatty():
        source = sys.stdin.read()
        if not source.strip():
            print(USAGE, file=sys.stderr)
            raise SystemExit(2)
        raise SystemExit(_run_code(source))

    print(HELP)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
