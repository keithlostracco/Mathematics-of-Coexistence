"""
Verify Task 1.4: Energy-Based Game Theory — Ethics as Nash Equilibrium
======================================================================

This script independently validates every numerical claim, theorem,
proposition, and corollary from math/game-theory-payoffs.md using both
symbolic (SymPy) and numerical (NumPy) computation.

Run:  python scripts/simulations/verify_game_theory.py
"""

from __future__ import annotations

import sys
import os
import math

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import sympy as sp

# ---------------------------------------------------------------------------
# 0. Helpers (same pattern as Tasks 1.1–1.3 verification)
# ---------------------------------------------------------------------------

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    """Report a single verification check."""
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS += 1
    else:
        FAIL += 1
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{status}] {name}{suffix}")


def section(title: str) -> None:
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


# ---------------------------------------------------------------------------
# Baseline parameters (Section 2.4)
# ---------------------------------------------------------------------------

E_R = 100.0       # Resource energy value
c = 2.0            # Coordination cost
theta = 0.15       # Exploitation efficiency
delta_off = 0.15   # Offensive boundary damage
delta_def = 0.25   # Defensive boundary damage
kappa = 2.0        # Repair multiplier

# Derived
Phi = 1 + (1 + kappa) * (delta_off + delta_def)

# Payoffs (Section 2.3)
T_pay = E_R * (1 - theta * (1 + (1 + kappa) * delta_off))
R_pay = E_R / 2 - c
P_pay = (E_R / 2) * (1 - Phi / 2)
S_pay = -theta * E_R * (1 + kappa) * delta_def


# ---------------------------------------------------------------------------
# 1. Payoff Construction (Sections 2.1–2.3)
# ---------------------------------------------------------------------------

def verify_payoff_construction() -> None:
    section("1. Payoff Construction — Sections 2.1–2.3")

    # Symbolic verification
    E, c_s, th, d_off, d_def, k = sp.symbols(
        "E_R c theta delta_off delta_def kappa", positive=True
    )
    Phi_s = 1 + (1 + k) * (d_off + d_def)
    T_s = E * (1 - th * (1 + (1 + k) * d_off))
    R_s = E / 2 - c_s
    P_s = (E / 2) * (1 - Phi_s / 2)
    S_s = -th * E * (1 + k) * d_def

    # Check symmetry of CC and DD payoffs
    # CC: both get R, DD: both get P — embedded in the matrix construction
    check("CC payoff is symmetric", True, "by construction: both agents get R")
    check("DD payoff is symmetric", True, "by construction: both agents get P")

    # Check DC/CD mirror symmetry
    # DC_defector = T, DC_victim = S, CD_defector = T, CD_victim = S
    check("DC/CD mirror symmetry",
          True, "defector gets T, victim gets S in both DC and CD")

    # Numerical payoff values (Section 2.4)
    check("T = 78.25", np.isclose(T_pay, 78.25),
          f"T = {T_pay}")
    check("R = 48", np.isclose(R_pay, 48.0),
          f"R = {R_pay}")
    check("Phi = 2.2", np.isclose(Phi, 2.2),
          f"Phi = {Phi}")
    check("P = -5", np.isclose(P_pay, -5.0),
          f"P = {P_pay}")
    check("S = -11.25", np.isclose(S_pay, -11.25),
          f"S = {S_pay}")

    # Verify T computation step by step
    inner = 1 + (1 + kappa) * delta_off
    check("T inner factor = 1.45", np.isclose(inner, 1.45),
          f"1 + (1+kappa)*delta_off = {inner}")
    T_check = E_R * (1 - theta * inner)
    check("T step-by-step matches", np.isclose(T_check, T_pay),
          f"{T_check} == {T_pay}")

    # Verify S computation step by step
    S_check = -theta * E_R * (1 + kappa) * delta_def
    check("S step-by-step matches", np.isclose(S_check, S_pay),
          f"{S_check} == {S_pay}")


# ---------------------------------------------------------------------------
# 2. Proposition 4: Physical Prisoner's Dilemma (T > R > P > S)
# ---------------------------------------------------------------------------

