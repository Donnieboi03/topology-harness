"""Pricing, synthetic A/B cost model, and session-tree rollup.

Synthetic cached Gemini model (Standard paid tier, documented for smoke):
  p_in    = $1.50 / 1M tokens
  p_out   = $7.50 / 1M tokens
  p_cache = $0.15 / 1M tokens  (cached input reads)

Skill-matrix rates (Flash-only report defaults from cost-analysis.md) are kept
as ``SKILL_MATRIX_PRICING`` for live session rollups that prefer that table.
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ── Synthetic cached Gemini (A/B smoke) ──────────────────────────────────────

# USD per 1M tokens
P_IN_PER_M = 1.50
P_OUT_PER_M = 7.50
P_CACHE_PER_M = 0.15

P_IN = P_IN_PER_M / 1_000_000
P_OUT = P_OUT_PER_M / 1_000_000
P_CACHE = P_CACHE_PER_M / 1_000_000

# ── Skill matrix (default Flash-class estimates for synthetic smoke) ─────────

SKILL_MATRIX_PRICING: dict[str, dict[str, float]] = {
    "gemini-3.5-flash": {
        "in": 0.075 / 1_000_000,
        "out": 0.30 / 1_000_000,
    },
    "gemini-3-flash-preview": {
        "in": 0.075 / 1_000_000,
        "out": 0.30 / 1_000_000,
    },
    "gemini-2.5-flash": {
        "in": 0.10 / 1_000_000,
        "out": 0.40 / 1_000_000,
    },
    "default": {
        "in": 0.10 / 1_000_000,
        "out": 0.40 / 1_000_000,
    },
}

# Back-compat alias used by session_cost wrapper
PRICING = SKILL_MATRIX_PRICING


@dataclass(frozen=True)
class SyntheticRates:
    p_in: float = P_IN
    p_out: float = P_OUT
    p_cache: float = P_CACHE


DEFAULT_RATES = SyntheticRates()


def _usd(tokens: float, price_per_token: float) -> float:
    return float(tokens) * price_per_token


def cost_A(
    C0: float,
    T_A: float = 1,
    N_retries: float = 1,
    *,
    S: float = 2_000,
    P: float = 500,
    R: float = 40_000,
    K: float = 8_000,
    U: float = 800,
    D: float = 2_000,
    T_fix: float = 1,
    n_bar: float = 6_000,
    rates: SyntheticRates = DEFAULT_RATES,
) -> float:
    """Monolithic Main cost (A) — fair one user-turn + N_retries (default 1).

    One turn: pay C0 once (cache write) + non-history input (skills/prompt/retrieval)
    + output. Each retry: re-read C0(+growth) at cache rate + one fix pass on Main.
    ``T_A`` is number of *work* turns on fat Main for the first pass (default 1).
    """
    p_in, p_out, p_c = rates.p_in, rates.p_out, rates.p_cache

    hist = _usd(C0, p_in) + _usd(max(T_A - 1, 0) * C0, p_c)
    new_in_per_turn = S + P + (R + K) / 2
    first = hist + _usd(T_A * new_in_per_turn, p_in) + _usd(T_A * U, p_out)

    retry_total = 0.0
    for k in range(int(N_retries)):
        C = C0 + (k + 1) * D
        retry_total += (
            _usd(T_fix * C, p_c)
            + _usd(T_fix * (S + P + n_bar), p_in)
            + _usd(T_fix * U, p_out)
        )
    return first + retry_total


def cost_B(
    C0: float,
    T_A: float = 1,  # unused; kept for call-signature symmetry with cost_A
    N_retries: float = 1,
    *,
    T_m: float = 1,
    T_o: float = 1,
    S: float = 2_000,
    P: float = 500,
    P_o: float = 1_500,
    R: float = 40_000,
    R_sum: float = 4_000,
    K: float = 8_000,
    K_sum: float = 1_000,
    U: float = 800,
    n_r: float = 3,
    T_r: float = 1,
    P_r: float = 800,
    L: float = 0,
    T_g: float = 1,
    P_c: float = 1_000,
    P_kg: float = 0,
    T_m_fix: float = 1,
    W_fix_usd: float | None = None,
    rates: SyntheticRates = DEFAULT_RATES,
) -> float:
    """Compound Topologies cost (B) — fair one user-turn + N_retries (default 1).

    One turn: Main routes once on C0; one TO brief; n_r thin scouts; optional
    Gen/Critiquer (``L`` extra critique rounds, default 0 → one Gen pass).
    Retry: Main re-route on cached C0 + one light worker pass (default priced
    as one scout-equivalent if ``W_fix_usd`` is None).
    ``T_A`` is accepted for API symmetry and ignored.
    """
    del T_A
    p_in, p_out, p_c = rates.p_in, rates.p_out, rates.p_cache

    main_hist = _usd(C0, p_in) + _usd(max(T_m - 1, 0) * C0, p_c)
    main = (
        main_hist
        + _usd(T_m * (S + P), p_in)
        + _usd(T_m * U, p_out)
    )

    to_in = T_o * (S + P_o) + T_o * (R_sum + K_sum) / 2
    to = _usd(to_in, p_in) + _usd(T_o * U, p_out)

    per_scout_in = T_r * (S + P_r) + T_r * (R / max(n_r, 1)) / 2
    res = n_r * (_usd(per_scout_in, p_in) + _usd(T_r * U, p_out))

    code_rounds = 1 + L
    code_in = code_rounds * T_g * (S + P_c + K)
    code = _usd(code_in, p_in) + _usd(code_rounds * T_g * U, p_out)

    kg = 0.0
    if P_kg:
        kg = _usd(S + P_kg, p_in) + _usd(U, p_out)

    first = main + to + res + code + kg

    if W_fix_usd is None:
        W_fix_usd = _usd(S + P_r + R / max(n_r, 1) / 2, p_in) + _usd(U, p_out)

    retry_main = N_retries * (
        _usd(T_m_fix * C0, p_c)
        + _usd(T_m_fix * (S + P), p_in)
        + _usd(T_m_fix * U, p_out)
    )
    retry_workers = N_retries * W_fix_usd
    return first + retry_main + retry_workers


def cost_trivial_main_only(
    *,
    C0: float = 2_000,
    T: float = 2,
    S: float = 2_000,
    P: float = 200,
    U: float = 400,
    rates: SyntheticRates = DEFAULT_RATES,
) -> float:
    """Cheap Main-in-chat path for a trivial job (no TO)."""
    p_in, p_out, p_c = rates.p_in, rates.p_out, rates.p_cache
    hist = _usd(C0, p_in) + _usd(max(T - 1, 0) * C0, p_c)
    return hist + _usd(T * (S + P), p_in) + _usd(T * U, p_out)


def cost_forced_topic_owner_trivial(
    *,
    C0: float = 2_000,
    T_m: float = 2,
    T_o: float = 4,
    S: float = 2_000,
    P: float = 200,
    P_o: float = 800,
    U: float = 400,
    rates: SyntheticRates = DEFAULT_RATES,
) -> float:
    """Same trivial job forced through Main → TO overhead (should be more expensive)."""
    p_in, p_out, p_c = rates.p_in, rates.p_out, rates.p_cache
    main = (
        _usd(C0, p_in)
        + _usd(max(T_m - 1, 0) * C0, p_c)
        + _usd(T_m * (S + P), p_in)
        + _usd(T_m * U, p_out)
    )
    to = _usd(T_o * (S + P_o), p_in) + _usd(T_o * U, p_out)
    return main + to


# ── Live session tree rollup (from scripts/graph_analysis/session_cost.py) ───


def get_db_path() -> Path:
    """Resolve host session DB for tree rollups.

    Set ``AGENT_TOPO_STATE_DB`` (or legacy ``VIRGIL_HERMES_STATE_DB``) to the
    host's SQLite path. No default home path is baked into the package.
    """
    override = (
        os.environ.get("AGENT_TOPO_STATE_DB")
        or os.environ.get("VIRGIL_HERMES_STATE_DB")
        or os.environ.get("HOST_SESSION_DB")
    )
    if override:
        return Path(override)
    raise FileNotFoundError(
        "Set AGENT_TOPO_STATE_DB to your host session database path "
        "(no default path is shipped in topology-harness)."
    )


def analyze_session_tree(
    parent_id: str,
    *,
    db_path: Path | str | None = None,
    pricing: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    """Recursively roll up token/cost from a parent session id in a host DB."""
    try:
        path = Path(db_path) if db_path is not None else get_db_path()
    except FileNotFoundError as exc:
        return {"error": str(exc)}
    price_table = pricing or SKILL_MATRIX_PRICING

    if not path.exists():
        return {"error": f"DB not found: {path}"}

    conn = sqlite3.connect(str(path))
    cursor = conn.cursor()

    all_sessions: list[dict[str, Any]] = []
    to_process = [parent_id]
    processed: set[str] = set()

    while to_process:
        current_id = to_process.pop(0)
        if current_id in processed:
            continue
        processed.add(current_id)

        cursor.execute(
            "SELECT id, model, input_tokens, output_tokens, estimated_cost_usd, "
            "parent_session_id FROM sessions WHERE id = ? OR parent_session_id = ?",
            (current_id, current_id),
        )
        rows = cursor.fetchall()
        for row in rows:
            sid, model, it, ot, cost, pid = row
            if any(s["id"] == sid for s in all_sessions):
                continue
            if not cost or cost == 0:
                p = price_table.get(model, price_table["default"])
                it_n = it or 0
                ot_n = ot or 0
                cost = (it_n * p["in"]) + (ot_n * p["out"])

            all_sessions.append(
                {
                    "id": sid,
                    "model": model,
                    "input": it or 0,
                    "output": ot or 0,
                    "cost": cost,
                    "parent": pid,
                }
            )
            if sid not in processed:
                to_process.append(sid)

    conn.close()

    total_cost = sum(s["cost"] for s in all_sessions)
    total_in = sum(s["input"] for s in all_sessions)
    total_out = sum(s["output"] for s in all_sessions)

    return {
        "parent_id": parent_id,
        "total_cost": total_cost,
        "total_tokens": {"input": total_in, "output": total_out},
        "agent_count": len(all_sessions),
        "breakdown": all_sessions,
    }


# Alias matching the historical script name
analyze_graph = analyze_session_tree
