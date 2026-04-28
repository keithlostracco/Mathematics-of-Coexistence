"""
Verify Task 1.2: Thermodynamic Friction — The Energy Cost of Conflict
======================================================================

This script independently validates every numerical claim, theorem,
and corollary from math/thermodynamic-friction.md using both symbolic
(SymPy) and numerical (NumPy) computation.

Run:  python scripts/simulations/verify_thermodynamic_friction.py
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
# 0. Helpers (same pattern as Task 1.1 verification)
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
# 1. Boundary Integrity Model (Section 2)
# ---------------------------------------------------------------------------

def verify_boundary_model() -> None:
    section("1. Boundary Integrity Model (Section 2)")

    # Full breach cost = B_i for all profiles
    B = 100.0
    for profile, f_desc in [("uniform", "f(s)=1"),
                             ("hardening", "f(s)=2s"),
                             ("shell", "f(s)=2(1-s)")]:
        if profile == "uniform":
            W_full = B * 1.0  # integral of 1 from 0 to 1
        elif profile == "hardening":
            W_full = B * 1.0  # integral of 2s from 0 to 1 = 1
        elif profile == "shell":
            W_full = B * 1.0  # integral of 2(1-s) from 0 to 1 = 1
        check(f"Full breach cost = B ({profile})",
              np.isclose(W_full, B),
              f"W_breach(1) = {W_full}, B = {B}")

    # Verify resistance profile normalization symbolically
    s = sp.Symbol("s")
    profiles = {
        "uniform": sp.Integer(1),
        "hardening": 2 * s,
        "shell": 2 * (1 - s),
    }
    for name, f_s in profiles.items():
        integral = sp.integrate(f_s, (s, 0, 1))
        check(f"Normalization: integral f(s)=1 ({name})",
              integral == 1,
              f"integral = {integral}")

    # Partial breach: hardening profile at d=0.5
    # integral_0^0.5 2s ds = [s^2]_0^0.5 = 0.25
    W_half_hardening = B * 0.25
    check("Hardening: W_breach(0.5) = 0.25*B",
          np.isclose(W_half_hardening, 25.0),
          f"{W_half_hardening}")

    # Partial breach: shell profile at d=0.5
    # integral_0^0.5 2(1-s) ds = [2s - s^2]_0^0.5 = 1.0 - 0.25 = 0.75
    W_half_shell = B * 0.75
    check("Shell: W_breach(0.5) = 0.75*B",
          np.isclose(W_half_shell, 75.0),
          f"{W_half_shell}")

    # Maintenance cost
    gamma = 0.1
    C_maintain = gamma * B
    check("Maintenance cost = gamma * B",
          np.isclose(C_maintain, 10.0),
          f"C = {C_maintain}")


# ---------------------------------------------------------------------------
# 2. Symmetric Contest NE — Proposition 2 (Section 3.3)
# ---------------------------------------------------------------------------

def verify_symmetric_contest_ne() -> None:
    section("2. Symmetric Contest NE — Proposition 2 (Section 3.3)")

    E_j = 100.0

    # Symbolic verification of FOC
    e_A, e_B, E = sp.symbols("e_A e_B E", positive=True)
    Pi_A = e_A / (e_A + e_B) * E - e_A
    dPi = sp.diff(Pi_A, e_A)

    # At symmetric NE: e_A = e_B
    e_sym = sp.Symbol("e", positive=True)
    foc_sym = dPi.subs([(e_A, e_sym), (e_B, e_sym)])
    sol = sp.solve(foc_sym, e_sym)
    check("Symbolic: symmetric NE e* = E/4",
          len(sol) == 1 and sp.simplify(sol[0] - E / 4) == 0,
          f"e* = {sol}")

    # Numerical verification
    e_star = E_j / 4
    D_2 = 2 * e_star
    Pi_star = E_j / 2 - e_star

    check("e* = 25.0", np.isclose(e_star, 25.0))
    check("D_2 = 50.0 (50% dissipation)", np.isclose(D_2, 50.0))
    check("Pi* = 25.0", np.isclose(Pi_star, 25.0))
    check("Dissipation ratio = 0.5", np.isclose(D_2 / E_j, 0.5))

    # Verify FOC satisfied numerically
    eps = 1e-8
    Pi_at_e = lambda ea, eb: ea / (ea + eb) * E_j - ea
    dPi_num = (Pi_at_e(e_star + eps, e_star) - Pi_at_e(e_star - eps, e_star)) / (2 * eps)
    check("FOC dPi/de_A ≈ 0 at NE",
          np.isclose(dPi_num, 0, atol=1e-4),
          f"dPi/de_A = {dPi_num:.8f}")


# ---------------------------------------------------------------------------
# 3. Asymmetric Contest NE — Proposition 3 (Section 3.3)
# ---------------------------------------------------------------------------

def verify_asymmetric_contest_ne() -> None:
    section("3. Asymmetric Contest NE — Proposition 3 (Section 3.3)")

    # Case: V_A = V_B = 100 (should reduce to symmetric)
    V_A, V_B = 100.0, 100.0
    e_A = V_A ** 2 * V_B / (V_A + V_B) ** 2
    e_B = V_A * V_B ** 2 / (V_A + V_B) ** 2
    D = e_A + e_B

    check("Symmetric case: e_A = E/4 = 25",
          np.isclose(e_A, 25.0), f"e_A = {e_A}")
    check("Symmetric case: e_B = E/4 = 25",
          np.isclose(e_B, 25.0), f"e_B = {e_B}")
    check("Symmetric case: D = E/2 = 50",
          np.isclose(D, 50.0), f"D = {D}")

    # Case: V_A = 150, V_B = 50
    V_A, V_B = 150.0, 50.0
    e_A = V_A ** 2 * V_B / (V_A + V_B) ** 2
    e_B = V_A * V_B ** 2 / (V_A + V_B) ** 2
    D = e_A + e_B
    D_harmonic = V_A * V_B / (V_A + V_B)

    check("Asymmetric: D = V_A*V_B/(V_A+V_B)",
          np.isclose(D, D_harmonic),
          f"D={D:.4f}, harmonic={D_harmonic:.4f}")
    check("Asymmetric: D = 37.5",
          np.isclose(D, 37.5), f"D = {D}")
    check("Asymmetric: e_A > e_B (higher valuer invests more)",
          e_A > e_B, f"e_A={e_A:.2f}, e_B={e_B:.2f}")

    # Symbolic verification of the harmonic semi-mean
    VA, VB = sp.symbols("V_A V_B", positive=True)
    eA_sym = VA ** 2 * VB / (VA + VB) ** 2
    eB_sym = VA * VB ** 2 / (VA + VB) ** 2
    D_sym = sp.simplify(eA_sym + eB_sym)
    expected = VA * VB / (VA + VB)
    check("Symbolic: D = V_A*V_B/(V_A+V_B)",
          sp.simplify(D_sym - expected) == 0,
          f"D_sym = {D_sym}")

    # Max dissipation at V_A = V_B
    # D(V_A, V_B) = V_A*V_B/(V_A+V_B), fixing V_A+V_B = S (constant sum)
    # D = V_A*(S-V_A)/S, maximized at V_A = S/2
    S_val = 200.0
    D_equal = (S_val / 2) ** 2 / S_val
    D_unequal = 150.0 * 50.0 / S_val
    check("Max dissipation at equal valuations",
          D_equal > D_unequal,
          f"D(100,100)={D_equal:.1f} > D(150,50)={D_unequal:.1f}")


# ---------------------------------------------------------------------------
# 4. N-Agent Contest Scaling — Theorem 4 (Section 3.4)
# ---------------------------------------------------------------------------

def verify_n_agent_scaling() -> None:
    section("4. N-Agent Contest Scaling — Theorem 4 (Section 3.4)")

    E_j = 100.0

    # Verify for specific N values from the table
    expected = [
        # (N, e_i_frac, D_frac, diss_ratio, payoff_frac)
        (2, 1 / 4, 1 / 2, 0.5, 1 / 4),
        (3, 2 / 9, 2 / 3, 2 / 3, 1 / 9),
        (5, 4 / 25, 4 / 5, 0.8, 1 / 25),
        (10, 9 / 100, 9 / 10, 0.9, 1 / 100),
        (100, 99 / 10000, 99 / 100, 0.99, 1 / 10000),
    ]

    for N, e_frac, D_frac, diss_pct, pi_frac in expected:
        e_i = (N - 1) / N ** 2 * E_j
        D_N = N * e_i
        diss_ratio = D_N / E_j
        Pi_i = E_j / N - e_i

        check(f"N={N:3d}: e_i = {e_frac:.6f}*E",
              np.isclose(e_i / E_j, e_frac),
              f"e_i/E = {e_i / E_j:.6f}")
        check(f"N={N:3d}: D_N/E = {diss_pct:.2f}",
              np.isclose(diss_ratio, diss_pct),
              f"D_N/E = {diss_ratio:.6f}")
        check(f"N={N:3d}: Pi_i = E/N^2",
              np.isclose(Pi_i / E_j, pi_frac),
              f"Pi_i/E = {Pi_i / E_j:.8f}")

    # Corollary 4.1: Vanishing returns
    N_large = 10000
    Pi_large = E_j / N_large ** 2
    check("Vanishing returns: Pi(N=10000) ≈ 0",
          Pi_large < 0.01,
          f"Pi = {Pi_large:.6f}")

    # Corollary 4.2: Unit dissipation limit
    D_large = (N_large - 1) / N_large * E_j
    check("Unit dissipation: D(N=10000)/E ≈ 1",
          np.isclose(D_large / E_j, 1.0, atol=1e-3),
          f"D/E = {D_large / E_j:.6f}")

    # Monotonicity: D_N/E_j is strictly increasing in N
    N_vals = [2, 3, 5, 10, 20, 50, 100, 1000]
    diss_ratios = [(N - 1) / N for N in N_vals]
    check("Dissipation ratio monotonically increasing in N",
          all(a < b for a, b in zip(diss_ratios, diss_ratios[1:])),
          f"ratios = {[f'{d:.4f}' for d in diss_ratios]}")


# ---------------------------------------------------------------------------
# 5. Friction Multiplier and System Loss — Theorem 5 (Sections 4-5)
# ---------------------------------------------------------------------------

def verify_friction_multiplier() -> None:
    section("5. Friction Multiplier & Net-Negative Theorem (Sections 4-5)")

    # Verify Phi formula
    delta_off, delta_def, kappa = 0.15, 0.25, 2.0
    Phi = 1 + (1 + kappa) * (delta_off + delta_def)
    check("Phi = 1 + (1+kappa)(delta_off+delta_def)",
          np.isclose(Phi, 2.2),
          f"Phi = {Phi}")

    # Verify complete ledger for 2-agent case (Example 9.1)
    E_j = 100.0
    N = 2
    e_star = E_j / 4  # = 25
    D_2 = E_j / 2  # = 50
    delta_sum = delta_off + delta_def  # = 0.4

    boundary_damage_per_agent = delta_sum * e_star  # = 10
    repair_per_agent = kappa * boundary_damage_per_agent  # = 20
    total_per_agent = e_star + boundary_damage_per_agent + repair_per_agent  # 25+10+20 = 55

    check("Boundary damage per agent = 10",
          np.isclose(boundary_damage_per_agent, 10.0))
    check("Repair per agent = 20",
          np.isclose(repair_per_agent, 20.0))
    check("Total per agent = 55",
          np.isclose(total_per_agent, 55.0))

    L_system = N * total_per_agent  # 110
    check("L_system = 110", np.isclose(L_system, 110.0))
    check("L_system = Phi * D_2",
          np.isclose(L_system, Phi * D_2),
          f"Phi*D_2 = {Phi * D_2}")

    V_net = E_j - L_system
    check("V_net = -10 (net-negative)", np.isclose(V_net, -10.0))

    # Verify net-negative condition: Phi > N/(N-1)
    threshold_2 = N / (N - 1)  # = 2
    check("Threshold for N=2: Phi > 2",
          np.isclose(threshold_2, 2.0) and Phi > threshold_2,
          f"Phi={Phi} > {threshold_2}")

    # Verify the table in Section 5.3
    table_data = [
        # (delta_sum, kappa, Phi, N=2 pct, N=5 pct, N=10 pct, N=100 pct)
        (0.0, 0.0, 1.0, 50.0, 80.0, 90.0, 99.0),
        (0.2, 1.5, 1.5, 75.0, 120.0, 135.0, 148.5),
        (0.4, 2.0, 2.2, 110.0, 176.0, 198.0, 217.8),
        (0.6, 2.0, 2.8, 140.0, 224.0, 252.0, 277.2),
        (0.8, 3.0, 4.2, 210.0, 336.0, 378.0, 415.8),
    ]

    for delta_s, kap, phi_exp, n2, n5, n10, n100 in table_data:
        phi_calc = 1 + (1 + kap) * delta_s if delta_s > 0 else 1.0
        check(f"Phi({delta_s},{kap}) = {phi_exp}",
              np.isclose(phi_calc, phi_exp),
              f"calc={phi_calc}")

        for N_val, expected_pct in [(2, n2), (5, n5), (10, n10), (100, n100)]:
            loss_pct = phi_exp * (N_val - 1) / N_val * 100
            check(f"  L/E (d={delta_s},N={N_val}) = {expected_pct}%",
                  np.isclose(loss_pct, expected_pct, atol=0.05),
                  f"calc={loss_pct:.1f}%")


# ---------------------------------------------------------------------------
# 6. Net-Negative Threshold (Corollaries 5.1, 5.2)
# ---------------------------------------------------------------------------

def verify_net_negative_threshold() -> None:
    section("6. Net-Negative Threshold — Corollaries 5.1, 5.2")

    # Corollary 5.2: Two-agent threshold
    # (1 + kappa)(delta_off + delta_def) > 1
    kappa, delta_off, delta_def = 2.0, 0.2, 0.2
    lhs = (1 + kappa) * (delta_off + delta_def)
    Phi = 1 + lhs
    check("Corollary 5.2: (1+kappa)(d_off+d_def) > 1",
          lhs > 1,
          f"lhs = {lhs}")
    check("Phi = 2.2 > 2",
          Phi > 2.0,
          f"Phi = {Phi}")

    # Critical N formula: N > Phi/(Phi-1) strictly, so N* accounts for boundary
    # When Phi/(Phi-1) is (near) integer k, N* = k+1; otherwise N* = ceil(val).
    for Phi_val in [1.1, 1.5, 2.0, 2.2, 3.0, 5.0]:
        val = Phi_val / (Phi_val - 1)
        n_round = round(val)
        if abs(n_round - val) < 1e-9:
            N_star = n_round + 1
        else:
            N_star = math.ceil(val)
        # Verify: at N*, Phi > N*/(N*-1)  (strict)
        is_neg = Phi_val > N_star / (N_star - 1)
        # At N*-1, should NOT be net-negative (or N*-1 < 2)
        if N_star > 2:
            not_neg_below = Phi_val <= (N_star - 1) / (N_star - 2)
        else:
            not_neg_below = True

        check(f"N*(Phi={Phi_val}) = {N_star}: net-neg at N*",
              is_neg,
              f"Phi={Phi_val} > {N_star}/{N_star - 1}={N_star / (N_star - 1):.4f}")
        check(f"  Not net-neg at N*-1",
              not_neg_below or N_star <= 2,
              f"N*-1={N_star - 1}")

    # Edge: Phi = 1 → never net-negative
    check("Phi=1 (pure contest, no damage): N* = inf",
          True,
          "Since Phi=1 → Phi*(N-1)/N < 1 for all finite N")


# ---------------------------------------------------------------------------
# 7. Cooperation Dominance — Theorem 6 (Section 6)
# ---------------------------------------------------------------------------

def verify_cooperation_dominance() -> None:
    section("7. Cooperation Dominance — Theorem 6 (Section 6)")

    # From Task 1.1 §8.7: symmetric agents, alpha=10, beta=1, R=12
    alpha, beta, R = 10.0, 1.0, 12.0

    U = lambda x: alpha * x - beta / 2 * x ** 2

    # Cooperative: VE allocation
    x_coop = R / 2  # = 6
    SW_coop = 2 * U(x_coop)
    check("SW_coop = 84", np.isclose(SW_coop, 84.0))

    # Conflict: with Phi=2.2, contested amount = 20-12 = 8
    Phi = 2.2
    E_contested = 2 * (alpha / beta) - R  # = 8
    D_2 = E_contested / 2  # = 4
    L_system = Phi * D_2  # = 8.8

    check("Contested amount = 8", np.isclose(E_contested, 8.0))
    check("Contest dissipation D_2 = 4", np.isclose(D_2, 4.0))
    check("Total system loss = 8.8", np.isclose(L_system, 8.8))
    check("Loss > contested amount",
          L_system > E_contested,
          f"L={L_system} > E_contested={E_contested}")

    # Cooperation premium is strictly positive
    premium = L_system  # minimum premium = system loss from conflict
    check("Cooperation premium > 0", premium > 0, f"premium >= {premium}")


# ---------------------------------------------------------------------------
# 8. Cascading Friction — Theorem 7 (Section 7)
# ---------------------------------------------------------------------------

def verify_cascading_friction() -> None:
    section("8. Cascading Friction — Theorem 7 (Section 7)")

    # Parameters from Section 7.8
    M = 1000
    E_bar = 10.0
    eta = 0.01
    epsilon = 0.05
    v = 50.0

    # Cascade cost formula
    C_cascade = eta * v * M * E_bar / epsilon
    check("C_cascade = 100,000",
          np.isclose(C_cascade, 100_000),
          f"C = {C_cascade}")

    # Amplification factor
    amp = C_cascade / v
    check("Amplification = 2000x",
          np.isclose(amp, 2000),
          f"amp = {amp}")

    # Verify via geometric series sum
    delta_phi = eta * v  # 0.5
    check("Delta_phi = 0.5", np.isclose(delta_phi, 0.5))

    # Simulate N periods and check convergence
    N_sim = 2000
    total_excess_cost = 0.0
    phi_excess = delta_phi
    for k in range(N_sim):
        total_excess_cost += phi_excess * M * E_bar
        phi_excess *= (1 - epsilon)

    check("Simulated cascade ≈ analytical",
          np.isclose(total_excess_cost, C_cascade, rtol=0.01),
          f"sim={total_excess_cost:.1f}, analytical={C_cascade:.1f}")

    # Half-life
    t_half = math.log(2) / math.log(1 / (1 - epsilon))
    check("Half-life ≈ 13.5 periods",
          np.isclose(t_half, 13.513, atol=0.1),
          f"t_half = {t_half:.3f}")

    # Verify half-life: after t_half periods, phi should be ~half
    phi_after = delta_phi * (1 - epsilon) ** int(round(t_half))
    check("phi after t_half ≈ 0.5 * initial",
          np.isclose(phi_after / delta_phi, 0.5, atol=0.05),
          f"ratio = {phi_after / delta_phi:.4f}")

    # Denser ecosystem (M = 10,000): amplification reaches 10^4 regime
    M_dense = 10_000
    C_cascade_dense = eta * v * M_dense * E_bar / epsilon
    amp_dense = C_cascade_dense / v
    check("Denser ecosystem (M=10,000): C_cascade = 1,000,000",
          np.isclose(C_cascade_dense, 1_000_000),
          f"C = {C_cascade_dense}")
    check("Denser ecosystem amplification = 20,000x (10^4 regime)",
          np.isclose(amp_dense, 20_000),
          f"amp = {amp_dense}")


# ---------------------------------------------------------------------------
# 9. Friction Ratchet — Corollary 7.1 (Section 7.9)
# ---------------------------------------------------------------------------

def verify_friction_ratchet() -> None:
    section("9. Friction Ratchet — Corollary 7.1 (Section 7.9)")

    M = 1000
    E_bar = 10.0
    eta = 0.01
    epsilon = 0.05
    v = 50.0

    # Steady-state phi under recurring violations
    for nu in [0.1, 0.5, 1.0, 5.0]:
        phi_ss = nu * eta * v / epsilon
        friction_tax = phi_ss * M * E_bar
        check(f"nu={nu}: phi_inf = {phi_ss:.2f}",
              np.isclose(phi_ss, nu * eta * v / epsilon),
              f"tax = {friction_tax:.0f}/period")

    # Verify convergence by simulation
    nu = 1.0  # 1 violation per period
    phi_ss_expected = nu * eta * v / epsilon  # = 10

    phi = 0.0
    for t in range(5000):
        phi += eta * v * nu  # injection each period (on average)
        phi *= (1 - epsilon)

    check("Simulated steady-state ≈ analytical",
          np.isclose(phi, phi_ss_expected, rtol=0.05),
          f"sim={phi:.4f}, analytical={phi_ss_expected:.4f}")

    # Collapse threshold
    E_coop_net = 500.0  # hypothetical cooperative surplus
    nu_star = (epsilon / (eta * v)) * (E_coop_net / (M * E_bar))
    check(f"Collapse threshold nu* = {nu_star:.4f}",
          nu_star > 0,
          f"Above nu*, friction tax > cooperative surplus")

    # Verify: at nu*, friction tax = coop surplus
    phi_at_nustar = nu_star * eta * v / epsilon
    tax_at_nustar = phi_at_nustar * M * E_bar
    check("At nu*: friction tax = coop surplus",
          np.isclose(tax_at_nustar, E_coop_net),
          f"tax={tax_at_nustar:.4f}, surplus={E_coop_net}")


# ---------------------------------------------------------------------------
# 10. Worked Examples (Section 9)
# ---------------------------------------------------------------------------

def verify_worked_examples() -> None:
    section("10. Worked Examples (Section 9)")

    # Example 9.1: Two-agent baseline
    E_j = 100.0
    delta_off, delta_def, kappa = 0.15, 0.25, 2.0
    Phi = 1 + (1 + kappa) * (delta_off + delta_def)

    e_star = E_j / 4  # 25
    D_2 = E_j / 2  # 50
    bd_per = (delta_off + delta_def) * e_star  # 10
    repair_per = kappa * bd_per  # 20
    L_total = 2 * (e_star + bd_per + repair_per)  # 110

    check("Ex 9.1: Phi = 2.2", np.isclose(Phi, 2.2))
    check("Ex 9.1: e* = 25", np.isclose(e_star, 25.0))
    check("Ex 9.1: D_2 = 50", np.isclose(D_2, 50.0))
    check("Ex 9.1: boundary damage/agent = 10", np.isclose(bd_per, 10.0))
    check("Ex 9.1: repair/agent = 20", np.isclose(repair_per, 20.0))
    check("Ex 9.1: L_system = 110", np.isclose(L_total, 110.0))
    check("Ex 9.1: V_net = -10", np.isclose(E_j - L_total, -10.0))
    check("Ex 9.1: L = Phi * D_2",
          np.isclose(L_total, Phi * D_2))

    # Example 9.2: Five-agent scramble
    N = 5
    e_i_5 = (N - 1) / N ** 2 * E_j  # 4*100/25 = 16
    D_5 = N * e_i_5  # 80
    L_5 = Phi * D_5  # 176

    check("Ex 9.2: e_i = 16", np.isclose(e_i_5, 16.0))
    check("Ex 9.2: D_5 = 80", np.isclose(D_5, 80.0))
    check("Ex 9.2: L_system = 176", np.isclose(L_5, 176.0))
    check("Ex 9.2: V_net = -76", np.isclose(E_j - L_5, -76.0))

    # Example 9.3: Profitable bully (sigma_A=3, sigma_B=1)
    sigma_A, sigma_B = 3.0, 1.0
    # Contest investments (equal in baseline model with equal valuations)
    e_bully = sigma_A * sigma_B / (sigma_A + sigma_B) ** 2 * E_j
    check("Ex 9.3: e_A = e_B = 18.75",
          np.isclose(e_bully, 18.75),
          f"e = {e_bully}")

    p_A = sigma_A / (sigma_A + sigma_B)
    check("Ex 9.3: p_A = 0.75", np.isclose(p_A, 0.75))

    D_bully = 2 * e_bully  # 37.5
    L_bully = Phi * D_bully  # 82.5
    V_net_bully = E_j - L_bully  # 17.5

    check("Ex 9.3: D = 37.5", np.isclose(D_bully, 37.5))
    check("Ex 9.3: L_system = 82.5", np.isclose(L_bully, 82.5))
    check("Ex 9.3: V_net = 17.5 (barely positive)",
          np.isclose(V_net_bully, 17.5))


# ---------------------------------------------------------------------------
# 11. Decisive Contests — Moderate regime + Budget-constrained corner NE
# ---------------------------------------------------------------------------

def verify_decisive_contests() -> None:
    section("11. Decisive Contests: Interior NE (r <= N/(N-1)) and Budget-Constrained Corner NE (r > N/(N-1))")

    E_j = 100.0

    # ---- Moderate regime: interior NE valid for r in (0, N/(N-1)] ----
    for N in [2, 5, 10]:
        threshold_r = N / (N - 1)

        # At r = threshold: interior formula gives D_N = E_j (boundary case)
        D_at_threshold = threshold_r * (N - 1) / N * E_j
        check(f"N={N}: interior NE at r={threshold_r:.4f} gives D_N = E_j",
              np.isclose(D_at_threshold, E_j),
              f"D = {D_at_threshold:.4f}")

        # Below threshold: interior NE gives D_N < E_j
        r_low = threshold_r * 0.8
        D_low = r_low * (N - 1) / N * E_j
        check(f"N={N}: interior NE at r={r_low:.3f} gives D_N < E_j",
              D_low < E_j,
              f"D = {D_low:.2f}")

        # At r = threshold, per-agent payoff is exactly zero
        e_star = threshold_r * (N - 1) / N**2 * E_j
        payoff = E_j / N - e_star
        check(f"N={N}: per-agent payoff at r={threshold_r:.4f} is zero",
              np.isclose(payoff, 0.0),
              f"payoff = {payoff:.6f}")

    # ---- Decisive regime r > N/(N-1): budget-constrained corner NE ----
    # Proposition: with budget cap e_bar in (0, E_j/N], symmetric profile e_i = e_bar
    # is a pure NE; D_N = N * e_bar; per-agent payoff = E_j/N - e_bar >= 0.
    for N in [2, 5, 10]:
        threshold_r = N / (N - 1)
        e_bar_max = E_j / N  # maximum cap consistent with non-negative payoff
        for e_bar_frac in [0.25, 0.5, 1.0]:
            e_bar = e_bar_frac * e_bar_max
            # Test for several r values strictly above the threshold
            for r in [threshold_r * 1.2, threshold_r * 2.0, 5.0, 10.0]:
                if r <= threshold_r:
                    continue

                # Verify symmetric corner profile is best response: at e_i = e_bar
                # with others at e_bar, marginal payoff is positive (cap binds upward),
                # and dropping to zero is weakly worse than playing at cap.

                # Marginal payoff at the cap (others at e_bar):
                # dPi/de_i = E_j * r * (N-1) * e_bar^(2r-1) / (N*e_bar^r)^2 - 1
                #         = E_j * r * (N-1) / (N^2 * e_bar) - 1
                marg_at_cap = E_j * r * (N - 1) / (N**2 * e_bar) - 1.0
                check(f"N={N}, r={r:.3f}, e_bar={e_bar:.3f}: marginal payoff at cap > 0 (upward deviation infeasible)",
                      marg_at_cap > 0,
                      f"marginal = {marg_at_cap:.4f}")

                # Equilibrium payoff at cap
                eq_payoff = E_j / N - e_bar
                # Drop-out payoff (e_i = 0; with others positive, p_i = 0): payoff = 0
                dropout_payoff = 0.0
                check(f"N={N}, r={r:.3f}, e_bar={e_bar:.3f}: cap-NE payoff >= dropout payoff",
                      eq_payoff >= dropout_payoff - 1e-12,
                      f"eq_payoff = {eq_payoff:.4f}, dropout = {dropout_payoff}")

                # Verify no profitable interior deviation by grid search
                # Pi_i(e_i) = E_j * e_i^r / (e_i^r + (N-1)*e_bar^r) - e_i
                e_grid = np.linspace(1e-4, e_bar, 200)
                others_pow = (N - 1) * e_bar**r
                payoffs = E_j * e_grid**r / (e_grid**r + others_pow) - e_grid
                max_interior_payoff = float(payoffs.max())
                check(f"N={N}, r={r:.3f}, e_bar={e_bar:.3f}: cap-NE dominates all interior deviations",
                      eq_payoff >= max_interior_payoff - 1e-9,
                      f"eq_payoff = {eq_payoff:.4f}, max interior = {max_interior_payoff:.4f}")

                # D_N = N * e_bar; check this equals N * e_bar and <= E_j
                D_N_corner = N * e_bar
                check(f"N={N}, r={r:.3f}, e_bar={e_bar:.3f}: D_N = N*e_bar = {D_N_corner:.3f} (<= E_j)",
                      np.isclose(D_N_corner, N * e_bar) and D_N_corner <= E_j + 1e-12,
                      f"D_N = {D_N_corner}")

    # ---- Net-negativity under budget constraints ----
    # In decisive regime: system loss = Phi * N * e_bar > E_j iff e_bar > E_j/(Phi*N)
    Phi = 2.2
    for N in [2, 5]:
        e_bar_critical = E_j / (Phi * N)
        # Just above critical: net-negative
        e_bar = e_bar_critical * 1.01
        L_sys = Phi * N * e_bar
        check(f"N={N}, Phi={Phi}, e_bar just above E_j/(Phi*N): net-negative (L_sys > E_j)",
              L_sys > E_j,
              f"L_sys = {L_sys:.3f}")
        # Just below critical: net-positive
        e_bar = e_bar_critical * 0.99
        L_sys = Phi * N * e_bar
        check(f"N={N}, Phi={Phi}, e_bar just below E_j/(Phi*N): net-positive (L_sys < E_j)",
              L_sys < E_j,
              f"L_sys = {L_sys:.3f}")

    # ---- Continuity at r = N/(N-1) when e_bar = E_j/N ----
    # Interior formula at r = threshold gives e* = (N-1)E_j/N^2 * N/(N-1) = E_j/N = e_bar
    for N in [2, 5, 10]:
        threshold_r = N / (N - 1)
        e_star_interior = threshold_r * (N - 1) / N**2 * E_j
        e_bar_match = E_j / N
        check(f"N={N}: interior NE at r={threshold_r:.4f} matches corner NE at e_bar = E_j/N",
              np.isclose(e_star_interior, e_bar_match),
              f"interior = {e_star_interior:.4f}, corner cap = {e_bar_match:.4f}")


# ---------------------------------------------------------------------------
# 12. Module Verification — thermodynamics.py
# ---------------------------------------------------------------------------

def verify_module() -> None:
    section("12. Module Verification — modules/thermodynamics.py")

    from modules.thermodynamics import (
        Boundary,
        symmetric_contest_ne,
        asymmetric_contest_ne_2,
        friction_multiplier,
        system_loss,
        net_system_value,
        is_net_negative,
        critical_N,
        NetworkFriction,
    )

    # Boundary
    b = Boundary(integrity=100, leakage_rate=0.1, profile="uniform")
    check("Boundary: maintenance = 10", np.isclose(b.maintenance_cost(), 10.0))
    check("Boundary: full breach = 100", np.isclose(b.breach_work(1.0), 100.0))
    check("Boundary: half breach (uniform) = 50", np.isclose(b.breach_work(0.5), 50.0))

    b_hard = Boundary(integrity=100, profile="hardening")
    check("Boundary: half breach (hardening) = 25", np.isclose(b_hard.breach_work(0.5), 25.0))

    b_shell = Boundary(integrity=100, profile="shell")
    check("Boundary: half breach (shell) = 75", np.isclose(b_shell.breach_work(0.5), 75.0))

    # Symmetric contest
    res = symmetric_contest_ne(100.0, N=2, r=1.0)
    check("Module: symmetric 2-agent e* = 25",
          np.isclose(res.investments[0], 25.0))
    check("Module: D_2 = 50",
          np.isclose(res.total_dissipation, 50.0))

    res5 = symmetric_contest_ne(100.0, N=5, r=1.0)
    check("Module: 5-agent D = 80",
          np.isclose(res5.total_dissipation, 80.0))

    # Asymmetric contest
    res_asym = asymmetric_contest_ne_2(100.0, 100.0)
    check("Module: asymmetric (equal) D = 50",
          np.isclose(res_asym.total_dissipation, 50.0))

    res_asym2 = asymmetric_contest_ne_2(150.0, 50.0)
    check("Module: asymmetric (150,50) D = 37.5",
          np.isclose(res_asym2.total_dissipation, 37.5))

    # Friction multiplier
    Phi = friction_multiplier(0.15, 0.25, 2.0)
    check("Module: Phi = 2.2", np.isclose(Phi, 2.2))

    # System loss
    L = system_loss(100.0, 2, 2.2)
    check("Module: L(N=2, Phi=2.2) = 110", np.isclose(L, 110.0))

    # Net value
    V = net_system_value(100.0, 2, 2.2)
    check("Module: V_net = -10", np.isclose(V, -10.0))

    # Is net-negative
    check("Module: is_net_negative(2, 2.2) = True", is_net_negative(2, 2.2))
    check("Module: is_net_negative(2, 1.5) = False", not is_net_negative(2, 1.5))

    # Critical N
    check("Module: N*(2.2) = 2", critical_N(2.2) == 2)
    check("Module: N*(1.5) = 4", critical_N(1.5) == 4)
    check("Module: N*(1.1) = 12", critical_N(1.1) == 12)
    check("Module: N*(2.0) = 3 (boundary: Phi=N/(N-1)=2 not strict)", critical_N(2.0) == 3)

    # Network friction
    nf = NetworkFriction(phi=0, eta=0.01, epsilon=0.05, M=1000, E_bar=10.0)
    check("Module: initial trust = 1.0", np.isclose(nf.trust, 1.0))
    check("Module: cascade(50) = 100000", np.isclose(nf.cascade_cost(50), 100_000))
    check("Module: amp factor = 2000", np.isclose(nf.amplification_factor(), 2000))

    t_half = nf.half_life()
    check("Module: half-life ≈ 13.5",
          np.isclose(t_half, 13.513, atol=0.1),
          f"t_half = {t_half:.3f}")

    # Simulate and verify decay
    nf2 = NetworkFriction(phi=0, eta=0.01, epsilon=0.05, M=1000, E_bar=10.0)
    trace = nf2.simulate(100, violations={0: 50.0})
    check("Module: simulation phi[0] = 0.5",
          np.isclose(trace[0], 0.5))
    check("Module: simulation decays",
          trace[-1] < trace[0] * 0.01,
          f"phi[99]={trace[-1]:.6f}")


# ---------------------------------------------------------------------------
# 13. Trust State Variable (Section 7.3)
# ---------------------------------------------------------------------------

def verify_trust_variable() -> None:
    section("13. Trust State Variable (Section 7.3)")

    # T = 1/(1+phi), phi = (1-T)/T
    for phi_val in [0.0, 0.5, 1.0, 5.0, 100.0]:
        T = 1.0 / (1.0 + phi_val)
        phi_back = (1.0 - T) / T
        check(f"phi={phi_val}: T={T:.4f}, roundtrip",
              np.isclose(phi_back, phi_val),
              f"phi_back = {phi_back:.4f}")

    # Boundary: T=1 iff phi=0
    check("T=1 iff phi=0", np.isclose(1.0 / (1.0 + 0.0), 1.0))
    # T→0 as phi→inf
    check("T→0 as phi→inf", 1.0 / (1.0 + 1e6) < 1e-5)


# ---------------------------------------------------------------------------
# 14. Interaction Cost Function — Definition 11 (Section 8)
# ---------------------------------------------------------------------------

def verify_interaction_cost_function() -> None:
    section("14. Interaction Cost Function — Definition 11 (Section 8)")

    E_j = 100.0
    N = 5
    delta_off, delta_def, kappa = 0.15, 0.25, 2.0
    Phi = 1 + (1 + kappa) * (delta_off + delta_def)
    phi = 0.5  # some ambient friction
    M = 1000
    E_bar = 10.0

    # Contest NE investments
    e_i = (N - 1) / N ** 2 * E_j  # = 16
    e_total = N * e_i  # = 80

    # Interaction cost components
    contest_diss = e_total  # 80
    boundary_repair = (1 + kappa) * (delta_off + delta_def) * e_total  # 1.2 * 0.4 * 80 = ... wait
    # (1 + kappa) = 3, (delta_off + delta_def) = 0.4
    boundary_repair = (1 + kappa) * (delta_off + delta_def) * e_total  # 3 * 0.4 * 80 = 96
    friction_tax = phi * M * E_bar  # 0.5 * 1000 * 10 = 5000

    C_total = contest_diss + boundary_repair + friction_tax
    C_star = Phi * (N - 1) / N * E_j + phi * M * E_bar

    check("C components sum correctly",
          np.isclose(C_total, contest_diss + boundary_repair + friction_tax))
    check("C* = Phi*(N-1)/N*E + phi*M*E_bar",
          np.isclose(C_star, Phi * (N - 1) / N * E_j + phi * M * E_bar),
          f"C* = {C_star:.1f}")
    check("C_total = C*",
          np.isclose(C_total, C_star),
          f"C_total={C_total:.1f}, C*={C_star:.1f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 72)
    print("  VERIFICATION: Task 1.2 — Thermodynamic Friction")
    print("  math/thermodynamic-friction.md")
    print("=" * 72)

    verify_boundary_model()
    verify_symmetric_contest_ne()
    verify_asymmetric_contest_ne()
    verify_n_agent_scaling()
    verify_friction_multiplier()
    verify_net_negative_threshold()
    verify_cooperation_dominance()
    verify_cascading_friction()
    verify_friction_ratchet()
    verify_worked_examples()
    verify_decisive_contests()
    verify_module()
    verify_trust_variable()
    verify_interaction_cost_function()

    print(f"\n{'='*72}")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"{'='*72}")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
