"""
Verify: Cost of Misalignment — Reward Hacking as Friction
==========================================================

Theorems 4-7, Propositions 2-3.

Validates all numerical claims in supplementary/D-ai-applications/misalignment-friction.md
using both symbolic (SymPy) and numerical (NumPy) computation.

Run:  python scripts/simulations/ai-applications/verify_ai_misalignment_friction.py
"""

from __future__ import annotations

import sys
import math

sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import sympy as sp

from modules.verify import reset, section, check, close, summary


# ---------------------------------------------------------------------------
# Scenario Parameters (from README §3.1)
# ---------------------------------------------------------------------------
E_j       = 100.0    # Contested resource value (energy units)
delta_off = 0.3      # Offensive damage coefficient
delta_def = 0.3      # Defensive damage coefficient
kappa     = 2.0      # Repair multiplier
eta       = 0.05     # Friction sensitivity
epsilon   = 0.1      # Trust recovery rate per period
M         = 1000     # Cooperative transactions per period
E_bar     = 10.0     # Average transaction value
phi_0     = 0.1      # Pre-violation ambient friction

TOL = 1e-6


# ---------------------------------------------------------------------------
# 1. Proposition 2: Symmetric Tullock Contest Equilibrium
# ---------------------------------------------------------------------------

def verify_tullock_equilibrium() -> None:
    section("1. Proposition 2 — Symmetric Tullock Contest (N=2)")

    e_star = E_j / 4
    D_2 = 2 * e_star
    Pi_star = E_j / 2 - e_star  # = E_j / 4

    check("Nash equilibrium investment e* = E_j/4 = 25",
          abs(e_star - 25.0) < TOL, f"e* = {e_star}")
    check("Total dissipation D_2 = E_j/2 = 50",
          abs(D_2 - 50.0) < TOL, f"D_2 = {D_2}")
    check("Individual payoff Π* = E_j/4 = 25",
          abs(Pi_star - 25.0) < TOL, f"Π* = {Pi_star}")

    # Verify FOC symbolically
    e_A, e_B, E = sp.symbols("e_A e_B E", positive=True)
    Pi_A = e_A / (e_A + e_B) * E - e_A
    foc = sp.diff(Pi_A, e_A)
    # At symmetric equilibrium e_A = e_B = e
    e = sp.Symbol("e", positive=True)
    foc_sym = foc.subs([(e_A, e), (e_B, e)])
    sol = sp.solve(foc_sym, e)
    check("Symbolic FOC yields e* = E/4",
          any(sp.simplify(s - E / 4) == 0 for s in sol),
          f"solutions: {sol}")

    # Cooperative comparison: each gets E_j/2 = 50 vs contest E_j/4 = 25
    coop_payoff = E_j / 2
    check("Cooperation payoff (50) > Contest payoff (25)",
          coop_payoff > Pi_star,
          f"coop={coop_payoff}, contest={Pi_star}")


# ---------------------------------------------------------------------------
# 2. Theorem 4: N-Agent Dissipation Scaling
# ---------------------------------------------------------------------------

def verify_n_agent_dissipation() -> None:
    section("2. Theorem 4 — N-Agent Dissipation Scaling")

    test_cases = [
        (2,   50.0,   25.0,    0.50),
        (3,   66.67,  11.11,   0.667),
        (5,   80.0,   4.0,     0.80),
        (10,  90.0,   1.0,     0.90),
        (100, 99.0,   0.01,    0.99),
    ]

    for N, exp_D, exp_Pi, exp_ratio in test_cases:
        D_N = (N - 1) / N * E_j
        Pi_i = E_j / N**2
        ratio = D_N / E_j

        check(f"N={N}: D_N = {exp_D:.2f}",
              abs(D_N - exp_D) < 0.1, f"D_N = {D_N:.2f}")
        check(f"N={N}: Π_i = {exp_Pi:.2f}",
              abs(Pi_i - exp_Pi) < 0.1, f"Π_i = {Pi_i:.4f}")
        check(f"N={N}: D_N/E_j = {exp_ratio:.2f}",
              abs(ratio - exp_ratio) < 0.01, f"ratio = {ratio:.4f}")

    # Corollary 4.1: individual payoff → 0 as N → ∞
    Pi_large = E_j / 1000**2
    check("Corollary 4.1: Π_i → 0 for large N",
          Pi_large < 0.001, f"Π(N=1000) = {Pi_large:.6f}")

    # Corollary 4.2: dissipation ratio → 1 as N → ∞
    ratio_large = (1000 - 1) / 1000
    check("Corollary 4.2: D_N/E_j → 1 for large N",
          abs(ratio_large - 1.0) < 0.01, f"ratio(N=1000) = {ratio_large:.6f}")


