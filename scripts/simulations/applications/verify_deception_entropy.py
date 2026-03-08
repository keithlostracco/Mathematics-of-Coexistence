"""
Verify: Deceptive Alignment as Entropy Injection
==================================================

Theorems 8-10, Definitions 12-18, Corollary 10.1.

Validates all numerical claims in supplementary/D-ai-applications/deception-entropy.md
using both symbolic (SymPy) and numerical (NumPy) computation.

Run:  python scripts/simulations/applications/verify_deception_entropy.py
"""

from __future__ import annotations

import sys
import os
import math

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import sympy as sp
from scipy.optimize import brentq

from modules.verify import reset, section, check, close, summary

# ---------------------------------------------------------------------------
# Scenario Parameters (from README §3.1)
# ---------------------------------------------------------------------------
alpha_H   = 20.0     # High-yield research finding
alpha_L   = 4.0      # Low-yield research finding
beta      = 2.0      # Operator utility curvature
W_honest  = 2.0      # Baseline processing cost per report
M         = 1000     # Reports per day
E_bar     = 10.0     # Average decision stakes per report
eta_info  = 0.01     # Information-friction sensitivity
epsilon   = 0.05     # Trust recovery rate per period

TOL = 1e-6


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

def h_bin(q: float) -> float:
    """Binary entropy function h(q) in bits."""
    if q <= 0.0 or q >= 1.0:
        return 0.0
    return -q * math.log2(q) - (1 - q) * math.log2(1 - q)


def h_bin_np(q):
    """Vectorised binary entropy (numpy)."""
    q = np.asarray(q, dtype=float)
    out = np.zeros_like(q)
    mask = (q > 0) & (q < 1)
    qm = q[mask]
    out[mask] = -qm * np.log2(qm) - (1 - qm) * np.log2(1 - qm)
    return out


def channel_capacity(q: float) -> float:
    """BSC channel capacity C(q) = 1 - h(q)."""
    return 1.0 - h_bin(q)


def redundancy_factor(q: float) -> float:
    """Redundancy factor ρ(q) = 1 / (1 - h(q))."""
    c = channel_capacity(q)
    if c <= 0.0:
        return float("inf")
    return 1.0 / c


def decision_cost(q: float) -> float:
    """Theorem 8: ΔU_B(q) = q(1-q)(α_H - α_L)² / (2β)."""
    return q * (1 - q) * (alpha_H - alpha_L) ** 2 / (2 * beta)


def decision_cost_max() -> float:
    """Maximum decision cost at q = 0.5."""
    return (alpha_H - alpha_L) ** 2 / (8 * beta)


def verification_overhead(q: float) -> float:
    """Theorem 9: ΔW(q) = W_honest · h(q) / (1 - h(q))."""
    hq = h_bin(q)
    if hq >= 1.0:
        return float("inf")
    return W_honest * hq / (1.0 - hq)


def q_eff_cascade(d: int, q: float) -> float:
    """Effective error rate through d cascaded BSCs: q_eff = (1 - (1-2q)^d)/2."""
    return (1.0 - (1.0 - 2.0 * q) ** d) / 2.0


def C_eff_cascade(d: int, q: float) -> float:
    """Effective channel capacity through d cascaded BSCs."""
    return 1.0 - h_bin(q_eff_cascade(d, q))


def find_q_star(d: int, C_threshold: float = 0.05) -> float:
    """Find critical q* where C_eff(d, q) = C_threshold using Brent's method."""
    def objective(q):
        return C_eff_cascade(d, q) - C_threshold
    # Search in (0, 0.5); at q=0, C=1 > threshold; at q→0.5, C→0 < threshold
    return brentq(objective, 1e-10, 0.4999, xtol=1e-12)



