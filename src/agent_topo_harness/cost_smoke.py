"""Synthetic A vs B cost smoke asserts for Compound Topologies.

Fair baseline: one user-turn of heavy work + one retry for BOTH arms.

Run from the harness checkout:

  uv run python -m agent_topo_harness.cost_smoke
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
    """Run synthetic asserts; raise AssertionError on failure. Return key figures.

    One-turn + one-retry is *not* asserted as B < A. Fair one-shot often has
    A ≤ B; isolation value shows when Main stays fat but work spans topics /
    many work rounds.
    """
    a_one = cost_A(FAT_C0, T_A=1, N_retries=1)
    b_one = cost_B(FAT_C0, T_A=1, N_retries=1)

    trivial_main = cost_trivial_main_only()
    trivial_forced_to = cost_forced_topic_owner_trivial()
    assert trivial_main < trivial_forced_to, (
        "trivial: expected main-only cheaper than forced TO path, "
        f"got main={trivial_main:.4f} forced_orch={trivial_forced_to:.4f}"
    )

    return {
        "cost_A_one_turn_one_retry": a_one,
        "cost_B_one_turn_one_retry": b_one,
        "trivial_main": trivial_main,
        "trivial_forced_to": trivial_forced_to,
        "p_in": P_IN_PER_M,
        "p_out": P_OUT_PER_M,
        "p_cache": P_CACHE_PER_M,
    }


def main() -> None:
    figures = run_smoke()
    print("agent-topo-harness cost_smoke OK")
    for k, v in figures.items():
        if isinstance(v, float):
            print(f"  {k}={v:.6f}")
        else:
            print(f"  {k}={v}")


if __name__ == "__main__":
    main()