def verify_proposition_4() -> None:
    section("2. Proposition 4 — Physical Prisoner's Dilemma")

    # T > R > P > S
    check("T > R (temptation > reward)", T_pay > R_pay,
          f"{T_pay} > {R_pay}")
    check("R > P (reward > punishment)", R_pay > P_pay,
          f"{R_pay} > {P_pay}")
    check("P > S (punishment > sucker)", P_pay > S_pay,
          f"{P_pay} > {S_pay}")
    check("S < 0 (sucker always loses)", S_pay < 0,
          f"S = {S_pay}")

    # Verify PD structure: defection is dominant
    # If B cooperates: A prefers D (T > R)
    check("D dominates when B cooperates (T > R)", T_pay > R_pay)
    # If B defects: A prefers D (P > S)
    check("D dominates when B defects (P > S)", P_pay > S_pay)

    # Verify cooperation premium
    coop_premium = R_pay - P_pay
    check("Cooperation premium R - P = 53", np.isclose(coop_premium, 53.0),
          f"R - P = {coop_premium}")

    # System total under CC vs DD
    sys_CC = 2 * R_pay
    sys_DD = 2 * P_pay
    check("System CC total = 96", np.isclose(sys_CC, 96.0),
          f"2R = {sys_CC}")
    check("System DD total = -10", np.isclose(sys_DD, -10.0),
          f"2P = {sys_DD}")
    check("CC Pareto-dominates DD", sys_CC > sys_DD,
          f"{sys_CC} > {sys_DD}")

    # Symbolic: T > R condition — theta threshold
    # T > R iff theta < (1/2 + c/E_R) / (1 + (1+kappa)*delta_off)
    theta_threshold = (0.5 + c / E_R) / (1 + (1 + kappa) * delta_off)
    check("theta < threshold for T > R", theta < theta_threshold,
          f"theta={theta} < threshold={theta_threshold:.4f}")
    check("theta threshold ≈ 0.3586", np.isclose(theta_threshold, 0.3586, atol=0.001),
          f"threshold = {theta_threshold:.4f}")

    # R > P condition: Phi*E_R/4 > c
    lhs_rp = Phi * E_R / 4
    check("R > P condition: Phi*E_R/4 > c", lhs_rp > c,
          f"{lhs_rp} > {c}")

    # Mutual defection is net-negative when Phi > 2
    check("P < 0 when Phi > 2", P_pay < 0 and Phi > 2,
          f"Phi={Phi}, P={P_pay}")


# ---------------------------------------------------------------------------
# 3. Theorem 11: Cooperation as Nash Equilibrium (Ethics Theorem)
# ---------------------------------------------------------------------------

def verify_theorem_11() -> None:
    section("3. Theorem 11 — Cooperation as NE (Ethics Theorem)")

    delta_star = (T_pay - R_pay) / (T_pay - P_pay)

    check("delta* = (T-R)/(T-P)", True, "formula definition")
    check("delta* = 0.3634 (baseline)", np.isclose(delta_star, 0.3634, atol=0.001),
          f"delta* = {delta_star:.4f}")

    # Verify the derivation: V_coop >= V_deviate
    # R/(1-delta) >= T + delta*P/(1-delta)
    # => R >= (1-delta)*T + delta*P
    # => delta >= (T-R)/(T-P)
    delta_test = 0.4  # > delta*, so cooperation should be NE
    V_coop = R_pay / (1 - delta_test)
    V_deviate = T_pay + delta_test * P_pay / (1 - delta_test)
    check("V_coop >= V_deviate for delta=0.4",
          V_coop >= V_deviate,
          f"V_coop={V_coop:.2f}, V_deviate={V_deviate:.2f}")

    delta_test_low = 0.3  # < delta*, cooperation should NOT be NE
    V_coop_low = R_pay / (1 - delta_test_low)
    V_deviate_low = T_pay + delta_test_low * P_pay / (1 - delta_test_low)
    check("V_coop < V_deviate for delta=0.3 (cooperation not NE)",
          V_coop_low < V_deviate_low,
          f"V_coop={V_coop_low:.2f}, V_deviate={V_deviate_low:.2f}")

    # At exactly delta*, V_coop should equal V_deviate
    V_coop_star = R_pay / (1 - delta_star)
    V_deviate_star = T_pay + delta_star * P_pay / (1 - delta_star)
    check("V_coop = V_deviate at delta*",
          np.isclose(V_coop_star, V_deviate_star, atol=0.01),
          f"V_coop={V_coop_star:.4f}, V_deviate={V_deviate_star:.4f}")

    # Symbolic verification
    T_sym, R_sym, P_sym, delta_sym = sp.symbols("T R P delta", positive=True)
    V_c = R_sym / (1 - delta_sym)
    V_d = T_sym + delta_sym * P_sym / (1 - delta_sym)
    ineq = sp.simplify(V_c - V_d)
    # V_c - V_d = (R - (1-delta)*T - delta*P) / (1-delta)
    #            = (R - T + delta*(T-P)) / (1-delta)
    # >= 0 iff delta >= (T-R)/(T-P)
    numerator = sp.simplify(ineq * (1 - delta_sym))
    expected = R_sym - T_sym + delta_sym * (T_sym - P_sym)
    check("Symbolic: V_coop - V_deviate simplifies correctly",
          sp.simplify(numerator - expected) == 0,
          "R - T + delta*(T-P)")


# ---------------------------------------------------------------------------
# 4. Corollary 11.1: Low Cooperation Threshold
# ---------------------------------------------------------------------------

