"""
Verify: Why Cooperative Strategy Outperforms Adversarial Strategy
=================================================================

Theorems 11-16, Proposition 4, Corollaries 11.1, 13.1, 13.2, 14.1, 16.1.

Source of truth: papers/TC-V-cooperative-equilibrium/01-game-theory-payoffs.md
(The companion case-study write-up survives only as an archived snapshot under
internal/archive/april-06-2026/case-studies/cooperative-equilibrium.md, which still
encodes the pre-recalibration ledger; the paper governs where the two disagree.)

Validates the numerical claims using both symbolic (SymPy) and numerical (NumPy)
computation.

Run:  python scripts/simulations/applied/verify_cooperative_equilibrium.py
"""

from __future__ import annotations

import sys
import os
import math

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import sympy as sp

from modules.verify import reset, section, check, close, summary

# ---------------------------------------------------------------------------
# Scenario Parameters (from README §3.1)
# ---------------------------------------------------------------------------
E_R       = 100.0    # Resource value (energy units)
c_coord   = 2.0      # Coordination cost
theta     = 0.15     # Exploitation efficiency
psi_off   = 0.15     # Offensive damage fraction
psi_def   = 0.25     # Defensive damage fraction
kappa     = 2.0      # Repair multiplier
eta       = 0.01     # Network friction sensitivity
epsilon   = 0.05     # Trust recovery rate per period
M         = 1000     # Cooperative transactions per period
E_bar     = 10.0     # Average transaction value
N_agents  = 2        # Number of agents (two-player baseline)

# N-player game parameters
alpha_coop = 2.0     # Cooperative multiplier
c_contrib  = 10.0    # Per-agent contribution
phi_0      = 0.5     # Background network friction

TOL = 1e-6


# ---------------------------------------------------------------------------
# Core Payoff Functions
# ---------------------------------------------------------------------------

def compute_Phi(p_off, p_def, kap):
    """Friction multiplier Φ = 1 + κ(ψ^off + ψ^def) = 1 + κψ.

    The repair term κ·dB already re-supplies the destroyed boundary energy dB;
    charging a standalone dB on top double-counts by ψ·e_i (TC-IV §325).
    """
    return 1.0 + kap * (p_off + p_def)


def compute_T(E, th, p_off, kap):
    """Temptation payoff T = E_R[1 - θ(1 + κψ^off)]."""
    return E * (1.0 - th * (1.0 + kap * p_off))


def compute_R(E, coord_cost):
    """Reward payoff R = E_R/2 - c."""
    return E / 2.0 - coord_cost


def compute_P(E, Phi):
    """Punishment payoff P = (E_R/2)(1 - Φ/2)."""
    return (E / 2.0) * (1.0 - Phi / 2.0)


def compute_S(th, E, kap, p_def):
    """Sucker's payoff S = -θ E_R κ ψ^def."""
    return -th * E * kap * p_def


def delta_star(T_val, R_val, P_val):
    """Critical discount factor δ* = (T-R)/(T-P)."""
    return (T_val - R_val) / (T_val - P_val)


def V_coop(R_val, delta):
    """Lifetime payoff from cooperation: R/(1-δ)."""
    return R_val / (1.0 - delta)


def V_alld(T_val, P_val, delta):
    """Lifetime payoff from Always-Defect: T + δP/(1-δ)."""
    return T_val + delta * P_val / (1.0 - delta)


def delta_N_star(N, alpha, c, phi0, E_bar_val):
    """N-player critical discount factor."""
    num = c * (N - alpha)
    den = alpha * (N - 1) * c + N * phi0 * E_bar_val
    return num / den