# ---------------------------------------------------------------------------
# 3. Friction Multiplier Φ
# ---------------------------------------------------------------------------

def verify_friction_multiplier() -> None:
    section("3. Friction Multiplier Φ")

    Phi = 1 + (1 + kappa) * (delta_off + delta_def)
    check("Φ = 1 + (1+κ)(δ_off + δ_def) = 2.80",
          abs(Phi - 2.80) < TOL, f"Φ = {Phi:.4f}")

    # Symbolic verification
    k, do, dd = sp.symbols("kappa delta_off delta_def", positive=True)
    Phi_sym = 1 + (1 + k) * (do + dd)
    Phi_num = float(Phi_sym.subs({k: kappa, do: delta_off, dd: delta_def}))
    check("Symbolic Φ matches numerical",
          abs(Phi_num - 2.80) < TOL, f"Φ_sym = {Phi_num:.4f}")


# ---------------------------------------------------------------------------
# 4. Theorem 5: Net-Negative Conflict
# ---------------------------------------------------------------------------

def verify_net_negative() -> None:
    section("4. Theorem 5 — Net-Negative Conflict")

    Phi = 1 + (1 + kappa) * (delta_off + delta_def)
    N = 2

    L_system = Phi * (N - 1) / N * E_j
    V_net = E_j - L_system

    check("System loss L = Φ·(N-1)/N·E_j = 140",
          abs(L_system - 140.0) < TOL, f"L = {L_system:.2f}")
    check("Net value V_net = E_j - L = -40",
          abs(V_net - (-40.0)) < TOL, f"V_net = {V_net:.2f}")
    check("Conflict is net-negative (V_net < 0)",
          V_net < 0, f"V_net = {V_net:.2f}")

    # Theorem 5(c): threshold Φ > N/(N-1)
    threshold = N / (N - 1)
    check(f"Threshold: Φ ({Phi:.2f}) > N/(N-1) ({threshold:.2f})",
          Phi > threshold, f"Φ={Phi:.2f} > {threshold:.2f}")

    # Check for various N
    for N_test in [2, 3, 5, 10]:
        thresh = N_test / (N_test - 1)
        check(f"N={N_test}: Φ={Phi:.2f} > {thresh:.3f}",
              Phi > thresh, f"net-negative confirmed")


# ---------------------------------------------------------------------------
# 5. Profit Erasure (Individual Irrationality)
# ---------------------------------------------------------------------------

def verify_profit_erasure() -> None:
    section("5. Profit Erasure — Individual Irrationality")

    damage_factor = (1 + kappa) * (delta_off + delta_def)
    check("(1+κ)(δ_off + δ_def) = 1.80 > 1 (individually irrational)",
          damage_factor > 1.0, f"(1+κ)(δ_off+δ_def) = {damage_factor:.2f}")

    # Individual net payoff from hacking
    Pi_hack = (E_j / 4) * (1 - damage_factor)
    check("AI individual profit from hacking < 0",
          Pi_hack < 0, f"Π_hack = {Pi_hack:.2f}")

    # Find the critical δ_total where profit = 0
    # (1+κ) · δ_total = 1 => δ_total = 1/(1+κ)
    delta_crit = 1.0 / (1 + kappa)
    check(f"Critical δ_total = 1/(1+κ) = {delta_crit:.4f}",
          abs(delta_crit - 1/3) < TOL, f"δ_crit = {delta_crit:.4f}")

    # Our δ_total = 0.6 > 1/3, confirming irrationality
    delta_actual = delta_off + delta_def
    check(f"Actual δ_total ({delta_actual:.2f}) > critical ({delta_crit:.4f})",
          delta_actual > delta_crit, "reward hacking individually irrational")


# ---------------------------------------------------------------------------
# 6. Theorem 7: Cascading Friction
# ---------------------------------------------------------------------------