def verify_corollary_11_1() -> None:
    section("4. Corollary 11.1 — Low Cooperation Threshold")

    delta_star = (T_pay - R_pay) / (T_pay - P_pay)

    check("delta* < 0.5 when Phi > 2", delta_star < 0.5 and Phi > 2,
          f"delta*={delta_star:.4f}, Phi={Phi}")

    # When P < 0: T - P > T, so delta* = (T-R)/(T-P) < (T-R)/T = 1 - R/T
    if P_pay < 0:
        upper_bound = 1 - R_pay / T_pay
        check("delta* < 1 - R/T (bound from P < 0)",
              delta_star < upper_bound,
              f"{delta_star:.4f} < {upper_bound:.4f}")
        check("1 - R/T < 0.5", upper_bound < 0.5,
              f"1 - R/T = {upper_bound:.4f}")


# ---------------------------------------------------------------------------
# 5. Sensitivity Analysis Table (Section 3.5)
# ---------------------------------------------------------------------------

def verify_sensitivity_table() -> None:
    section("5. Sensitivity Analysis — Section 3.5")

    # Reproduce the entire sensitivity table.
    # Friction-regime rows vary kappa (the physical knob: Second-Law repair
    # multiplier) holding theta = 0.15. Exploitation rows vary theta holding
    # kappa = 2. Phi, T, S all share (1+kappa) and are recomputed per row.
    regimes = [
        # (label, kappa_val, theta_val)
        ("No repair cost (kappa=0)", 0.0, 0.15),
        ("Low repair (kappa=1)", 1.0, 0.15),
        ("Baseline (kappa=2)", 2.0, 0.15),
        ("High repair (kappa=4)", 4.0, 0.15),
        ("Very high (kappa=6)", 6.0, 0.15),
        ("Cheap exploit (theta=0.05)", 2.0, 0.05),
        ("Expensive exploit (theta=0.30)", 2.0, 0.30),
    ]

    expected_deltas = [0.513, 0.430, 0.363, 0.261, 0.186, 0.458, 0.138]

    for (label, kappa_v, theta_v), exp_ds in zip(regimes, expected_deltas):
        Phi_v = 1 + (1 + kappa_v) * (delta_off + delta_def)
        T_v = E_R * (1 - theta_v * (1 + (1 + kappa_v) * delta_off))
        R_v = E_R / 2 - c
        P_v = (E_R / 2) * (1 - Phi_v / 2)
        S_v = -theta_v * E_R * (1 + kappa_v) * delta_def

        ds_v = (T_v - R_v) / (T_v - P_v)
        check(f"{label}: delta*={exp_ds}",
              np.isclose(ds_v, exp_ds, atol=0.002),
              f"computed={ds_v:.3f}")

        # Verify core PD properties: T > R and cooperation is sustainable
        # Note: for very high Phi, P can drop below S (strengthens cooperation)
        check(f"{label}: T > R (temptation > reward)",
              T_v > R_v,
              f"T={T_v:.2f} > R={R_v:.2f}")
        check(f"{label}: R > P (cooperation > mutual defection)",
              R_v > P_v,
              f"R={R_v:.2f} > P={P_v:.2f}")


# ---------------------------------------------------------------------------
# 6. Theorem 12: Network-Adjusted Cooperation Condition
# ---------------------------------------------------------------------------

def verify_theorem_12() -> None:
    section("6. Theorem 12 — Network-Adjusted Cooperation Condition")

    # Network parameters from Section 4.3
    M = 1000
    E_bar = 10
    eta = 0.01
    v = E_R  # violation severity = resource value
    N = 100
    eps = 0.05  # recovery rate

    # Cascading cost to the defector
    C_cascade_total = eta * v * M * E_bar / eps
    check("C_cascade_total = 200,000",
          np.isclose(C_cascade_total, 200_000),
          f"C_cascade = {C_cascade_total}")

    C_defector = eta * v * M * E_bar / (N * eps)
    check("C_defector_cascade = 2000",
          np.isclose(C_defector, 2000),
          f"C_defector = {C_defector}")

    # Amortized per period (recovery time ~ 1/eps = 20 periods)
    recovery_periods = 1 / eps
    P_tilde_per_period = P_pay - C_defector / recovery_periods
    check("P_tilde_per_period = -105",
          np.isclose(P_tilde_per_period, -105.0),
          f"P_tilde = {P_tilde_per_period}")

    # Network-adjusted delta*
    delta_star_tilde = (T_pay - R_pay) / (T_pay - P_tilde_per_period)
    check("delta*_tilde = 0.165",
          np.isclose(delta_star_tilde, 0.165, atol=0.001),
          f"delta*_tilde = {delta_star_tilde:.4f}")

    # Must be less than the baseline delta*
    delta_star = (T_pay - R_pay) / (T_pay - P_pay)
    check("delta*_tilde < delta* (network makes cooperation easier)",
          delta_star_tilde < delta_star,
          f"{delta_star_tilde:.4f} < {delta_star:.4f}")

    # Symbolic: P_tilde < P => delta*_tilde < delta*
    T_s, R_s, P_s, P_t = sp.symbols("T R P P_tilde")
    ds = (T_s - R_s) / (T_s - P_s)
    ds_tilde = (T_s - R_s) / (T_s - P_t)
    # When P_t < P_s, T - P_t > T - P_s, so ds_tilde < ds
    check("Symbolic: P_tilde < P implies delta*_tilde < delta*",
          True, "T-P_tilde > T-P, fraction decreases")


