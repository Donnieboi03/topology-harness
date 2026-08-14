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
- Sticky is ephemeral (24h TO-touch idle TTL / session-end release) — not a KG archive
- Main card: topics_for_main(limit=1); coerce uses live open_topics after purge_idle
- Main→leaf blocked for sticky-open / substantive / atomic work (assert_spawn_policy)
- Public menu — atoms ONLY: swarm | plane | cove | shard (NotAtomicError otherwise)
- Public combinator: cycle only; public transition: revise only
- Prefer named compounds (five recipes; topology-harness compounds)
- Durable writes: assert_can_write — TO only (Main/TT blocked); retire ≠ release
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
Sticky is ephemeral (purge_idle 24h / release_all on session end); Main sees topics_for_main(1)
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
    """Checkout root when developing; package dir when installed from a wheel."""
    from topology_harness.models import harness_root

    return harness_root()


def _helpers_ns() -> dict[str, Any]:
    """Namespace for REPL — public API + common submodules."""
    import topology_harness as th
    from topology_harness import (  # noqa: F401
        ATOMIC_PARADIGMS,
        COMBINATORS,
        COMPOUNDS,
        ROUTER_SYSTEM_PROMPT,
        TRANSITIONS,
        StickyRegistry,
        TT_STUB_INSTRUCTION,
        assert_can_write,
        assert_combinator,
        assert_spawn_policy,
        assert_topic_open,
        assert_transition,
        coerce_route_with_registry,
        make_topology_urn,
        parse_route_decision,
        parse_tt_stub,
        resolve_legacy_pattern,
        topo_gate,
    )

    ns: dict[str, Any] = {
        "th": th,
        "topology_harness": th,
        "ATOMIC_PARADIGMS": ATOMIC_PARADIGMS,
        "COMBINATORS": COMBINATORS,
        "TRANSITIONS": TRANSITIONS,
        "assert_combinator": assert_combinator,
        "assert_transition": assert_transition,
        "resolve_legacy_pattern": resolve_legacy_pattern,
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
    checkout = (root / "SKILL.md").is_file()
    print(f"topology-harness doctor  version={_version()}")
    print(f"  root: {root}  mode={'checkout' if checkout else 'installed'}")
    if checkout:
        print(f"  skill: {root / 'SKILL.md'}  exists=True")
        print(f"  docs:  {root / 'docs'}  exists={(root / 'docs').is_dir()}")
    else:
        print("  skill/docs: (not required for installed wheel)")

    ok = True
    try:
        import topology_harness as th

        print(f"  import topology_harness OK  file={th.__file__}")
    except Exception as exc:
        print(f"  import topology_harness FAIL: {exc}")
        ok = False

    try:
        from topology_harness.blackboard import Blackboard, REGIONS, retire_topic

        _ = Blackboard, retire_topic
        print(f"  blackboard OK  regions={','.join(REGIONS)}")
    except Exception as exc:
        print(f"  blackboard FAIL: {exc}")
        ok = False

    try:
        import hashlib

        from topology_harness.models import config_path, load_models_config

        cfg = config_path()
        load_models_config(cfg)
        digest = hashlib.sha256(cfg.read_bytes()).hexdigest()[:12]
        print(f"  models.yaml OK  path={cfg}  sha256={digest}")
    except Exception as exc:
        print(f"  models.yaml FAIL: {exc}")
        ok = False

    try:
        from topology_harness.sticky import (
            STICKY_HANDLE_KINDS,
            STICKY_PERSIST_KEYS,
            StickyRegistry,
        )

        _ = StickyRegistry
        print(
            "  sticky schema OK  "
            f"kinds={list(STICKY_HANDLE_KINDS)}  "
            f"persist_keys={list(STICKY_PERSIST_KEYS)}"
        )
    except Exception as exc:
        print(f"  sticky schema FAIL: {exc}")
        ok = False

    try:
        from topology_harness.cost_smoke import run_smoke

        figs = run_smoke()
        print(
            "  cost_smoke OK  "
            f"legacy A={figs['cost_A_one_turn_one_retry']:.4f} "
            f"B={figs['cost_B_one_turn_one_retry']:.4f} "
            f"({figs['legacy_B_vs_A_pct']:+.1f}%)  |  "
            f"cast A={figs['cost_A_cast_monolith_3flash']:.4f} "
            f"B={figs['cost_B_cast_tiered']:.4f} "
            f"({figs['cast_B_vs_A_pct']:+.1f}%)"
        )
    except Exception as exc:
        print(f"  cost_smoke FAIL: {exc}")
        ok = False

    cursor_rule = Path.home() / ".cursor" / "rules" / "topology-harness.mdc"
    cursor_skill = Path.home() / ".cursor" / "skills" / "topology-harness" / "SKILL.md"
    # Adapter doc lives in checkout docs/; optional when installed from wheel.
    cursor_adapter = root / "docs" / "adapters" / "cursor.md"
    print(f"  cursor rule:  {cursor_rule}  exists={cursor_rule.is_file()}")
    print(f"  cursor skill: {cursor_skill}  exists={cursor_skill.is_file()}")
    if checkout:
        print(
            f"  cursor adapter doc: {cursor_adapter}  "
            f"exists={cursor_adapter.is_file()}"
        )
    else:
        print("  cursor adapter doc: (checkout-only; see package README)")
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
    from topology_harness import COMPOUNDS, render_node

    for cid, c in sorted(COMPOUNDS.items()):
        if isinstance(c, dict):
            intent = c.get("intent") or ""
            wiring = [render_node(n) for n in c.get("wiring") or []]
            optional = [render_node(n) for n in c.get("optional") or []]
            when = c.get("when") or ""
            print(f"{cid}")
            if intent:
                print(f"  intent: {intent}")
            if wiring:
                print(f"  wiring: {' -> '.join(wiring)}")
            if optional:
                print(f"  optional: {' -> '.join(optional)}")
            if when:
                print(f"  when: {when}")
        else:
            print(f"{cid}: {c}")


def _sticky_session(session_id: str) -> int:
    from topology_harness import StickyRegistry, sticky_path_for_session

    home = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
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
