"""Synthetic A vs B cost figures for Compound Topologies.

Fair baseline: one user-turn of heavy work + one retry for BOTH arms.

* **legacy_uniform** — every call at $1.50/$7.50
* **cast_tiered** — monolith A at 3-flash; B uses Main 3.1-flash-lite /
  TO 3-flash / scout 3.5-lite / gen 3.6

Hard asserts live in ``tests/``; this module computes + prints for CLI/doctor.

  topology-harness cost-smoke
"""
from __future__ import annotations

from .cost import (
    CAST_RATES,
    MONOLITH_RATES,
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
    """Compute synthetic A/B figures (no asserts — tests own pass/fail)."""
    a_legacy = cost_A(FAT_C0, T_A=1, N_retries=1)
    b_legacy = cost_B(FAT_C0, T_A=1, N_retries=1)

    a_cast = cost_A(FAT_C0, T_A=1, N_retries=1, rates=MONOLITH_RATES)
    b_cast = cost_B(FAT_C0, T_A=1, N_retries=1, role_rates=CAST_RATES)

    trivial_main = cost_trivial_main_only()
    trivial_forced_to = cost_forced_topic_owner_trivial()

    def _pct(a: float, b: float) -> float:
        return 0.0 if a == 0 else 100.0 * (b - a) / a

    return {
        "cost_A_one_turn_one_retry": a_legacy,
        "cost_B_one_turn_one_retry": b_legacy,
        "legacy_B_vs_A_pct": _pct(a_legacy, b_legacy),
        "cost_A_cast_monolith_3flash": a_cast,
        "cost_B_cast_tiered": b_cast,
        "cast_B_vs_A_pct": _pct(a_cast, b_cast),
        "trivial_main": trivial_main,
        "trivial_forced_to": trivial_forced_to,
        "p_in": P_IN_PER_M,
        "p_out": P_OUT_PER_M,
        "p_cache": P_CACHE_PER_M,
    }


def main() -> None:
    figures = run_smoke()
    print("topology-harness cost_smoke")
    print(
        f"  legacy_uniform  A={figures['cost_A_one_turn_one_retry']:.6f}  "
        f"B={figures['cost_B_one_turn_one_retry']:.6f}  "
        f"B_vs_A={figures['legacy_B_vs_A_pct']:+.1f}%"
    )
    print(
        f"  cast_tiered     A={figures['cost_A_cast_monolith_3flash']:.6f}  "
        f"B={figures['cost_B_cast_tiered']:.6f}  "
        f"B_vs_A={figures['cast_B_vs_A_pct']:+.1f}%"
    )
    print(f"  trivial_main={figures['trivial_main']:.6f}")
    print(f"  trivial_forced_to={figures['trivial_forced_to']:.6f}")


if __name__ == "__main__":
    main()