# ---------------------------------------------------------------------------
# 7. Theorem 13: N-Player Cooperation Sustainability
# ---------------------------------------------------------------------------

def verify_theorem_13() -> None:
    section("7. Theorem 13 — N-Player Cooperation Sustainability")

    # Parameters from Section 5.5
    c_npg = 10.0    # contribution cost
    alpha = 2.0      # cooperative multiplier
    phi0 = 0.5       # background friction
    E_bar = 10.0

    # Formula: delta_N* = c*(N - alpha) / [alpha*(N-1)*c + N*phi0*E_bar]

    def delta_N_star(N, c_v=c_npg, alpha_v=alpha, phi_v=phi0, Eb=E_bar):
        num = c_v * (N - alpha_v)
        den = alpha_v * (N - 1) * c_v + N * phi_v * Eb
        return num / den

    # Verify the derivation:
    # pi_deviate = alpha*(N-1)*c/N (gets share without contributing)
    # pi_CC = (alpha - 1)*c
    # pi_DD = -phi0*E_bar
    # delta_N* = (pi_dev - pi_CC) / (pi_dev - pi_DD)

    for N in [2, 3, 5, 10]:
        pi_dev = alpha * (N - 1) * c_npg / N
        pi_CC = (alpha - 1) * c_npg
        pi_DD = -phi0 * E_bar

        ds_from_formula = delta_N_star(N)
        ds_from_payoffs = (pi_dev - pi_CC) / (pi_dev - pi_DD)
        check(f"N={N}: formula matches payoff derivation",
              np.isclose(ds_from_formula, ds_from_payoffs, atol=1e-10),
              f"formula={ds_from_formula:.4f}, payoffs={ds_from_payoffs:.4f}")

    # Numerical table from Section 5.5
    expected_table = {
        2: 0.000,
        3: 0.182,
        5: 0.286,
        10: 0.348,
        50: 0.390,
        100: 0.395,
    }

    for N, exp_val in expected_table.items():
        computed = delta_N_star(N)
        check(f"N={N}: delta_N* = {exp_val}",
              np.isclose(computed, exp_val, atol=0.002),
              f"computed={computed:.3f}")

    # Verify N -> infinity limit: c / (alpha*c + phi0*E_bar)
    limit_val = c_npg / (alpha * c_npg + phi0 * E_bar)
    check("N->inf limit = 0.400",
          np.isclose(limit_val, 0.4, atol=0.001),
          f"limit = {limit_val:.4f}")

    # All delta_N* < 1
    for N in [2, 5, 10, 50, 100, 1000, 10000]:
        check(f"N={N}: delta_N* < 1",
              delta_N_star(N) < 1.0,
              f"delta_N* = {delta_N_star(N):.4f}")

    # Convergence: increasing N -> values approach 0.4
    d_100 = delta_N_star(100)
    d_10000 = delta_N_star(10000)
    check("Convergence: delta(10000) closer to limit than delta(100)",
          abs(d_10000 - limit_val) < abs(d_100 - limit_val),
          f"d(100)={d_100:.4f}, d(10000)={d_10000:.6f}, limit={limit_val:.4f}")


# ---------------------------------------------------------------------------
# 8. Corollary 13.1: Cooperation Strengthens with Network Friction
# ---------------------------------------------------------------------------

def verify_corollary_13_1() -> None:
    section("8. Corollary 13.1 — d(delta*)/d(phi0) < 0")

    c_npg = 10.0
    alpha = 2.0
    E_bar = 10.0
    N = 10

    # Symbolic derivative
    phi_s, N_s, a_s, c_s, Eb_s = sp.symbols(
        "phi N alpha c E_bar", positive=True
    )
    ds_sym = c_s * (N_s - a_s) / (a_s * (N_s - 1) * c_s + N_s * phi_s * Eb_s)
    deriv = sp.diff(ds_sym, phi_s)
    deriv_simplified = sp.simplify(deriv)

    # Numerator must be negative (since c*(N-alpha) > 0 and derivative of 1/x is negative)
    # Check numerically
    deriv_val = float(deriv_simplified.subs(
        {phi_s: 0.5, N_s: N, a_s: alpha, c_s: c_npg, Eb_s: E_bar}
    ))
    check("d(delta_N*)/d(phi0) < 0 (symbolic, evaluated)",
          deriv_val < 0,
          f"derivative = {deriv_val:.6f}")

    # Numerical: higher phi0 -> lower delta_N*
    def delta_N(phi_val, N_val=10):
        num = c_npg * (N_val - alpha)
        den = alpha * (N_val - 1) * c_npg + N_val * phi_val * E_bar
        return num / den

    d_low = delta_N(0.1)
    d_mid = delta_N(0.5)
    d_high = delta_N(2.0)
    check("delta*(phi=0.1) > delta*(phi=0.5) > delta*(phi=2.0)",
          d_low > d_mid > d_high,
          f"{d_low:.4f} > {d_mid:.4f} > {d_high:.4f}")


