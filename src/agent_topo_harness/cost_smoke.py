"""Synthetic A vs B cost smoke asserts for Compound Topologies.

Run from the harness checkout:

  uv run python -m agent_topo_harness.cost_smoke

Virgil thin wrapper (optional): ``python scripts/agent_topo_cost_smoke.py``.
"""
from __future__ import annotations

from .cost import (
    P_CACHE_PER_M,
    P_IN_PER_M,
    P_OUT_PER_M,
    cost_A,
    cost_B,
    cost_forced_topic_owner_trivial,
    cost_trivial_main_only,
)

FAT_C0 = 200_000


def run_smoke() -> dict[str, float]:
    """Run synthetic asserts; raise AssertionError on failure. Return key figures."""
    a_fat = cost_A(FAT_C0, T_A=20, N_retries=4)
    b_fat = cost_B(FAT_C0, N_retries=1)
    assert b_fat < a_fat, (
        f"fat C0={FAT_C0}: expected cost_B < cost_A, got B={b_fat:.4f} A={a_fat:.4f}"
    )

    trivial_main = cost_trivial_main_only()
    trivial_forced_to = cost_forced_topic_owner_trivial()
    assert trivial_main < trivial_forced_to, (
        "trivial: expected main-only cheaper than forced TO path, "
        f"got main={trivial_main:.4f} forced_to={trivial_forced_to:.4f}"
    )

    return {
        "p_in_per_m": P_IN_PER_M,
        "p_out_per_m": P_OUT_PER_M,
        "p_cache_per_m": P_CACHE_PER_M,
        "cost_A_fat": a_fat,
        "cost_B_fat": b_fat,
        "ratio_A_over_B": a_fat / b_fat if b_fat else float("inf"),
        "trivial_main": trivial_main,
        "trivial_forced_to": trivial_forced_to,
    }


def main() -> None:
    figures = run_smoke()
    print("agent-topo-harness cost smoke OK")
    print(
        f"  synthetic Gemini rates: "
        f"p_in=${figures['p_in_per_m']}/1M  "
        f"p_out=${figures['p_out_per_m']}/1M  "
        f"p_cache=${figures['p_cache_per_m']}/1M"
    )
    print(
        f"  fat C0={FAT_C0}: "
        f"A=${figures['cost_A_fat']:.4f}  B=${figures['cost_B_fat']:.4f}  "
        f"(A/B={figures['ratio_A_over_B']:.2f}×)"
    )
    print(
        f"  trivial: main=${figures['trivial_main']:.4f}  "
        f"forced_TO=${figures['trivial_forced_to']:.4f}"
    )


if __name__ == "__main__":
    main()