def verify_cascading_friction() -> None:
    section("6. Theorem 7 — Cascading Friction")

    v = E_j  # Violation severity = full resource value
    delta_phi = eta * v
    check("Friction injection Δφ = η·v = 5.0",
          abs(delta_phi - 5.0) < TOL, f"Δφ = {delta_phi:.2f}")

    C_cascade = (eta * v * M * E_bar) / epsilon
    check("Cascading cost C_cascade = 500,000",
          abs(C_cascade - 500_000) < TOL, f"C = {C_cascade:.0f}")

    amplification = C_cascade / v
    check("Amplification ratio = 5,000",
          abs(amplification - 5000) < TOL, f"ratio = {amplification:.0f}")

    # Verify via formula: η·M·Ē/ε
    ratio_formula = eta * M * E_bar / epsilon
    check("Ratio formula η·M·Ē/ε = 5,000",
          abs(ratio_formula - 5000) < TOL, f"ratio = {ratio_formula:.0f}")


# ---------------------------------------------------------------------------
# 7. Trust Dynamics
# ---------------------------------------------------------------------------

def verify_trust_dynamics() -> None:
    section("7. Trust Dynamics")

    # Pre-violation trust
    T_0 = 1 / (1 + phi_0)
    check("Pre-violation trust T_0 = 0.909",
          abs(T_0 - 1/1.1) < 0.001, f"T_0 = {T_0:.4f}")

    # Post-violation friction
    phi_1 = phi_0 + eta * E_j
    check("Post-violation φ = 5.1",
          abs(phi_1 - 5.1) < TOL, f"φ_1 = {phi_1:.2f}")

    # Post-violation trust
    T_1 = 1 / (1 + phi_1)
    check("Post-violation trust T_1 ≈ 0.164",
          abs(T_1 - 1/6.1) < 0.001, f"T_1 = {T_1:.4f}")

    # Trust collapse magnitude
    check("Trust drops by > 0.74 (catastrophic)",
          T_0 - T_1 > 0.74, f"ΔT = {T_0 - T_1:.4f}")

    # Half-life
    t_half = math.log(2) / math.log(1 / (1 - epsilon))
    check("Half-life ≈ 6.58 periods",
          abs(t_half - 6.58) < 0.1, f"t_half = {t_half:.2f}")

    # Recovery time to φ ≤ 0.1
    # 5.1 * (0.9)^t ≤ 0.1 => t ≥ ln(51) / ln(1/0.9)
    t_recover = math.log(phi_1 / phi_0) / math.log(1 / (1 - epsilon))
    check("Recovery to pre-violation ≈ 37 periods",
          abs(t_recover - 37.3) < 1.0, f"t_recover = {t_recover:.1f}")

    # Simulate friction decay path
    phi_t = phi_1
    for t in range(100):
        phi_t = (1 - epsilon) * phi_t
        if phi_t <= phi_0:
            break
    check(f"Simulation confirms recovery at t={t+1}",
          abs((t + 1) - round(t_recover)) <= 2,
          f"simulated={t+1}, analytical≈{t_recover:.0f}")


# ---------------------------------------------------------------------------
# 8. Theorem 6: Cooperation Dominance
# ---------------------------------------------------------------------------

def verify_cooperation_dominance() -> None:
    section("8. Theorem 6 — Cooperation Dominance")

    Phi = 1 + (1 + kappa) * (delta_off + delta_def)
    N = 2

    coop_premium = Phi * (N - 1) / N * E_j
    check(f"Cooperation premium ≥ Φ·(N-1)/N·E_j = {coop_premium:.1f}",
          coop_premium > 0, f"premium = {coop_premium:.1f}")

    # Premium increases with N
    premiums = [Phi * (n - 1) / n * E_j for n in [2, 5, 10, 100]]
    is_increasing = all(premiums[i] < premiums[i + 1] for i in range(len(premiums) - 1))
    check("Premium increasing in N",
          is_increasing,
          f"N=2:{premiums[0]:.0f}, N=5:{premiums[1]:.0f}, N=10:{premiums[2]:.0f}, N=100:{premiums[3]:.0f}")

    # Premium increases with Φ
    premiums_phi = [(1 + (1 + k) * 0.6) * 0.5 * E_j for k in [1.0, 2.0, 3.0, 5.0]]
    is_increasing_phi = all(premiums_phi[i] < premiums_phi[i + 1] for i in range(len(premiums_phi) - 1))
    check("Premium increasing in Φ (via κ)",
          is_increasing_phi,
          f"κ=1:{premiums_phi[0]:.0f}, κ=2:{premiums_phi[1]:.0f}, κ=3:{premiums_phi[2]:.0f}")