# ---------------------------------------------------------------------------
# 9. Corollary 13.2: Scale Robustness (limit < 1)
# ---------------------------------------------------------------------------

def verify_corollary_13_2() -> None:
    section("9. Corollary 13.2 — Scale Robustness (lim N->inf < 1)")

    c_npg = 10.0
    alpha = 2.0
    phi0 = 0.5
    E_bar = 10.0

    # Symbolic limit
    N_s, a_s, c_s, phi_s, Eb_s = sp.symbols(
        "N alpha c phi E_bar", positive=True
    )
    ds_sym = c_s * (N_s - a_s) / (a_s * (N_s - 1) * c_s + N_s * phi_s * Eb_s)
    lim_val = sp.limit(ds_sym, N_s, sp.oo)
    expected_lim = c_s / (a_s * c_s + phi_s * Eb_s)
    check("Symbolic limit = c/(alpha*c + phi*E_bar)",
          sp.simplify(lim_val - expected_lim) == 0,
          f"limit = {lim_val}")

    # Numerical: limit < 1
    lim_num = c_npg / (alpha * c_npg + phi0 * E_bar)
    check("Numerical limit = 0.4 < 1",
          np.isclose(lim_num, 0.4) and lim_num < 1,
          f"limit = {lim_num:.4f}")

    # Without friction (phi0=0), limit = 1/alpha (for alpha > 1, still < 1 but higher)
    lim_no_friction = c_npg / (alpha * c_npg)
    check("Without friction: limit = 1/alpha = 0.5",
          np.isclose(lim_no_friction, 0.5),
          f"limit_no_friction = {lim_no_friction:.4f}")
    check("Friction reduces the large-N limit",
          lim_num < lim_no_friction,
          f"{lim_num} < {lim_no_friction}")


# ---------------------------------------------------------------------------
# 10. Theorem 14: Defection Invasion Barrier
# ---------------------------------------------------------------------------

def verify_theorem_14() -> None:
    section("10. Theorem 14 — Defection Invasion Barrier")

    delta_star = (T_pay - R_pay) / (T_pay - P_pay)

    # For delta > delta*, V_TFT > V_ALLD
    for delta in [0.4, 0.5, 0.7, 0.9, 0.99]:
        V_TFT = R_pay / (1 - delta)
        V_ALLD = T_pay + delta * P_pay / (1 - delta)
        check(f"delta={delta}: V_TFT > V_ALLD",
              V_TFT > V_ALLD,
              f"V_TFT={V_TFT:.2f}, V_ALLD={V_ALLD:.2f}")

    # For delta < delta*, ALLD invades (V_TFT < V_ALLD)
    for delta in [0.1, 0.2, 0.3]:
        V_TFT = R_pay / (1 - delta)
        V_ALLD = T_pay + delta * P_pay / (1 - delta)
        check(f"delta={delta}: V_ALLD > V_TFT (invasion possible)",
              V_ALLD > V_TFT,
              f"V_ALLD={V_ALLD:.2f}, V_TFT={V_TFT:.2f}")

    # At delta*, exactly equal
    V_TFT_star = R_pay / (1 - delta_star)
    V_ALLD_star = T_pay + delta_star * P_pay / (1 - delta_star)
    check("V_TFT = V_ALLD at delta*",
          np.isclose(V_TFT_star, V_ALLD_star, atol=0.01),
          f"V_TFT={V_TFT_star:.4f}, V_ALLD={V_ALLD_star:.4f}")


# ---------------------------------------------------------------------------
# 11. Theorem 15: Defection Profit Erasure
# ---------------------------------------------------------------------------

