"""Unit tests for synthetic cost smoke (no live network)."""
from __future__ import annotations

from topology_harness.cost import CAST_RATES, MONOLITH_RATES, cost_A, cost_B
from topology_harness.cost_smoke import FAT_C0, run_smoke


def test_cost_smoke_figures() -> None:
    figures = run_smoke()
    assert figures["trivial_main"] < figures["trivial_forced_to"]
    assert figures["cost_A_one_turn_one_retry"] > 0
    assert figures["cost_B_one_turn_one_retry"] > 0
    assert figures["cost_A_cast_monolith_3flash"] > 0
    assert figures["cost_B_cast_tiered"] > 0
    assert figures["cast_B_vs_A_pct"] < figures["legacy_B_vs_A_pct"]


def test_fair_one_turn_one_retry_defaults() -> None:
    a = cost_A(FAT_C0, T_A=1, N_retries=1)
    b = cost_B(FAT_C0, T_A=1, N_retries=1)
    assert a > 0 and b > 0


def test_cast_tiered_vs_monolith() -> None:
    a = cost_A(FAT_C0, T_A=1, N_retries=1, rates=MONOLITH_RATES)
    b = cost_B(FAT_C0, T_A=1, N_retries=1, role_rates=CAST_RATES)
    assert a > 0 and b > 0
    assert b <= a * 1.05
