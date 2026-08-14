"""Pricing and synthetic A/B cost model for Compound Topologies.

Two synthetic rate sets:

1. **Uniform legacy** (``DEFAULT_RATES``): one Flash-class rate for every call —
   used only to reproduce the old A/B ratio. Masks role-tier savings.
2. **Role cast** (``ROLE_RATES_*``): Main / TO / scout / gen priced like
   ``config/models.yaml`` (3.1-flash-lite / 3-flash / 3.5-lite / 3.6). This is the
   fair monolith-vs-compound comparison after the cast.

Monolith arm (A) under the cast uses **3-flash** rates — one model does all work.
"""
from __future__ import annotations

from dataclasses import dataclass

# ── Synthetic cached Gemini (legacy uniform A/B smoke) ───────────────────────

# USD per 1M tokens — legacy uniform (3.6-class sticker)
P_IN_PER_M = 1.50
P_OUT_PER_M = 7.50
P_CACHE_PER_M = 0.15

P_IN = P_IN_PER_M / 1_000_000
P_OUT = P_OUT_PER_M / 1_000_000
P_CACHE = P_CACHE_PER_M / 1_000_000

# Role cast — Google/OR working rates used for fair A/B (USD / 1M)
RATE_3_FLASH = (0.50, 3.00, 0.05)          # TO / monolith baseline
RATE_3_6_FLASH = (1.50, 7.50, 0.15)        # gen / critiquer
RATE_3_5_FLASH_LITE = (0.30, 2.50, 0.03)   # scout
RATE_3_1_FLASH_LITE = (0.25, 1.50, 0.025)  # Main / cove
RATE_2_5_FLASH_LITE = (0.10, 0.40, 0.01)   # cheapest lite (ladder bottom)


@dataclass(frozen=True)
class SyntheticRates:
    p_in: float = P_IN
    p_out: float = P_OUT
    p_cache: float = P_CACHE


def rates_from_per_m(in_m: float, out_m: float, cache_m: float | None = None) -> SyntheticRates:
    """Build SyntheticRates from USD-per-1M prices."""
    cache = in_m * 0.10 if cache_m is None else cache_m
    return SyntheticRates(
        p_in=in_m / 1_000_000,
        p_out=out_m / 1_000_000,
        p_cache=cache / 1_000_000,
    )


DEFAULT_RATES = SyntheticRates()

# Fair cast rates (matches config/models.yaml roles)
MONOLITH_RATES = rates_from_per_m(*RATE_3_FLASH)  # one model does everything
MAIN_RATES = rates_from_per_m(*RATE_3_1_FLASH_LITE)
TO_RATES = rates_from_per_m(*RATE_3_FLASH)
SCOUT_RATES = rates_from_per_m(*RATE_3_5_FLASH_LITE)
GEN_RATES = rates_from_per_m(*RATE_3_6_FLASH)


@dataclass(frozen=True)
class RoleRateSheet:
    """Per-role prices for compound (B) under the current cast."""

    main: SyntheticRates = MAIN_RATES
    topic_owner: SyntheticRates = TO_RATES
    scout: SyntheticRates = SCOUT_RATES
    generator: SyntheticRates = GEN_RATES


CAST_RATES = RoleRateSheet()


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
    role_rates: RoleRateSheet | None = None,
) -> float:
    """Compound Topologies cost (B) — fair one user-turn + N_retries (default 1).

    One turn: Main routes once on C0; one TO brief; n_r thin scouts; optional
    Gen/Critiquer (``L`` extra critique rounds, default 0 → one Gen pass).
    Retry: Main re-route on cached C0 + one light worker pass (default priced
    as one scout-equivalent if ``W_fix_usd`` is None).
    ``T_A`` is accepted for API symmetry and ignored.

    When ``role_rates`` is set, Main / TO / scout / gen use that sheet (cast A/B).
    Otherwise every call uses ``rates`` (legacy uniform).
    """
    del T_A
    sheet = role_rates
    r_main = sheet.main if sheet else rates
    r_to = sheet.topic_owner if sheet else rates
    r_scout = sheet.scout if sheet else rates
    r_gen = sheet.generator if sheet else rates

    main_hist = _usd(C0, r_main.p_in) + _usd(max(T_m - 1, 0) * C0, r_main.p_cache)
    main = (
        main_hist
        + _usd(T_m * (S + P), r_main.p_in)
        + _usd(T_m * U, r_main.p_out)
    )

    to_in = T_o * (S + P_o) + T_o * (R_sum + K_sum) / 2
    to = _usd(to_in, r_to.p_in) + _usd(T_o * U, r_to.p_out)

    per_scout_in = T_r * (S + P_r) + T_r * (R / max(n_r, 1)) / 2
    res = n_r * (_usd(per_scout_in, r_scout.p_in) + _usd(T_r * U, r_scout.p_out))

    code_rounds = 1 + L
    code_in = code_rounds * T_g * (S + P_c + K)
    code = _usd(code_in, r_gen.p_in) + _usd(code_rounds * T_g * U, r_gen.p_out)

    kg = 0.0
    if P_kg:
        kg = _usd(S + P_kg, r_to.p_in) + _usd(U, r_to.p_out)

    first = main + to + res + code + kg

    if W_fix_usd is None:
        W_fix_usd = (
            _usd(S + P_r + R / max(n_r, 1) / 2, r_scout.p_in)
            + _usd(U, r_scout.p_out)
        )

    retry_main = N_retries * (
        _usd(T_m_fix * C0, r_main.p_cache)
        + _usd(T_m_fix * (S + P), r_main.p_in)
        + _usd(T_m_fix * U, r_main.p_out)
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