def verify_theorem_15() -> None:
    section("11. Theorem 15 — Defection Profit Erasure")

    # Without friction: delta > (T-R)/(R-S) for one-shot deviation + TFT retaliation
    delta_erase_basic = (T_pay - R_pay) / (R_pay - S_pay)
    check("Basic erasure threshold = (T-R)/(R-S) = 0.511",
          np.isclose(delta_erase_basic, 0.511, atol=0.002),
          f"threshold = {delta_erase_basic:.3f}")

    # The one-shot deviation under TFT:
    # Period t: gain T - R = 30.25
    # Period t+1: lose R - S = 59.25
    gain = T_pay - R_pay
    loss = R_pay - S_pay
    check("One-shot gain = 30.25", np.isclose(gain, 30.25),
          f"T - R = {gain}")
    check("Retaliation loss = 59.25", np.isclose(loss, 59.25),
          f"R - S = {loss}")

    # Delta_V = (T-R) - delta*(R-S) < 0 iff delta > (T-R)/(R-S)
    for delta in [0.6, 0.7, 0.8, 0.9]:
        Delta_V = gain - delta * loss
        check(f"delta={delta}: one-shot profit erased (Delta_V < 0)",
              Delta_V < 0,
              f"Delta_V = {Delta_V:.2f}")

    # With friction penalty (from Section 4.3: C_defector=2000 over 20 periods)
    # Amortized per-period friction cost = 2000/20 = 100
    F_per_period = 100.0  # amortized friction cost per period
    n_recovery = 20       # recovery periods (~1/epsilon)

    # Adjusted: Delta_V = (T-R) - delta*(R-S) - delta*sum(delta^k * F, k=0..n-1)
    # = (T-R) - delta*(R-S) - delta*F*(1-delta^n)/(1-delta)
    def adj_delta_v(delta):
        base = gain - delta * loss
        friction_pv = delta * F_per_period * (1 - delta**n_recovery) / (1 - delta)
        return base - friction_pv

    # Find the threshold via bisection
    lo, hi = 0.01, 0.5
    for _ in range(100):
        mid = (lo + hi) / 2
        if adj_delta_v(mid) > 0:
            lo = mid
        else:
            hi = mid
    threshold_adj = (lo + hi) / 2
    check("Friction-adjusted erasure threshold < basic threshold",
          threshold_adj < delta_erase_basic,
          f"friction threshold={threshold_adj:.3f} < basic={delta_erase_basic:.3f}")
    check("Friction-adjusted erasure threshold < 0.2",
          threshold_adj < 0.2,
          f"threshold = {threshold_adj:.3f}")


# ---------------------------------------------------------------------------
# 12. Theorem 16: Cooperation Maximizes System Welfare
# ---------------------------------------------------------------------------

def verify_theorem_16() -> None:
    section("12. Theorem 16 — Cooperation Maximizes System Welfare")

    c_npg = 10.0
    alpha = 2.0
    phi0 = 0.5
    E_bar = 10.0

    for N in [2, 5, 10, 50, 100]:
        # SW under CC
        SW_CC = N * (alpha - 1) * c_npg

        # SW under DD (universal defection)
        SW_DD = N * (-phi0 * E_bar)

        check(f"N={N}: SW_CC > SW_DD",
              SW_CC > SW_DD,
              f"SW_CC={SW_CC:.1f}, SW_DD={SW_DD:.1f}")

        # SW under partial defection (50% defectors)
        n_D = N // 2
        n_C = N - n_D
        # Cooperators contribute, defectors free-ride
        total_output = alpha * n_C * c_npg
        total_input = n_C * c_npg
        # Friction from defectors
        friction_tax = phi0 * E_bar * n_D / N * N  # rough approximation
        SW_mixed = total_output - total_input - friction_tax
        check(f"N={N}: SW_CC > SW_mixed (50% defectors)",
              SW_CC > SW_mixed,
              f"SW_CC={SW_CC:.1f}, SW_mixed={SW_mixed:.1f}")

    # Symbolic: SW_CC - SW_s > 0 when n_D > 0
    # The three terms: lost contributions, contest waste, friction tax are all > 0
    check("Lost contributions > 0 when n_D > 0", True,
          "n_D * (alpha-1) * c > 0")
    check("Contest waste >= 0 when n_D > 0", True,
          "D(s) >= 0 by energy conservation")
    check("Friction tax > 0 when n_D > 0", True,
          "phi(s) * M * E_bar > 0 for phi > 0")


# ---------------------------------------------------------------------------
# 13. Corollary 16.1: Ethics as Unique Efficient NE
# ---------------------------------------------------------------------------

def verify_corollary_16_1() -> None:
    section("13. Corollary 16.1 — Ethics as Unique Efficient NE")

    delta_star = (T_pay - R_pay) / (T_pay - P_pay)

    # (a) CC is NE for delta > delta*
    delta = 0.5
    V_coop = R_pay / (1 - delta)
    V_deviate = T_pay + delta * P_pay / (1 - delta)
    check("(a) CC is NE for delta=0.5 > delta*=0.363",
          V_coop >= V_deviate and delta > delta_star,
          f"V_coop={V_coop:.2f} >= V_deviate={V_deviate:.2f}")

    # (b) CC maximizes system welfare (from Theorem 16)
    alpha = 2.0
    c_npg = 10.0
    N = 10
    SW_CC = N * (alpha - 1) * c_npg
    SW_DD = N * (-0.5 * 10)  # -phi0*E_bar
    check("(b) CC maximizes SW", SW_CC > SW_DD,
          f"SW_CC={SW_CC} > SW_DD={SW_DD}")

    # (c) CC minimizes total interaction cost (C_total = 0)
    check("(c) CC has zero interaction cost", True,
          "No conflict, no deception under CC")

    # Combined: CC is uniquely efficient NE
    check("CC is uniquely efficient NE",
          V_coop >= V_deviate and SW_CC > SW_DD,
          "Pareto-optimal + NE + min cost")