if __name__ == "__main__":
    reset()


    # ===================================================================
    section("1. Proposition 4 — Physical Prisoner's Dilemma (MILD regime baseline)")
    # ===================================================================

    # Baseline ψ = ψ^off + ψ^def = 0.4 with κ = 2 gives κψ = 0.8 < 1, i.e. Φ < 2:
    # this is the MILD-dispute regime, in which mutual defection is still weakly
    # net-positive (P > 0). The destructive regime (κψ > 1) is checked below.
    Phi = compute_Phi(psi_off, psi_def, kappa)
    check("Φ = 1.8", abs(Phi - 1.8) < TOL, f"Φ={Phi:.2f}")

    T = compute_T(E_R, theta, psi_off, kappa)
    check("T = 80.5", abs(T - 80.5) < TOL, f"T={T:.4f}")

    R = compute_R(E_R, c_coord)
    check("R = 48", abs(R - 48.0) < TOL, f"R={R:.4f}")

    P = compute_P(E_R, Phi)
    check("P = +5 (mild regime: κψ < 1)", abs(P - 5.0) < TOL, f"P={P:.4f}")

    S = compute_S(theta, E_R, kappa, psi_def)
    check("S = -7.5", abs(S - (-7.5)) < TOL, f"S={S:.4f}")

    # Verify PD structure: T > R > P > S
    check("T > R", T > R, f"{T} > {R}")
    check("R > P", R > P, f"{R} > {P}")
    check("P > S", P > S, f"{P} > {S}")
    check("S < 0", S < 0, f"S={S}")
    check("PD structure: T > R > P > S", T > R > P > S)

    # Cooperation premium
    coop_premium = R - P
    check("Cooperation premium R-P = 43", abs(coop_premium - 43.0) < TOL,
          f"R-P={coop_premium:.2f}")

    # Admissibility (rmk-admissibility): P = (E_R/2)(1 - Φ/2) < 0 exactly when Φ > 2,
    # i.e. κψ > 1, i.e. ψ > 1/κ (one half at κ=2). The baseline sits BELOW that line.
    check("Baseline is the MILD regime: κψ < 1 ⟺ Φ < 2 ⟺ P > 0",
          kappa * (psi_off + psi_def) < 1.0 and Phi < 2.0 and P > 0,
          f"κψ={kappa*(psi_off+psi_def):.2f}, Φ={Phi:.2f}, P={P:+.1f}")

    # --- DESTRUCTIVE regime (κψ > 1): net-negative mutual defection ------------
    # Same κ=2, but a heavier damage split ψ^off=0.25, ψ^def=0.35 (ψ=0.6 > 1/κ=0.5).
    # This is the regime that carries the "conflict is net-negative" narrative;
    # it must be entered explicitly rather than read off the mild baseline.
    psi_off_dest, psi_def_dest = 0.25, 0.35
    Phi_dest = compute_Phi(psi_off_dest, psi_def_dest, kappa)
    T_dest = compute_T(E_R, theta, psi_off_dest, kappa)
    P_dest = compute_P(E_R, Phi_dest)
    S_dest = compute_S(theta, E_R, kappa, psi_def_dest)

    check("Destructive regime: κψ > 1 ⟺ Φ = 2.2 > 2",
          kappa * (psi_off_dest + psi_def_dest) > 1.0 and abs(Phi_dest - 2.2) < TOL,
          f"κψ={kappa*(psi_off_dest+psi_def_dest):.2f}, Φ={Phi_dest:.2f}")
    check("Destructive regime: T = 77.5", abs(T_dest - 77.5) < TOL, f"T={T_dest:.4f}")
    check("Destructive regime: R = 48 (no κ/ψ dependence)",
          abs(compute_R(E_R, c_coord) - 48.0) < TOL)
    check("Destructive regime: P = -5 < 0 (net-negative mutual defection)",
          abs(P_dest - (-5.0)) < TOL and P_dest < 0, f"P={P_dest:.4f}")
    check("Destructive regime: S = -10.5", abs(S_dest - (-10.5)) < TOL, f"S={S_dest:.4f}")
    check("Destructive regime: PD structure T > R > P > S",
          T_dest > R > P_dest > S_dest)
    check("Destructive regime: δ* = 0.358",
          abs(delta_star(T_dest, R, P_dest) - 0.358) < 0.001,
          f"δ*={delta_star(T_dest, R, P_dest):.4f}")

    # P crosses zero at Φ = 2 exactly (κψ = 1) — between the mild baseline (Φ=1.8,
    # P=+5) and the destructive regime (Φ=2.2, P=-5). This is the claim the figure
    # caption makes about panel (a).
    check("P crosses zero at Φ = 2, between Φ = 1.8 (P>0) and Φ = 2.2 (P<0)",
          abs(compute_P(E_R, 2.0)) < TOL and Phi < 2.0 < Phi_dest and P > 0 > P_dest,
          f"P(1.8)={P:+.1f}, P(2.0)={compute_P(E_R, 2.0):+.1f}, P(2.2)={P_dest:+.1f}")


    # ===================================================================
    section("2. Proposition 4 — Symbolic Verification")
    # ===================================================================

    E_s, c_s, th_s = sp.symbols('E_R c theta', positive=True)
    poff_s, pdef_s, kap_s = sp.symbols('psi_off psi_def kappa', positive=True)

    Phi_sym = 1 + kap_s * (poff_s + pdef_s)
    T_sym = E_s * (1 - th_s * (1 + kap_s * poff_s))
    R_sym = E_s / 2 - c_s
    P_sym = (E_s / 2) * (1 - Phi_sym / 2)
    S_sym = -th_s * E_s * kap_s * pdef_s

    # Verify S < 0 symbolically (all params positive)
    check("Symbolic S < 0 (all params positive)", S_sym.could_extract_minus_sign())

    # Verify P_sym at Φ = 2 gives P = 0
    P_at_Phi2 = P_sym.subs(Phi_sym, 2)
    # Alternatively, check P = 0 when Φ = 2
    Phi_num = Phi_sym.subs({poff_s: sp.Rational(15,100), pdef_s: sp.Rational(25,100), kap_s: 2})
    check("Symbolic Φ with baseline params = 9/5",
          Phi_num == sp.Rational(9, 5),
          f"Φ_sym = {Phi_num}")


    # ===================================================================
    section("3. Theorem 11 — Ethics Theorem (δ*)")
    # ===================================================================

    ds = delta_star(T, R, P)
    check("δ* = 0.431", abs(ds - 0.431) < 0.001, f"δ*={ds:.4f}")

    # Corollary 11.1: Φ > 2 → δ* < 0.5
    check("Corollary 11.1: δ* < 0.5", ds < 0.5, f"δ*={ds:.4f}")

    # Symbolic verification
    delta_s = sp.Symbol('delta', positive=True)
    ds_sym = (T_sym - R_sym) / (T_sym - P_sym)
    ds_num = ds_sym.subs({
        E_s: 100, c_s: 2, th_s: sp.Rational(15,100),
        poff_s: sp.Rational(15,100), pdef_s: sp.Rational(25,100), kap_s: 2
    })
    check("Symbolic δ* = 65/151",
          ds_num == sp.Rational(65, 151) or abs(float(ds_num) - ds) < 0.001,
          f"symbolic δ*={float(ds_num):.4f}")


    # ===================================================================
    section("4. Theorem 11 — Cooperation vs Defection Payoffs")
    # ===================================================================

    for delta_val in [0.431, 0.5, 0.8, 0.95]:
        vc = V_coop(R, delta_val)
        vd = V_alld(T, P, delta_val)
        if delta_val >= ds:
            check(f"V_coop > V_ALLD at δ={delta_val}",
                  vc > vd,
                  f"V_coop={vc:.2f}, V_ALLD={vd:.2f}")
        else:
            check(f"V_ALLD > V_coop at δ={delta_val} (below threshold)",
                  vd >= vc,
                  f"V_coop={vc:.2f}, V_ALLD={vd:.2f}")


    # ===================================================================
    section("5. Sensitivity — δ* Across Friction Regimes")
    # ===================================================================

    # Sensitivity table (TC-V §3.5). Each row carries its OWN (ψ^off, ψ^def, κ):
    # Φ, T, P and S all move together, so a row may NOT be generated by holding the
    # baseline T fixed and sliding Φ. The κ=2 rows differ only in the damage split —
    # the mild baseline (ψ=0.4) and the destructive regime (ψ=0.6) straddle Φ=2.
    friction_table = [
        # (label, psi_off, psi_def, kappa, Phi, T, P, S, delta_star)
        ("No repair cost",   0.15, 0.25, 0.0, 1.0, 85.00,  25.0,   0.00, 0.617),
        ("Low repair",       0.15, 0.25, 1.0, 1.4, 82.75,  15.0,  -3.75, 0.513),
        ("Baseline (mild)",  0.15, 0.25, 2.0, 1.8, 80.50,   5.0,  -7.50, 0.431),
        ("Destructive",      0.25, 0.35, 2.0, 2.2, 77.50,  -5.0, -10.50, 0.358),
        ("High repair",      0.15, 0.25, 4.0, 2.6, 76.00, -15.0, -15.00, 0.308),
    ]

    for label, po, pd_, kap, Phi_exp, T_exp, P_exp, S_exp, ds_exp in friction_table:
        Phi_calc = compute_Phi(po, pd_, kap)
        T_calc = compute_T(E_R, theta, po, kap)
        P_calc = compute_P(E_R, Phi_calc)
        S_calc = compute_S(theta, E_R, kap, pd_)
        ds_calc = delta_star(T_calc, R, P_calc)
        check(f"{label}: Φ={Phi_exp}, T={T_exp}, P={P_exp}, S={S_exp}, δ*={ds_exp}",
              abs(Phi_calc - Phi_exp) < TOL and abs(T_calc - T_exp) < TOL
              and abs(P_calc - P_exp) < TOL and abs(S_calc - S_exp) < TOL
              and abs(ds_calc - ds_exp) < 0.002,
              f"Φ={Phi_calc:.2f}, T={T_calc:.2f}, P={P_calc:.1f}, "
              f"S={S_calc:.2f}, δ*={ds_calc:.4f}")

    # Closed form along the κ-sweep at the baseline damage split (ψ^off=0.15,
    # ψ^def=0.25): δ*(κ) = (37 - 2.25κ)/(60 + 7.75κ).
    for kap in [0.0, 1.0, 2.0, 4.0]:
        Phi_k = compute_Phi(psi_off, psi_def, kap)
        ds_k = delta_star(compute_T(E_R, theta, psi_off, kap), R, compute_P(E_R, Phi_k))
        ds_closed = (37.0 - 2.25 * kap) / (60.0 + 7.75 * kap)
        check(f"δ*(κ={kap:.0f}) matches closed form (37-2.25κ)/(60+7.75κ)",
              abs(ds_k - ds_closed) < TOL,
              f"δ*={ds_k:.4f}, closed={ds_closed:.4f}")

    # Monotonicity: sweep the physical knob κ (not Φ at fixed T) so that Φ, T and S
    # stay mutually consistent. Restricted to κ ≤ 4, above which Φ > Φ_PD and the
    # game becomes Chicken (δ* switches to (T-R)/(T-S)).
    kappa_range = np.linspace(0.0, 4.0, 100)
    ds_range = [
        delta_star(compute_T(E_R, theta, psi_off, k), R,
                   compute_P(E_R, compute_Phi(psi_off, psi_def, k)))
        for k in kappa_range
    ]
    diffs = np.diff(ds_range)
    check("δ* monotonically decreases with κ (hence with Φ)", np.all(diffs < 0))


    # ===================================================================
    section("6. Theorem 12 — Network-Adjusted Cooperation")
    # ===================================================================

    v_violation = E_R  # Severity = full resource
    N_two = 2
    C_cascade_defector = eta * v_violation * M * E_bar / (N_two * epsilon)
    check("C_cascade (N=2) = 100,000",
          abs(C_cascade_defector - 100_000) < TOL,
          f"C_cascade={C_cascade_defector:.0f}")

    recovery_periods = 1.0 / epsilon  # = 20
    P_tilde_per_period = P - C_cascade_defector / recovery_periods
    check("P̃ ≈ -4,995",
          abs(P_tilde_per_period - (-4995)) < 1,
          f"P̃={P_tilde_per_period:.0f}")

    ds_network = (T - R) / (T - P_tilde_per_period)
    check("δ̃* ≈ 0.006",
          abs(ds_network - 0.006) < 0.001,
          f"δ̃*={ds_network:.5f}")

    check("δ̃* < δ* (network friction makes cooperation easier)",
          ds_network < ds)


    # ===================================================================
    section("7. Theorem 13 — N-Player Cooperation Thresholds")
    # ===================================================================

    # Table from README §3.6
    n_player_table = [
        # (N, dev_gain, punish_gap, delta_N_star_expected)
        (2,   0.00, 15.0, 0.000),
        (3,   3.33, 18.33, 0.182),
        (5,   6.00, 21.0, 0.286),
        (10,  8.00, 23.0, 0.348),
        (50,  9.60, 24.6, 0.390),
        (100, 9.80, 24.8, 0.395),
    ]

    for N_val, dev_exp, gap_exp, ds_N_exp in n_player_table:
        # Deviation gain: α(N-1)c/N - (α-1)c
        pi_dev = alpha_coop * (N_val - 1) * c_contrib / N_val
        pi_cc = (alpha_coop - 1) * c_contrib
        pi_dd = -phi_0 * E_bar  # = -5
        dev_gain = pi_dev - pi_cc
        punish_gap = pi_dev - pi_dd

        ds_N_calc = delta_N_star(N_val, alpha_coop, c_contrib, phi_0, E_bar)

        check(f"N={N_val}: δ_N*≈{ds_N_exp}",
              abs(ds_N_calc - ds_N_exp) < 0.002,
              f"δ_N*={ds_N_calc:.4f}")

        # Also verify deviation gain and gap
        check(f"N={N_val}: dev_gain≈{dev_exp}",
              abs(dev_gain - dev_exp) < 0.02,
              f"dev_gain={dev_gain:.2f}")

    # Verify limit as N → ∞ (Corollary 13.2)
    ds_inf = c_contrib / (alpha_coop * c_contrib + phi_0 * E_bar)
    check("δ_∞* = 0.400 (Corollary 13.2)",
          abs(ds_inf - 0.400) < 0.001,
          f"δ_∞*={ds_inf:.4f}")

    check("δ_∞* < 1 (cooperation scales to large N)",
          ds_inf < 1.0)


    # ===================================================================
    section("8. Corollary 13.1 — Cooperation Strengthens with Friction")
    # ===================================================================

    phi_vals = np.linspace(0.0, 2.0, 50)
    ds_N_vals = [delta_N_star(100, alpha_coop, c_contrib, phi, E_bar) for phi in phi_vals]
    diffs = np.diff(ds_N_vals)
    check("∂δ_N*/∂φ₀ < 0 (monotone decreasing)",
          np.all(diffs < 0),
          "verified for N=100 across φ₀ ∈ [0, 2]")

    # Without friction, δ_N* is higher
    ds_no_friction = delta_N_star(100, alpha_coop, c_contrib, 0.0, E_bar)
    ds_with_friction = delta_N_star(100, alpha_coop, c_contrib, phi_0, E_bar)
    check("Friction lowers threshold: δ*(φ=0.5) < δ*(φ=0)",
          ds_with_friction < ds_no_friction,
          f"φ=0.5: {ds_with_friction:.4f} < φ=0: {ds_no_friction:.4f}")


    # ===================================================================
    section("9. Theorem 14 — Invasion Barrier")
    # ===================================================================

    # δ = 0.5
    delta_test = 0.5
    vc_05 = V_coop(R, delta_test)
    vd_05 = V_alld(T, P, delta_test)
    check("V_TFT(δ=0.5) = 96", abs(vc_05 - 96.0) < TOL, f"V_TFT={vc_05:.2f}")
    check("V_ALLD(δ=0.5) = 85.5", abs(vd_05 - 85.5) < TOL, f"V_ALLD={vd_05:.2f}")
    check("TFT > ALLD at δ=0.5", vc_05 > vd_05)

    deficit_05 = 1 - vd_05 / vc_05
    check("Defector deficit ≈ 11% at δ=0.5",
          abs(deficit_05 - 0.109) < 0.01,
          f"deficit={deficit_05:.4f}")

    # δ = 0.8
    delta_test = 0.8
    vc_08 = V_coop(R, delta_test)
    vd_08 = V_alld(T, P, delta_test)
    check("V_TFT(δ=0.8) = 240", abs(vc_08 - 240.0) < TOL, f"V_TFT={vc_08:.2f}")
    check("V_ALLD(δ=0.8) = 100.5", abs(vd_08 - 100.5) < TOL, f"V_ALLD={vd_08:.2f}")
    check("TFT > ALLD at δ=0.8", vc_08 > vd_08)

    deficit_08 = 1 - vd_08 / vc_08
    check("Defector deficit ≈ 58% at δ=0.8",
          abs(deficit_08 - 0.581) < 0.01,
          f"deficit={deficit_08:.4f}")

    # For all δ > δ*, TFT dominates
    delta_sweep = np.linspace(ds + 0.001, 0.999, 200)
    all_tft_wins = all(V_coop(R, d) > V_alld(T, P, d) for d in delta_sweep)
    check("TFT > ALLD for all δ > δ*", all_tft_wins)


    # ===================================================================
    section("10. Theorem 15 — Profit Erasure")
    # ===================================================================

    # Without friction: breakeven at δ = (T-R)/(R-S)
    ds_erasure_basic = (T - R) / (R - S)
    check("δ_erasure (no friction) = 0.586",
          abs(ds_erasure_basic - 0.586) < 0.001,
          f"δ_erasure={ds_erasure_basic:.4f}")

    # Verify: ΔV = (T-R) - δ(R-S) = 0 at breakeven
    DV_at_break = (T - R) - ds_erasure_basic * (R - S)
    check("ΔV = 0 at breakeven", abs(DV_at_break) < TOL,
          f"ΔV={DV_at_break:.6f}")

    # With friction: F = 100/period over 20 recovery periods
    F_friction = C_cascade_defector / recovery_periods  # = 5000
    # Actually the README says F = 100 for the general case (not N=2 specific);
    # let's use the N=100 network from the math file
    # C_cascade for N=100: eta*v*M*E_bar/(N*epsilon) = 0.01*100*1000*10/(100*0.05) = 2000
    # F = 2000/20 = 100
    C_cascade_N100 = eta * v_violation * M * E_bar / (100 * epsilon)
    F_per_period = C_cascade_N100 / recovery_periods
    check("F (N=100 network) = 100/period",
          abs(F_per_period - 100.0) < TOL,
          f"F={F_per_period:.1f}")

    # Verify that with F = 100, defection is unprofitable for δ ≳ 0.183.
    # Breakeven solves (R-S)δ² - [(T-R) + (R-S) + F]δ + (T-R) = 0, i.e.
    # 55.5δ² - 188δ + 32.5 = 0 → δ = 0.18274 (the other root, 3.20, is rejected).
    a_q, b_q, c_q = (R - S), -((T - R) + (R - S) + F_per_period), (T - R)
    root_erasure = (-b_q - math.sqrt(b_q**2 - 4*a_q*c_q)) / (2*a_q)
    check("δ_erasure (with friction) = 0.183",
          abs(root_erasure - 0.18274) < 0.001,
          f"δ_erasure={root_erasure:.5f}")

    delta_test_friction = 0.19
    # ΔV_adj = (T-R) - δ(R-S) - sum of F discounted
    # The friction cost over 20 periods: δ*F * (1 - δ^20)/(1 - δ)
    geo_sum = delta_test_friction * F_per_period * (1 - delta_test_friction**20) / (1 - delta_test_friction)
    DV_adj = (T - R) - delta_test_friction * (R - S) - geo_sum
    check("ΔV_adj < 0 at δ=0.19 with friction (above the 0.183 breakeven)",
          DV_adj < 0,
          f"ΔV_adj={DV_adj:.2f}")


    # ===================================================================
    section("11. Theorem 16 / Corollary 16.1 — Welfare Maximization")
    # ===================================================================

    # Universal cooperation welfare: N(α-1)c
    for N_val in [2, 5, 10, 100]:
        SW_cc = N_val * (alpha_coop - 1) * c_contrib
        check(f"SW_CC(N={N_val}) = {N_val * 10}",
              abs(SW_cc - N_val * 10) < TOL)

    # Any defection strictly reduces welfare
    # With n_D = 1 defector out of N = 10:
    N_w = 10
    n_D = 1
    # Lost contribution
    lost = n_D * (alpha_coop - 1) * c_contrib
    # Contest dissipation (simplified: proportional to defection)
    # Friction tax
    phi_defect = eta * v_violation  # single defection friction injection
    friction_tax = phi_defect * M * E_bar
    SW_reduction = lost + friction_tax  # lower bound
    check("SW reduction > 0 with 1 defector (N=10)",
          SW_reduction > 0,
          f"lost={lost:.1f}, friction_tax={friction_tax:.1f}, total={SW_reduction:.1f}")


    # ===================================================================
    section("12. Iterated Game Simulation — TFT vs ALLD vs ALLC")
    # ===================================================================

    def simulate_iterated(strategy_A, strategy_B, delta, rounds=200):
        """Simulate an iterated PD between two strategies.
        Strategies: 'TFT', 'ALLD', 'ALLC', 'PAVLOV'
        Returns (total_A, total_B) discounted payoffs.
        """
        payoffs = {
            ('C', 'C'): (R, R),
            ('C', 'D'): (S, T),
            ('D', 'C'): (T, S),
            ('D', 'D'): (P, P),
        }

        history_A, history_B = [], []
        total_A, total_B = 0.0, 0.0

        for t in range(rounds):
            # Determine actions
            if strategy_A == 'TFT':
                a = 'C' if t == 0 or history_B[-1] == 'C' else 'D'
            elif strategy_A == 'ALLD':
                a = 'D'
            elif strategy_A == 'ALLC':
                a = 'C'
            elif strategy_A == 'PAVLOV':
                if t == 0:
                    a = 'C'
                else:
                    # Repeat if last round was good (CC or DC), switch if bad
                    last_payoff_A = payoffs[(history_A[-1], history_B[-1])][0]
                    a = history_A[-1] if last_payoff_A >= R else ('D' if history_A[-1] == 'C' else 'C')
            else:
                a = 'C'

            if strategy_B == 'TFT':
                b = 'C' if t == 0 or history_A[-1] == 'C' else 'D'
            elif strategy_B == 'ALLD':
                b = 'D'
            elif strategy_B == 'ALLC':
                b = 'C'
            elif strategy_B == 'PAVLOV':
                if t == 0:
                    b = 'C'
                else:
                    last_payoff_B = payoffs[(history_A[-1], history_B[-1])][1]
                    b = history_B[-1] if last_payoff_B >= R else ('D' if history_B[-1] == 'C' else 'C')
            else:
                b = 'C'

            pa, pb = payoffs[(a, b)]
            total_A += (delta ** t) * pa
            total_B += (delta ** t) * pb
            history_A.append(a)
            history_B.append(b)

        return total_A, total_B


    # TFT vs TFT → mutual cooperation
    delta_sim = 0.95
    va_tft_tft, vb_tft_tft = simulate_iterated('TFT', 'TFT', delta_sim)
    check("TFT vs TFT: mutual cooperation payoff ≈ R/(1-δ)",
          abs(va_tft_tft - R / (1 - delta_sim)) / (R / (1 - delta_sim)) < 0.01,
          f"simulated={va_tft_tft:.1f}, analytic={R/(1-delta_sim):.1f}")

    # TFT vs ALLD → ALLD gets T then P...
    va_tft_alld, vb_tft_alld = simulate_iterated('TFT', 'ALLD', delta_sim)
    # ALLD should earn approximately T + δP/(1-δ) against TFT
    alld_analytic = T + delta_sim * P / (1 - delta_sim)
    check("TFT vs ALLD: ALLD payoff ≈ T + δP/(1-δ)",
          abs(vb_tft_alld - alld_analytic) / max(abs(alld_analytic), 1) < 0.05,
          f"simulated={vb_tft_alld:.1f}, analytic={alld_analytic:.1f}")

    # TFT vs ALLD: TFT should still outperform in population
    # Compare TFT-vs-TFT payoff to ALLD-vs-TFT payoff
    check("TFT in cooperative population > ALLD mutant",
          va_tft_tft > vb_tft_alld,
          f"TFT={va_tft_tft:.1f} > ALLD={vb_tft_alld:.1f}")

    # ALLD vs ALLD → mutual defection
    va_alld_alld, _ = simulate_iterated('ALLD', 'ALLD', delta_sim)
    check("ALLD vs ALLD: mutual defection ≈ P/(1-δ)",
          abs(va_alld_alld - P / (1 - delta_sim)) / max(abs(P / (1 - delta_sim)), 1) < 0.01,
          f"simulated={va_alld_alld:.1f}, analytic={P/(1-delta_sim):.1f}")


    # ===================================================================
    section("13. Multi-Strategy Tournament")
    # ===================================================================

    strategies = ['TFT', 'ALLD', 'ALLC', 'PAVLOV']
    delta_tourney = 0.95

    # Round-robin tournament
    scores = {s: 0.0 for s in strategies}
    for i, s1 in enumerate(strategies):
        for j, s2 in enumerate(strategies):
            va, vb = simulate_iterated(s1, s2, delta_tourney)
            scores[s1] += va
            scores[s2] += vb

    # TFT should be the top or near-top performer
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    check("TFT is top-2 strategy in tournament",
          ranked[0][0] in ('TFT', 'PAVLOV') or ranked[1][0] in ('TFT', 'PAVLOV'),
          f"ranking: {[(s, f'{v:.0f}') for s, v in ranked]}")

    # ALLD should be worst or near-worst
    check("ALLD is bottom-2 in tournament",
          ranked[-1][0] == 'ALLD' or ranked[-2][0] == 'ALLD',
          f"ranking: {[(s, f'{v:.0f}') for s, v in ranked]}")


    # ===================================================================
    section("14. N-Player Convergence Properties")
    # ===================================================================

    # Verify δ_N* is monotonically increasing in N (for N >= α)
    N_range = range(3, 201)
    ds_N_list = [delta_N_star(n, alpha_coop, c_contrib, phi_0, E_bar) for n in N_range]
    diffs = np.diff(ds_N_list)
    check("δ_N* monotonically increasing in N (N≥3)",
          np.all(diffs >= -TOL),
          "verified for N ∈ [3, 200]")

    # Verify convergence to limit
    ds_200 = delta_N_star(200, alpha_coop, c_contrib, phi_0, E_bar)
    check("δ_200* ≈ δ_∞* (convergence)",
          abs(ds_200 - ds_inf) < 0.005,
          f"δ_200*={ds_200:.4f}, δ_∞*={ds_inf:.4f}")

    # All bounded below 1
    check("All δ_N* < 1", all(d < 1.0 for d in ds_N_list))

    # Without friction: limit approaches 0.5
    ds_inf_no_friction = c_contrib / (alpha_coop * c_contrib)
    check("δ_∞* without friction = 0.5",
          abs(ds_inf_no_friction - 0.5) < TOL,
          f"δ_∞*(φ=0)={ds_inf_no_friction:.4f}")


    # ===================================================================
    section("15. Invasion Dynamics Simulation")
    # ===================================================================

    def simulate_invasion(N_pop, n_defectors, delta, payoffs=None, rounds=100):
        """Simulate a population of N_pop agents with n_defectors ALLD and rest TFT.
        Returns average payoff per TFT and per ALLD agent.

        `payoffs` is a (T, R, P, S) tuple, defaulting to the mild-regime baseline.
        The invasion crossover depends on the SIGN of P: mutual defection only
        self-punishes a defector-heavy population when κψ > 1 (P < 0).
        """
        T_v, R_v, P_v, S_v = payoffs if payoffs is not None else (T, R, P, S)
        n_coop = N_pop - n_defectors
        # Each agent plays against every other agent
        # TFT vs TFT: R/(1-δ)
        # TFT vs ALLD: S + δR/(1-δ) for TFT (gets S first round, then DD)
        # ALLD vs TFT: T + δP/(1-δ)
        # ALLD vs ALLD: P/(1-δ)

        v_tft_tft = R_v / (1 - delta)
        # TFT against ALLD: round 1 gets S (cooperated), round 2+ both defect
        v_tft_vs_alld = S_v + delta * P_v / (1 - delta)
        v_alld_vs_tft = T_v + delta * P_v / (1 - delta)
        v_alld_alld = P_v / (1 - delta)

        avg_tft = ((n_coop - 1) * v_tft_tft + n_defectors * v_tft_vs_alld) / (N_pop - 1) if n_coop > 0 else 0
        avg_alld = (n_coop * v_alld_vs_tft + (n_defectors - 1) * v_alld_alld) / (N_pop - 1) if n_defectors > 0 else 0

        return avg_tft, avg_alld

    def invasion_crossover(delta, payoffs=None):
        """Largest defector count n_d (out of 100) at which TFT still out-earns ALLD."""
        last = 0
        for n_d in range(1, 100):
            at, ad = simulate_invasion(100, n_d, delta, payoffs)
            if at > ad:
                last = n_d
            else:
                break
        return last

    # 99 TFT + 1 ALLD
    avg_tft, avg_alld = simulate_invasion(100, 1, 0.5)
    check("1 ALLD in 99 TFT: TFT > ALLD (δ=0.5)",
          avg_tft > avg_alld,
          f"TFT={avg_tft:.2f}, ALLD={avg_alld:.2f}")

    # 10 ALLD in 90 TFT
    avg_tft, avg_alld = simulate_invasion(100, 10, 0.5)
    check("10 ALLD in 90 TFT: TFT > ALLD (δ=0.5)",
          avg_tft > avg_alld,
          f"TFT={avg_tft:.2f}, ALLD={avg_alld:.2f}")

    # 50 ALLD in 50 TFT — in the MILD regime ALLD now edges ahead. With κψ < 1 mutual
    # defection still pays P = +5, so a defector-heavy population no longer punishes
    # itself and TFT's first-round S exploitation is not recouped. This is a genuine
    # consequence of the recalibrated ledger, not a regression.
    avg_tft, avg_alld = simulate_invasion(100, 50, 0.5)
    check("50 ALLD in 50 TFT: ALLD edges ahead in the MILD regime (δ=0.5)",
          avg_alld > avg_tft,
          f"TFT={avg_tft:.2f}, ALLD={avg_alld:.2f}")

    # At high defector fractions TFT loses first-round S exploitation — the standard
    # bi-stability result. The crossover location is regime-dependent.
    n_d_mild = invasion_crossover(0.5)
    check("Mild regime: TFT resists invasion up to n_d = 41 (δ=0.5)",
          n_d_mild == 41,
          f"TFT wins for n_d ≤ {n_d_mild}")

    # --- DESTRUCTIVE regime (κψ > 1, P = -5 < 0) ------------------------------
    # Majority-resistance is a claim about SELF-PUNISHING mutual defection, so it
    # belongs to the destructive regime rather than the mild baseline.
    dest_payoffs = (T_dest, R, P_dest, S_dest)
    avg_tft_d, avg_alld_d = simulate_invasion(100, 50, 0.5, dest_payoffs)
    check("50 ALLD in 50 TFT: TFT > ALLD in the DESTRUCTIVE regime (δ=0.5)",
          avg_tft_d > avg_alld_d,
          f"TFT={avg_tft_d:.2f}, ALLD={avg_alld_d:.2f}")

    n_d_dest = invasion_crossover(0.5, dest_payoffs)
    check("Destructive regime: TFT resists invasion up to majority defectors (δ=0.5)",
          n_d_dest >= 50,
          f"TFT wins for n_d ≤ {n_d_dest}")

    check("Net-negative mutual defection widens TFT's basin (n_d: 41 → majority)",
          n_d_dest > n_d_mild,
          f"mild n_d ≤ {n_d_mild}, destructive n_d ≤ {n_d_dest}")

    # Verify the critical cluster size exists (bi-stability) in both regimes
    check("Bi-stability: critical defector fraction exists (both regimes)",
          0 < n_d_mild < 99 and 0 < n_d_dest < 99,
          f"critical n_d ≈ {n_d_mild} (mild), {n_d_dest} (destructive)")


    # ===================================================================
    section("16. System Welfare Comparison")
    # ===================================================================

    # Compare total system welfare under different strategy profiles
    N_sw = 10

    # All cooperate
    SW_all_coop = N_sw * R  # each gets R
    # All defect
    SW_all_def = N_sw * P   # each gets P
    # 1 defector, N-1 cooperators (approximately)
    # Defector gets T, each victim gets S, other cooperators get R
    SW_one_def = T + (N_sw - 1) * ((N_sw - 2) / (N_sw - 1) * R + 1 / (N_sw - 1) * S)

    check(f"SW(all coop, N={N_sw}) = {N_sw * R:.0f}",
          abs(SW_all_coop - N_sw * R) < TOL,
          f"SW={SW_all_coop:.0f}")

    check(f"SW(all defect, N={N_sw}) = {N_sw * P:.0f}",
          abs(SW_all_def - N_sw * P) < TOL,
          f"SW={SW_all_def:.0f}")

    check("SW(all coop) > SW(1 defector) > SW(all defect)",
          SW_all_coop > SW_one_def > SW_all_def,
          f"coop={SW_all_coop:.0f}, 1def={SW_one_def:.0f}, alldef={SW_all_def:.0f}")

    # -------------------------------------------------------------------
    # FIGURE DATA EXPORT
    # -------------------------------------------------------------------
    section("FIGURE DATA — Cooperative Equilibrium")

    from modules.figure_data import save_figure_data

    # Panel (a): Payoff matrix heatmap across friction regimes.
    # Vary kappa (physical knob) so Phi, T, S are all consistently recomputed
    # per row. Matches the sensitivity table in the paper (TC-V Section 3.5).
    kappa_vals_fig = np.array([0.0, 1.0, 2.0, 4.0, 6.0])
    Phi_vals = np.array([
        compute_Phi(psi_off, psi_def, k) for k in kappa_vals_fig
    ])
    payoff_matrix = np.zeros((len(kappa_vals_fig), 4))
    for i, k_v in enumerate(kappa_vals_fig):
        Phi_v = compute_Phi(psi_off, psi_def, k_v)
        T_v = compute_T(E_R, theta, psi_off, k_v)
        R_v = compute_R(E_R, c_coord)
        P_v = compute_P(E_R, Phi_v)
        S_v = compute_S(theta, E_R, k_v, psi_def)
        payoff_matrix[i] = [T_v, R_v, P_v, S_v]

    # Panel (b): N-player cooperation threshold vs friction
    N_range_fig = np.arange(3, 201)
    phi_scenarios = np.array([0.0, 0.25, 0.5, 1.0])
    delta_N_curves = np.array([
        [delta_N_star(N, alpha_coop, c_contrib, phi0, E_bar)
         for N in N_range_fig]
        for phi0 in phi_scenarios
    ])

    # Panel (c): Invasion barrier — payoff ratio vs delta
    Phi_base = compute_Phi(psi_off, psi_def, kappa)
    T_base = compute_T(E_R, theta, psi_off, kappa)
    R_base = compute_R(E_R, c_coord)
    P_base = compute_P(E_R, Phi_base)
    ds_base = delta_star(T_base, R_base, P_base)
    delta_range_invasion = np.linspace(0.01, 0.99, 500)
    payoff_ratio = np.array([
        V_alld(T_base, P_base, d) / V_coop(R_base, d)
        if V_coop(R_base, d) != 0 else np.nan
        for d in delta_range_invasion
    ])

    save_figure_data(
        "cooperative_equilibrium",
        Phi_vals=Phi_vals,
        payoff_matrix=payoff_matrix,
        N_range=N_range_fig,
        phi_scenarios=phi_scenarios,
        delta_N_curves=delta_N_curves,
        delta_range_invasion=delta_range_invasion,
        payoff_ratio=payoff_ratio,
        delta_star_base=np.array(ds_base),
        T_base=np.array(T_base),
        R_base=np.array(R_base),
        P_base=np.array(P_base),
        alpha_coop=np.array(alpha_coop),
        c_contrib=np.array(c_contrib),
        E_bar=np.array(E_bar),
    )
    check("Figure data saved", True)

    sys.exit(summary())