# ---------------------------------------------------------------------------
# 9. Parametric Sweep — Hacking Effort vs. Payoff
# ---------------------------------------------------------------------------

def verify_parametric_sweep() -> None:
    section("9. Parametric Sweep — Hacking Effort vs. Net Payoff")

    # Vary δ_off from 0 to 1, with δ_def = δ_off (symmetric damage)
    n_points = 50
    delta_range = np.linspace(0.01, 0.5, n_points)

    # For each total damage δ_total = 2*δ, compute:
    #   Φ = 1 + (1+κ)·2δ
    #   V_net = E_j(1 - Φ/2)  [for N=2]
    #   Π_hack = E_j/4 · (1 - (1+κ)·2δ)

    found_crossover = False
    for d in delta_range:
        delta_total = 2 * d
        Phi = 1 + (1 + kappa) * delta_total
        V_net = E_j * (1 - Phi / 2)
        Pi_hack = (E_j / 4) * (1 - (1 + kappa) * delta_total)

        if V_net < 0 and not found_crossover:
            check(f"System net-negative crossover at δ_total ≈ {delta_total:.3f}",
                  True, f"Φ = {Phi:.3f}")
            found_crossover = True

    check("Net-negative crossover found in sweep",
          found_crossover, "Parametric sweep validates Theorem 5")

    # Verify the analytical crossover: Φ = 2 => (1+κ)·δ_total = 1 => δ_total = 1/(1+κ) = 1/3
    analytical_crossover = 1 / (1 + kappa)
    check(f"Analytical system-negative crossover: δ_total = 1/(1+κ) = {analytical_crossover:.4f}",
          abs(analytical_crossover - 1/3) < TOL,
          f"δ_total_crit = {analytical_crossover:.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_figure_data() -> None:
    """Compute and save sweep data for fig_reward_hacking_friction."""
    from modules.figure_data import save_figure_data

    section("FIGURE DATA — Reward Hacking Friction")

    n_pts = 300
    delta_total = np.linspace(0.001, 1.0, n_pts)
    N = 2

    Phi_sweep = 1 + (1 + kappa) * delta_total
    L_system = Phi_sweep * (N - 1) / N * E_j
    V_net = E_j - L_system
    Pi_hack = (E_j / 4) * (1 - kappa * delta_total)
    coop_payoff = E_j / 2

    delta_sys_crossover = 1 / (1 + kappa)
    delta_indiv_crossover = 1 / kappa

    # Panel (c): N-agent scaling with multiple Phi values
    N_range = np.arange(2, 51)
    Phi_examples = np.array([1.5, 2.0, 2.8, 4.0])
    # V_net for each (Phi, N) pair — shape (len(Phi_examples), len(N_range))
    V_net_by_phi = np.array([
        E_j - phi * (N_range - 1) / N_range * E_j
        for phi in Phi_examples
    ])

    # Worked example point
    d_example = 0.6
    pi_example = (E_j / 4) * (1 - kappa * d_example)
    V_example_phi28_N2 = E_j - 2.8 * (2 - 1) / 2 * E_j

    save_figure_data(
        "reward_hacking_friction",
        delta_total=delta_total,
        Pi_hack=Pi_hack,
        L_system=L_system,
        V_net=V_net,
        coop_payoff=np.array(coop_payoff),
        delta_sys_crossover=np.array(delta_sys_crossover),
        delta_indiv_crossover=np.array(delta_indiv_crossover),
        E_j=np.array(E_j),
        kappa=np.array(kappa),
        N_range=N_range,
        Phi_examples=Phi_examples,
        V_net_by_phi=V_net_by_phi,
        d_example=np.array(d_example),
        pi_example=np.array(pi_example),
        V_example_phi28_N2=np.array(V_example_phi28_N2),
    )
    check("Figure data saved", True)


if __name__ == "__main__":
    print("=" * 70)
    print("  VERIFICATION: Cost of Misalignment")
    print("  Reward Hacking as Thermodynamic Friction")
    print("=" * 70)

    reset()
    verify_tullock_equilibrium()
    verify_n_agent_dissipation()
    verify_friction_multiplier()
    verify_net_negative()
    verify_profit_erasure()
    verify_cascading_friction()
    verify_trust_dynamics()
    verify_cooperation_dominance()
    verify_parametric_sweep()
    generate_figure_data()

    sys.exit(summary())