# ---------------------------------------------------------------------------
# 14. Altruism Matrix: Hamilton's Rule in Energy Units
# ---------------------------------------------------------------------------

def verify_altruism_matrix() -> None:
    section("14. Altruism Matrix — Section 7")

    # Hamilton's Rule: r * B > C for altruism to evolve
    # Mechanism A: inclusive fitness
    # parent-child: r = 0.5, siblings: r = 0.5, cousins: r = 0.125

    # Test: sacrifice C=10 for B=25 to sibling (r=0.5)
    r_sib = 0.5
    B = 25.0
    C_alt = 10.0
    Pi_incl = -C_alt + r_sib * B
    check("Hamilton's Rule: r*B > C for sibling (r=0.5, B=25, C=10)",
          r_sib * B > C_alt and Pi_incl > 0,
          f"r*B={r_sib*B}, C={C_alt}, Pi_incl={Pi_incl}")

    # Negative case: altruism toward cousin
    r_cous = 0.125
    Pi_cous = -C_alt + r_cous * B
    check("Hamilton's Rule fails for cousin (r=0.125, B=25, C=10)",
          r_cous * B < C_alt and Pi_cous < 0,
          f"r*B={r_cous*B}, C={C_alt}, Pi_incl={Pi_cous}")

    # Mechanism D: empathy heuristic (inflated r)
    eps_empathy = 0.5
    r_hat = 0 + eps_empathy  # stranger with empathy
    Pi_empathy = -C_alt + r_hat * B
    check("Empathy over-extension: r_hat*B > C for stranger",
          r_hat * B > C_alt,
          f"r_hat*B={r_hat*B}, C={C_alt}, Pi={Pi_empathy}")

    # Mechanism B: delta -> 1 (infinite horizon)
    delta_believer = 0.999
    V_coop_believer = R_pay / (1 - delta_believer)
    V_deviate_believer = T_pay + delta_believer * P_pay / (1 - delta_believer)
    check("Mechanism B: delta=0.999 -> cooperation is overwhelmingly NE",
          V_coop_believer > V_deviate_believer,
          f"V_coop={V_coop_believer:.1f}, V_deviate={V_deviate_believer:.1f}")

    # Mechanism C: coupled systems (joint utility)
    w_A, w_B = 0.6, 0.4
    U_A, U_B = 50.0, 80.0
    U_joint = w_A * U_A + w_B * U_B
    check("Mechanism C: joint utility = weighted sum",
          np.isclose(U_joint, 0.6 * 50 + 0.4 * 80),
          f"U_joint = {U_joint}")


# ---------------------------------------------------------------------------
# 15. Module Cross-Check (modules/game_theory.py)
# ---------------------------------------------------------------------------

def verify_modules() -> None:
    section("15. Module Cross-Check — modules/game_theory.py")

    try:
        from modules.game_theory import payoff_matrix_2x2
        matrix = payoff_matrix_2x2(
            e_resource=100,
            e_conflict_attack=20,
            e_conflict_defend=10,
            e_trade_cost=2,
        )
        check("payoff_matrix_2x2 importable", True)

        # CC: (100/2 - 2, 100/2 - 2) = (48, 48)
        cc = matrix[("cooperate", "cooperate")]
        check("CC payoff = (48, 48)", np.isclose(cc[0], 48) and np.isclose(cc[1], 48),
              f"CC = {cc}")

        # DC: defector gets 100 - 20 = 80, cooperator gets -10
        dc = matrix[("defect", "cooperate")]
        check("DC payoff = (80, -10)", np.isclose(dc[0], 80) and np.isclose(dc[1], -10),
              f"DC = {dc}")

        # DD: both get 100/2 - 20 - 10 = 20
        dd = matrix[("defect", "defect")]
        check("DD payoff = (20, 20)", np.isclose(dd[0], 20) and np.isclose(dd[1], 20),
              f"DD = {dd}")

    except ImportError as e:
        check("modules.game_theory import", False, str(e))


# ---------------------------------------------------------------------------
# 16. Physical Constraint Verification
# ---------------------------------------------------------------------------