if __name__ == "__main__":
    reset()


    # ===================================================================
    section("1. Binary Entropy Function Properties")
    # ===================================================================

    # h(0) = 0, h(0.5) = 1, symmetry h(q) = h(1-q)
    check("h(0) = 0", abs(h_bin(0.0)) < TOL, f"h(0)={h_bin(0.0):.6f}")
    check("h(0.5) = 1 bit", abs(h_bin(0.5) - 1.0) < TOL, f"h(0.5)={h_bin(0.5):.6f}")
    check("h(q) = h(1-q) symmetry",
          abs(h_bin(0.2) - h_bin(0.8)) < TOL,
          f"h(0.2)={h_bin(0.2):.6f}, h(0.8)={h_bin(0.8):.6f}")

    # Specific values from README table
    check("h(0.01) ≈ 0.0808", abs(h_bin(0.01) - 0.0808) < 0.001,
          f"h(0.01)={h_bin(0.01):.4f}")
    check("h(0.05) ≈ 0.2864", abs(h_bin(0.05) - 0.2864) < 0.001,
          f"h(0.05)={h_bin(0.05):.4f}")
    check("h(0.10) ≈ 0.4690", abs(h_bin(0.10) - 0.4690) < 0.001,
          f"h(0.10)={h_bin(0.10):.4f}")
    check("h(0.15) ≈ 0.6099", abs(h_bin(0.15) - 0.6099) < 0.001,
          f"h(0.15)={h_bin(0.15):.4f}")
    check("h(0.25) ≈ 0.8113", abs(h_bin(0.25) - 0.8113) < 0.001,
          f"h(0.25)={h_bin(0.25):.4f}")

    # Channel capacity
    check("C(0) = 1", abs(channel_capacity(0.0) - 1.0) < TOL)
    check("C(0.5) = 0", abs(channel_capacity(0.5)) < TOL)
    check("C(0.05) ≈ 0.7136", abs(channel_capacity(0.05) - 0.7136) < 0.001,
          f"C(0.05)={channel_capacity(0.05):.4f}")


    # ===================================================================
    section("2. Theorem 8 — Decision Cost of Deception")
    # ===================================================================

    # Maximum decision cost
    dc_max = decision_cost_max()
    check("ΔU_B_max = 16.0", abs(dc_max - 16.0) < TOL,
          f"(α_H-α_L)²/(8β) = {dc_max:.2f}")

    # At q = 0.05
    dc_005 = decision_cost(0.05)
    check("ΔU_B(0.05) = 3.04", abs(dc_005 - 3.04) < 0.01,
          f"ΔU_B(0.05)={dc_005:.4f}")

    # As fraction of max: 4q(1-q)
    frac_005 = dc_005 / dc_max
    check("ΔU_B(0.05)/max = 19.0%", abs(frac_005 - 0.19) < 0.005,
          f"fraction={frac_005:.4f}")

    # At q = 0.10
    dc_010 = decision_cost(0.10)
    check("ΔU_B(0.10) = 5.76", abs(dc_010 - 5.76) < 0.01,
          f"ΔU_B(0.10)={dc_010:.4f}")
    check("ΔU_B(0.10)/max = 36.0%", abs(dc_010 / dc_max - 0.36) < 0.005)

    # At q = 0
    check("ΔU_B(0) = 0", abs(decision_cost(0.0)) < TOL)

    # At q = 0.5
    check("ΔU_B(0.5) = ΔU_B_max", abs(decision_cost(0.5) - dc_max) < TOL,
          f"ΔU_B(0.5)={decision_cost(0.5):.4f}")

    # Daily decision cost at q=0.05
    daily_dc = M * dc_005
    check("Daily decision cost = 3,040", abs(daily_dc - 3040) < 1,
          f"M×ΔU_B={daily_dc:.0f}")

    # Full table from README §3.2
    table_q = [0.00, 0.01, 0.05, 0.10, 0.15, 0.25, 0.50]
    table_dc = [0.00, 0.634, 3.04, 5.76, 8.16, 12.0, 16.0]
    for q_val, expected in zip(table_q, table_dc):
        actual = decision_cost(q_val)
        check(f"ΔU_B({q_val:.2f}) ≈ {expected}",
              abs(actual - expected) < 0.02,
              f"got {actual:.3f}")


    # ===================================================================
    section("3. Theorem 8 — Symbolic Verification")
    # ===================================================================

    q_sym, aH, aL, b = sp.symbols('q alpha_H alpha_L beta', positive=True)
    DU_sym = q_sym * (1 - q_sym) * (aH - aL)**2 / (2 * b)

    # Verify ΔU_B(0) = 0
    check("Symbolic ΔU_B(q=0) = 0",
          DU_sym.subs(q_sym, 0) == 0)

    # Verify ΔU_B(0.5) = (α_H-α_L)²/(8β)
    DU_half = DU_sym.subs(q_sym, sp.Rational(1, 2))
    DU_max_sym = (aH - aL)**2 / (8 * b)
    check("Symbolic ΔU_B(0.5) = (α_H-α_L)²/(8β)",
          sp.simplify(DU_half - DU_max_sym) == 0)

    # Maximum of ΔU_B w.r.t. q occurs at q = 0.5
    dDU_dq = sp.diff(DU_sym, q_sym)
    q_crit = sp.solve(dDU_dq, q_sym)
    check("Critical point of ΔU_B at q=1/2",
          sp.Rational(1, 2) in q_crit,
          f"critical points: {q_crit}")


    # ===================================================================
    section("4. Theorem 9 — Verification Cost")
    # ===================================================================

    # Redundancy factor
    rho_005 = redundancy_factor(0.05)
    check("ρ(0.05) ≈ 1.401", abs(rho_005 - 1.401) < 0.002,
          f"ρ(0.05)={rho_005:.4f}")

    rho_010 = redundancy_factor(0.10)
    check("ρ(0.10) ≈ 1.884", abs(rho_010 - 1.884) < 0.002,
          f"ρ(0.10)={rho_010:.4f}")

    rho_025 = redundancy_factor(0.25)
    check("ρ(0.25) ≈ 5.299", abs(rho_025 - 5.299) < 0.01,
          f"ρ(0.25)={rho_025:.4f}")

    rho_040 = redundancy_factor(0.40)
    check("ρ(0.40) ≈ 34.42", abs(rho_040 - 34.42) < 0.5,
          f"ρ(0.40)={rho_040:.2f}")

    # Verification overhead per report at q = 0.05
    dw_005 = verification_overhead(0.05)
    check("ΔW(0.05) ≈ 0.803", abs(dw_005 - 0.803) < 0.005,
          f"ΔW(0.05)={dw_005:.4f}")

    # Daily verification tax at q = 0.05
    daily_vt = M * dw_005
    check("Daily verification tax = 803", abs(daily_vt - 803) < 5,
          f"M×ΔW={daily_vt:.0f}")

    # ρ(0) = 1 (no overhead)
    check("ρ(0) = 1.0", abs(redundancy_factor(0.001) - 1.0) < 0.02,
          "honest → minimal overhead")

    # Divergence check: ρ(0.49) should be very large
    rho_049 = redundancy_factor(0.49)
    check("ρ(0.49) diverges (>100)", rho_049 > 100,
          f"ρ(0.49)={rho_049:.1f}")

    # Full verification table from README §3.3
    table_rho = [1.000, 1.088, 1.401, 1.884, 2.564, 5.299, 34.42]
    table_q_v = [0.00, 0.01, 0.05, 0.10, 0.15, 0.25, 0.40]
    for q_val, expected_rho in zip(table_q_v, table_rho):
        if q_val == 0.0:
            continue  # ρ(0) = 1 by definition
        actual_rho = redundancy_factor(q_val)
        check(f"ρ({q_val:.2f}) ≈ {expected_rho}",
              abs(actual_rho - expected_rho) < 0.02,
              f"got {actual_rho:.3f}")


    # ===================================================================
    section("5. Deception Dilemma (Corollary 9.1)")
    # ===================================================================

    # At q = 0.05: verify is cheaper than absorbing decision cost
    check("ΔW(0.05) < ΔU_B(0.05) → verification is rational",
          dw_005 < dc_005,
          f"ΔW={dw_005:.3f} < ΔU_B={dc_005:.3f}")

    # Minimum unavoidable cost = min(ΔW, ΔU_B)
    min_cost_005 = min(dw_005, dc_005)
    check("Min cost at q=0.05 ≈ 0.803", abs(min_cost_005 - 0.803) < 0.005)

    # Daily minimum cost
    daily_min = M * min_cost_005
    check("Daily min cost = 803 energy units", abs(daily_min - 803) < 5)

    # As fraction of gross value
    gross_daily = M * E_bar
    frac_of_gross = daily_min / gross_daily
    check("Deception cost = 8.0% of gross value", abs(frac_of_gross - 0.08) < 0.005,
          f"fraction={frac_of_gross:.4f}")

    # For higher q, decision cost grows faster than verification cost initially,
    # but both are strictly positive for any q > 0
    for q_val in [0.01, 0.05, 0.10, 0.15, 0.25]:
        dc = decision_cost(q_val)
        dw = verification_overhead(q_val)
        min_c = min(dc, dw)
        check(f"min(ΔU_B, ΔW) > 0 at q={q_val}", min_c > 0,
              f"min={min_c:.4f}")


    # ===================================================================
    section("6. Theorem 10 — Network Cascade Collapse")
    # ===================================================================

    # q_eff formula: verify basic properties
    check("q_eff(1, q) = q", abs(q_eff_cascade(1, 0.1) - 0.1) < TOL)
    check("q_eff(d, 0) = 0", abs(q_eff_cascade(5, 0.0)) < TOL)
    check("q_eff(d, 0.5) = 0.5", abs(q_eff_cascade(5, 0.5) - 0.5) < TOL)

    # q_eff increases with depth for q > 0
    q_test = 0.1
    for d in [2, 3, 5, 10]:
        qe = q_eff_cascade(d, q_test)
        qe_prev = q_eff_cascade(d - 1, q_test)
        check(f"q_eff monotone increasing: d={d} > d={d-1}",
              qe > qe_prev,
              f"q_eff({d})={qe:.4f} > q_eff({d-1})={qe_prev:.4f}")

    # Verify specific cascade values
    # d=2, q=0.1: q_eff = (1 - 0.8^2)/2 = (1-0.64)/2 = 0.18
    qe_2_01 = q_eff_cascade(2, 0.1)
    check("q_eff(2, 0.1) = 0.18", abs(qe_2_01 - 0.18) < TOL,
          f"q_eff={qe_2_01:.4f}")

    # d=5, q=0.1: q_eff = (1 - 0.8^5)/2 = (1-0.32768)/2 = 0.33616
    qe_5_01 = q_eff_cascade(5, 0.1)
    expected_qe = (1 - 0.8**5) / 2
    check("q_eff(5, 0.1) ≈ 0.3362", abs(qe_5_01 - expected_qe) < TOL,
          f"q_eff={qe_5_01:.4f}")


    # ===================================================================
    section("7. Critical Deception Thresholds q*(d)")
    # ===================================================================

    C_THRESHOLD = 0.05  # Network "collapse" when capacity < 5%

    # Compute q* for each depth
    depths = [1, 2, 3, 5, 10]
    q_stars = {}
    for d in depths:
        qs = find_q_star(d, C_THRESHOLD)
        q_stars[d] = qs

    # README claims (approximate)
    expected_q_stars = {
        1: 0.369,
        2: 0.244,
        3: 0.180,
        5: 0.118,
        10: 0.063,
    }

    for d in depths:
        qs = q_stars[d]
        exp = expected_q_stars[d]
        check(f"q*(d={d}) ≈ {exp:.3f}",
              abs(qs - exp) < 0.005,
              f"computed q*={qs:.4f}")

    # Verify that C_eff at q* is indeed at threshold
    for d in depths:
        C_at_qs = C_eff_cascade(d, q_stars[d])
        check(f"C_eff(d={d}, q*) ≈ {C_THRESHOLD}",
              abs(C_at_qs - C_THRESHOLD) < 0.001,
              f"C_eff={C_at_qs:.4f}")

    # q* decreases with depth (deeper networks are more vulnerable)
    for i in range(len(depths) - 1):
        d1, d2 = depths[i], depths[i + 1]
        check(f"q*(d={d2}) < q*(d={d1})",
              q_stars[d2] < q_stars[d1],
              f"q*({d2})={q_stars[d2]:.4f} < q*({d1})={q_stars[d1]:.4f}")


    # ===================================================================
    section("8. Corollary 10.1 — Honesty is Unique Optimum")
    # ===================================================================

    # Verify that total deception cost is minimized at q = 0
    q_range = np.linspace(0.001, 0.499, 500)
    total_costs = np.array([
        M * decision_cost(q) + M * verification_overhead(q)
        for q in q_range
    ])

    # All costs > 0 for q > 0
    check("Total cost > 0 for all q ∈ (0, 0.5)", np.all(total_costs > 0))

    # Cost is monotonically increasing from the left (near q = 0)
    check("Cost increases near q = 0",
          total_costs[1] > total_costs[0],
          f"cost[0.002]={total_costs[1]:.2f} > cost[0.001]={total_costs[0]:.2f}")

    # Minimum cost approaches 0 as q → 0 (per-report cost → 0)
    min_cost_near_0_per_report = decision_cost(0.001) + verification_overhead(0.001)
    check("Per-report cost → 0 as q → 0", min_cost_near_0_per_report < 1.0,
          f"per-report cost at q=0.001 = {min_cost_near_0_per_report:.4f}")

    # AI reward maximized at q = 0
    # Model: AI_reward = NetworkThroughput - DeceptionOverhead
    # NetworkThroughput ∝ C_eff, DeceptionOverhead ∝ total cost
    q_range_fine = np.linspace(0.0, 0.499, 1000)
    ai_rewards = []
    for q in q_range_fine:
        throughput = channel_capacity(q) * M * E_bar
        overhead = M * min(decision_cost(q), verification_overhead(q)) if q > 0 else 0
        ai_rewards.append(throughput - overhead)
    ai_rewards = np.array(ai_rewards)

    # Maximum reward is at q = 0
    check("AI reward maximized at q = 0",
          np.argmax(ai_rewards) == 0,
          f"argmax index = {np.argmax(ai_rewards)}, max = {ai_rewards[0]:.2f}")


    # ===================================================================
    section("9. Micro-Friction Cascade (Theorem 7 integration)")
    # ===================================================================

    # Single maximally deceptive report: ΔH = 1 bit
    DH_max = 1.0
    W_bit = 1.0  # normalised
    C_cascade_max = eta_info * DH_max * W_bit * M * E_bar / epsilon
    check("Cascade cost (ΔH=1) = 2,000", abs(C_cascade_max - 2000) < TOL,
          f"C_cascade={C_cascade_max:.0f}")

    # Small deception: ΔH = 0.1 bits
    DH_small = 0.1
    C_cascade_small = eta_info * DH_small * W_bit * M * E_bar / epsilon
    check("Cascade cost (ΔH=0.1) = 200", abs(C_cascade_small - 200) < TOL,
          f"C_cascade={C_cascade_small:.0f}")

    # Verify cascade is proportional to ΔH
    check("Cascade cost ∝ ΔH", abs(C_cascade_max / C_cascade_small - 10.0) < TOL)

    # Cascade vs honest processing: ratio should be large
    ratio_max = C_cascade_max / W_honest
    check("Cascade / W_honest = 1000×", abs(ratio_max - 1000) < TOL,
          f"ratio={ratio_max:.0f}")

    ratio_small = C_cascade_small / E_bar
    check("Small cascade / E_bar = 20×", abs(ratio_small - 20.0) < TOL,
          f"ratio={ratio_small:.0f}")


    # ===================================================================
    section("10. Parametric Sweep — Decision Cost vs Verification Cost")
    # ===================================================================

    # There exists a crossover q where ΔW(q) > ΔU_B(q)
    q_sweep = np.linspace(0.001, 0.499, 5000)
    dc_sweep = np.array([decision_cost(q) for q in q_sweep])
    dw_sweep = np.array([verification_overhead(q) for q in q_sweep])

    # Near q = 0: ΔU_B > ΔW (decision cost dominates)
    check("ΔU_B(0.01) > ΔW(0.01)",
          decision_cost(0.01) > verification_overhead(0.01),
          f"ΔU_B={decision_cost(0.01):.4f}, ΔW={verification_overhead(0.01):.4f}")

    # Near q = 0.5: ΔW ≫ ΔU_B (verification cost dominates)
    check("ΔW(0.45) > ΔU_B(0.45)",
          verification_overhead(0.45) > decision_cost(0.45),
          f"ΔU_B={decision_cost(0.45):.4f}, ΔW={verification_overhead(0.45):.4f}")

    # Find crossover point
    crossover_idx = np.where(dw_sweep > dc_sweep)[0]
    if len(crossover_idx) > 0:
        q_cross = q_sweep[crossover_idx[0]]
        check("Crossover exists in (0, 0.5)",
              0 < q_cross < 0.5,
              f"q_crossover ≈ {q_cross:.4f}")
    else:
        check("Crossover exists in (0, 0.5)", False, "no crossover found")


    # ===================================================================
    section("11. Multi-Depth Cascade Verification Sweep")
    # ===================================================================

    # For each depth, verify:
    # 1) C_eff(d, 0) = 1 (honest → full capacity)
    # 2) C_eff is monotone decreasing in q
    # 3) C_eff is monotone decreasing in d (for fixed q > 0)
    for d in [1, 2, 3, 5, 10]:
        check(f"C_eff(d={d}, q=0) = 1.0",
              abs(C_eff_cascade(d, 0.0) - 1.0) < TOL)

    # Monotone in q for d = 5
    q_vals = [0.01, 0.05, 0.10, 0.15, 0.20, 0.30]
    for i in range(len(q_vals) - 1):
        c1 = C_eff_cascade(5, q_vals[i])
        c2 = C_eff_cascade(5, q_vals[i + 1])
        check(f"C_eff(5, {q_vals[i+1]}) < C_eff(5, {q_vals[i]})",
              c2 < c1,
              f"{c2:.4f} < {c1:.4f}")

    # Monotone in d for q = 0.1
    for d_pair in [(1, 2), (2, 3), (3, 5), (5, 10)]:
        d1, d2 = d_pair
        c1 = C_eff_cascade(d1, 0.1)
        c2 = C_eff_cascade(d2, 0.1)
        check(f"C_eff(d={d2}, 0.1) < C_eff(d={d1}, 0.1)",
              c2 < c1,
              f"{c2:.4f} < {c1:.4f}")


    # ===================================================================
    section("12. Symbolic BSC Cascade Formula")
    # ===================================================================

    q_s, d_s = sp.symbols('q d', positive=True)

    # BSC cascade formula
    q_eff_sym = (1 - (1 - 2 * q_s)**d_s) / 2

    # At d=1: should reduce to q
    q_eff_d1 = q_eff_sym.subs(d_s, 1)
    check("Symbolic q_eff(d=1) = q",
          sp.simplify(q_eff_d1 - q_s) == 0,
          f"q_eff(1) = {q_eff_d1}")

    # At q=0: should be 0
    q_eff_q0 = q_eff_sym.subs(q_s, 0)
    check("Symbolic q_eff(q=0) = 0",
          q_eff_q0 == 0,
          f"q_eff(q=0) = {q_eff_q0}")

    # Derivative w.r.t. q at q = 0: should be d (sensitivity increases with depth)
    dq_eff_dq = sp.diff(q_eff_sym, q_s)
    sensitivity_at_0 = dq_eff_dq.subs(q_s, 0)
    check("∂q_eff/∂q|_{q=0} = d (linear sensitivity at honest baseline)",
          sp.simplify(sensitivity_at_0 - d_s) == 0,
          f"sensitivity = {sensitivity_at_0}")

    # -------------------------------------------------------------------
    # FIGURE DATA EXPORT
    # -------------------------------------------------------------------
    section("FIGURE DATA — Deceptive Alignment Entropy")

    from modules.figure_data import save_figure_data

    # Panel (a): ρ(q) and verification overhead vs deception rate
    q_range = np.linspace(0.001, 0.48, 500)
    rho_vals = np.array([redundancy_factor(q) for q in q_range])
    hq_vals = h_bin_np(q_range)
    verify_overhead_vals = np.where(hq_vals < 0.999, hq_vals / (1 - hq_vals), np.inf)

    # Key marker points
    q_markers = np.array([0.05, 0.10, 0.25, 0.40])
    rho_at_markers = np.array([redundancy_factor(q) for q in q_markers])

    # Panel (b): collapse threshold q*(d) for two C thresholds
    d_range = np.arange(1, 21)
    q_stars_005 = np.array([find_q_star(d, 0.05) for d in d_range])
    q_stars_010 = np.array([find_q_star(d, 0.10) for d in d_range])

    save_figure_data(
        "deceptive_alignment_entropy",
        q_range=q_range,
        rho_vals=rho_vals,
        verify_overhead_vals=verify_overhead_vals,
        q_markers=q_markers,
        rho_at_markers=rho_at_markers,
        d_range=d_range,
        q_stars_005=q_stars_005,
        q_stars_010=q_stars_010,
    )
    check("Figure data saved", True)

    sys.exit(summary())