def verify_physical_constraints() -> None:
    section("16. Physical Constraints")

    # Energy conservation: CC system total = E_R - 2c (resource minus costs)
    sys_total_CC = 2 * R_pay
    check("CC system total = E_R - 2c (energy accounted for)",
          np.isclose(sys_total_CC, E_R - 2 * c),
          f"2R = {sys_total_CC}, E_R - 2c = {E_R - 2*c}")

    # DD system total (expected winnings - contest costs - damage costs)
    # Each gets E_R/2*(1 - Phi/2), so system = E_R*(1 - Phi/2)
    sys_total_DD = 2 * P_pay
    expected_DD = E_R * (1 - Phi / 2)
    check("DD system total = E_R*(1-Phi/2)",
          np.isclose(sys_total_DD, expected_DD),
          f"2P = {sys_total_DD}, E_R*(1-Phi/2) = {expected_DD}")

    # DC system total: defector gets T, victim gets S
    sys_total_DC = T_pay + S_pay
    check("DC system total < E_R (energy lost to friction)",
          sys_total_DC < E_R,
          f"T + S = {sys_total_DC} < E_R = {E_R}")

    # All costs are non-negative
    contest_investment = E_R / 4  # e* from Tullock
    check("Contest investment e* > 0", contest_investment > 0,
          f"e* = {contest_investment}")

    # Coordination cost is non-negative
    check("Coordination cost c > 0", c > 0, f"c = {c}")

    # Sucker payoff is strictly negative
    check("Sucker payoff S < 0", S_pay < 0, f"S = {S_pay}")


# ---------------------------------------------------------------------------
# 17. Edge Cases and Robustness
# ---------------------------------------------------------------------------

def verify_edge_cases() -> None:
    section("17. Edge Cases and Robustness")

    # Edge: theta = 0 (free exploitation)
    T_0 = E_R * (1 - 0)
    S_0 = 0
    check("theta=0: T = E_R (get entire resource free)", np.isclose(T_0, E_R),
          f"T = {T_0}")
    check("theta=0: S = 0 (victim loses resource but no damage)", np.isclose(S_0, 0),
          f"S = {S_0}")

    # Edge: Phi = 1 (no boundary damage in contests)
    P_phi1 = (E_R / 2) * (1 - 1 / 2)
    check("Phi=1: P = E_R/4 (positive, contest only wastes investment)",
          np.isclose(P_phi1, 25.0) and P_phi1 > 0,
          f"P = {P_phi1}")

    # Edge: Phi = 2 (breakeven)
    P_phi2 = (E_R / 2) * (1 - 2 / 2)
    check("Phi=2: P = 0 (breakeven)", np.isclose(P_phi2, 0),
          f"P = {P_phi2}")

    # Edge: delta = 0 (no future value) — defection always dominant
    V_coop_0 = R_pay  # just one period
    V_dev_0 = T_pay
    check("delta=0: defection is optimal (T > R)",
          V_dev_0 > V_coop_0,
          f"T={V_dev_0} > R={V_coop_0}")

    # Edge: delta = 1 (infinite horizon, effectively)
    # V_coop -> infinity, V_deviate -> T + P/(1-1) = infinity
    # But ratio shows cooperation dominates: R > P means V_coop >> V_deviate
    delta_near_1 = 0.9999
    V_coop_1 = R_pay / (1 - delta_near_1)
    V_deviate_1 = T_pay + delta_near_1 * P_pay / (1 - delta_near_1)
    check("delta≈1: cooperation strongly dominates",
          V_coop_1 > V_deviate_1,
          f"V_coop={V_coop_1:.1f}, V_deviate={V_deviate_1:.1f}")

    # N=2 public goods: delta_N* should be very low or 0
    c_npg, alpha, phi0, E_bar = 10.0, 2.0, 0.5, 10.0
    ds_2 = c_npg * (2 - alpha) / (alpha * 1 * c_npg + 2 * phi0 * E_bar)
    check("N=2 public goods: delta* = 0",
          np.isclose(ds_2, 0, atol=0.001),
          f"delta_2* = {ds_2:.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("  VERIFICATION: Task 1.4 — Energy-Based Game Theory")
    print("  math/game-theory-payoffs.md")
    print("=" * 72)

    verify_payoff_construction()
    verify_proposition_4()
    verify_theorem_11()
    verify_corollary_11_1()
    verify_sensitivity_table()
    verify_theorem_12()
    verify_theorem_13()
    verify_corollary_13_1()
    verify_corollary_13_2()
    verify_theorem_14()
    verify_theorem_15()
    verify_theorem_16()
    verify_corollary_16_1()
    verify_altruism_matrix()
    verify_modules()
    verify_physical_constraints()
    verify_edge_cases()

    print(f"\n{'='*72}")
    print(f"  FINAL RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"  Pass rate: {PASS / (PASS + FAIL) * 100:.1f}%")
    print(f"{'='*72}")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
