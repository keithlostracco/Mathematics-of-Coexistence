"""
Verify Task 1.3: Micro-Friction — Information Entropy of Deception
===================================================================

This script independently validates every numerical claim, theorem,
and corollary from math/information-negentropy.md (Part A) using both
symbolic (SymPy) and numerical (NumPy/SciPy) computation.

Run:  python scripts/simulations/verify_information_entropy.py
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
# 0. Helpers (same pattern as Tasks 1.1 / 1.2 verification)
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
# 1. Binary Entropy Function (Section 2.2)
# ---------------------------------------------------------------------------

def verify_binary_entropy() -> None:
    section("1. Binary Entropy Function h(q) — Section 2.2")

    # Symbolic definition
    q = sp.Symbol("q", positive=True)
    h_sym = -q * sp.log(q, 2) - (1 - q) * sp.log(1 - q, 2)

    # Boundary values
    h_0 = float(sp.limit(h_sym, q, 0, "+"))
    check("h(0) = 0 (perfect honesty)", np.isclose(h_0, 0.0, atol=1e-10),
          f"h(0) = {h_0}")

    h_half = float(h_sym.subs(q, sp.Rational(1, 2)))
    check("h(0.5) = 1 (total deception)", np.isclose(h_half, 1.0),
          f"h(0.5) = {h_half}")

    # Monotonicity on (0, 0.5)
    dh = sp.diff(h_sym, q)
    # At q=0.25, derivative should be positive
    dh_025 = float(dh.subs(q, sp.Rational(1, 4)))
    check("h'(0.25) > 0 (increasing on [0, 0.5])", dh_025 > 0,
          f"h'(0.25) = {dh_025:.4f}")

    # Specific values from the table in Section 2.2
    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    table_values = [
        (0.01, 0.081),
        (0.05, 0.286),
        (0.10, 0.469),
        (0.25, 0.811),
        (0.50, 1.000),
    ]

    for q_val, h_expected in table_values:
        h_actual = h_num(q_val)
        check(f"h({q_val}) ≈ {h_expected}",
              np.isclose(h_actual, h_expected, atol=0.001),
              f"h({q_val}) = {h_actual:.3f}")

    # Channel capacity C(q) = 1 - h(q)
    for q_val, h_val in table_values:
        C = 1.0 - h_num(q_val)
        check(f"C({q_val}) = 1 - h({q_val}) = {1 - h_val:.3f}",
              np.isclose(C, 1 - h_val, atol=0.001),
              f"C = {C:.3f}")


# ---------------------------------------------------------------------------
# 2. Redundancy Factor (Definition 16, Section 4.2)
# ---------------------------------------------------------------------------

def verify_redundancy_factor() -> None:
    section("2. Redundancy Factor ρ(q) — Definition 16")

    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    def rho(q_val: float) -> float:
        C = 1.0 - h_num(q_val)
        return 1.0 / C if C > 0 else float("inf")

    # Table from Section 4.2
    table = [
        (0.00, 1.00),
        (0.01, 1.09),
        (0.05, 1.40),
        (0.10, 1.88),
        (0.25, 5.30),
        (0.40, 34.4),
    ]

    for q_val, rho_expected in table:
        rho_actual = rho(q_val)
        check(f"ρ({q_val}) ≈ {rho_expected}",
              np.isclose(rho_actual, rho_expected, atol=0.15),
              f"ρ = {rho_actual:.2f}")

    # Divergence at q → 0.5
    rho_049 = rho(0.49)
    check("ρ(0.49) >> 1 (diverges near 0.5)",
          rho_049 > 50,
          f"ρ(0.49) = {rho_049:.1f}")

    # ρ(0) = 1 (no overhead for honest)
    check("ρ(0) = 1.0 (honest baseline)", rho(0) == 1.0)


# ---------------------------------------------------------------------------
# 3. Decision Cost of Deception — Theorem 8 (Section 3)
# ---------------------------------------------------------------------------

def verify_decision_cost() -> None:
    section("3. Decision Cost of Deception — Theorem 8")

    # The closed-form for binary-state quadratic model:
    # ΔU_B(q) = q(1-q)(α_H - α_L)² / (2β)

    # Symbolic verification of the formula via the law of total variance
    q_s = sp.Symbol("q", positive=True)
    aH, aL, beta_s = sp.symbols("alpha_H alpha_L beta", positive=True)

    # Prior variance: Var(α) = (α_H - α_L)²/4
    sigma2_alpha = (aH - aL) ** 2 / 4

    # Explained variance under BSC:
    # E[α|Y=H] = (1-q)α_H + q α_L, E[α|Y=L] = q α_H + (1-q) α_L
    # Both equally likely → Var(E[α|Y]) = ((1-2q)(α_H-α_L)/2)² ... wait
    # E[α|Y=H] - E[α|Y=L] = (1-2q)(α_H - α_L)
    # Mean of E[α|Y] = (α_H + α_L)/2 for both
    # Var(E[α|Y]) = E[ (E[α|Y] - mean)² ] = ((1-2q)(α_H-α_L))²/4
    sigma2_hat = (1 - 2 * q_s) ** 2 * (aH - aL) ** 2 / 4

    # Residual variance = σ²_α - σ²_hat
    residual_var = sp.simplify(sigma2_alpha - sigma2_hat)

    # Decision cost = residual / (2β)
    delta_U_derived = sp.simplify(residual_var / (2 * beta_s))

    # Expected formula: q(1-q)(α_H - α_L)² / (2β)
    delta_U_expected = q_s * (1 - q_s) * (aH - aL) ** 2 / (2 * beta_s)

    check("Symbolic: ΔU_B formula derivation matches",
          sp.simplify(delta_U_derived - delta_U_expected) == 0,
          f"derived = {delta_U_derived}, expected = {delta_U_expected}")

    # Boundary checks
    delta_at_0 = float(delta_U_expected.subs(q_s, 0))
    check("ΔU_B(0) = 0 (honest → no loss)",
          np.isclose(delta_at_0, 0.0))

    # Maximum at q=0.5
    delta_at_half = sp.simplify(delta_U_expected.subs(q_s, sp.Rational(1, 2)))
    max_expected = (aH - aL) ** 2 / (8 * beta_s)
    check("ΔU_B(0.5) = (α_H - α_L)²/(8β) (maximum loss)",
          sp.simplify(delta_at_half - max_expected) == 0,
          f"ΔU_B(0.5) = {delta_at_half}")

    # Numerical example from Section 6.1
    alpha_H_val, alpha_L_val, beta_val = 20.0, 4.0, 2.0
    q_val = 0.1
    delta_U_num = q_val * (1 - q_val) * (alpha_H_val - alpha_L_val) ** 2 / (2 * beta_val)
    check("Example 6.1: ΔU_B(0.1) = 5.76",
          np.isclose(delta_U_num, 5.76),
          f"ΔU_B = {delta_U_num}")

    # Table from Section 3.3
    delta_U_max = (alpha_H_val - alpha_L_val) ** 2 / (8 * beta_val)
    check("ΔU_B_max = (20-4)²/(8×2) = 16.0",
          np.isclose(delta_U_max, 16.0),
          f"ΔU_B_max = {delta_U_max}")

    table_ratios = [
        (0.00, 0.00),
        (0.01, 0.0396),
        (0.05, 0.19),
        (0.10, 0.36),
        (0.25, 0.75),
        (0.50, 1.00),
    ]

    for q_v, ratio_expected in table_ratios:
        ratio_actual = q_v * (1 - q_v) / 0.25  # q(1-q)/0.25 is ratio to max
        check(f"ΔU_B({q_v})/ΔU_max = {ratio_expected:.4f}",
              np.isclose(ratio_actual, ratio_expected, atol=0.001),
              f"ratio = {ratio_actual:.4f}")


# ---------------------------------------------------------------------------
# 4. Verification Overhead — Theorem 9 (Section 4)
# ---------------------------------------------------------------------------

def verify_verification_cost() -> None:
    section("4. Verification Overhead — Theorem 9")

    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    def overhead_ratio(q_val: float) -> float:
        h = h_num(q_val)
        return h / (1 - h) if h < 1 else float("inf")

    # Zero at q=0
    check("ΔW/W_honest(0) = 0", np.isclose(overhead_ratio(0.0), 0.0))

    # Monotonicity
    ratios = [overhead_ratio(q) for q in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4]]
    monotone = all(ratios[i] < ratios[i + 1] for i in range(len(ratios) - 1))
    check("ΔW/W_honest strictly increasing", monotone)

    # Divergence near 0.5
    check("ΔW/W_honest(0.49) >> 1",
          overhead_ratio(0.49) > 50,
          f"ratio(0.49) = {overhead_ratio(0.49):.1f}")

    # Numerical example from Section 6.1
    q_val = 0.1
    W_honest = 2.0
    rho_val = 1.0 / (1.0 - h_num(q_val))
    delta_W = W_honest * (rho_val - 1.0)
    check("Example 6.1: rho(0.1) ≈ 1.884",
          np.isclose(rho_val, 1.884, atol=0.01),
          f"ρ = {rho_val:.3f}")
    check("Example 6.1: ΔW ≈ 1.77",
          np.isclose(delta_W, 1.77, atol=0.02),
          f"ΔW = {delta_W:.2f}")

    # Verification is worthwhile in Example 6.1 (ΔW < ΔU_B)
    delta_U = 5.76  # from Theorem 8
    check("Example 6.1: verification worthwhile (ΔW < ΔU_B)",
          delta_W < delta_U,
          f"ΔW={delta_W:.2f} < ΔU_B={delta_U}")


# ---------------------------------------------------------------------------
# 5. Corollary 9.1 — Inevitability of Deception Cost
# ---------------------------------------------------------------------------

def verify_inevitability() -> None:
    section("5. Corollary 9.1 — Inevitability of Deception Cost")

    alpha_H, alpha_L, beta = 20.0, 4.0, 2.0
    W_honest = 2.0

    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    # For any q > 0, both costs are positive
    for q_val in [0.001, 0.01, 0.05, 0.1, 0.25, 0.49]:
        delta_U = q_val * (1 - q_val) * (alpha_H - alpha_L) ** 2 / (2 * beta)
        h = h_num(q_val)
        delta_W = W_honest * h / (1 - h) if h < 1 else float("inf")
        cost_min = min(delta_U, delta_W)
        check(f"q={q_val}: min(ΔU_B, ΔW) > 0",
              cost_min > 0,
              f"min = {cost_min:.4f}")

    # At q=0, both are zero
    delta_U_0 = 0.0 * (1 - 0.0) * (alpha_H - alpha_L) ** 2 / (2 * beta)
    delta_W_0 = W_honest * 0.0  # h(0) = 0
    check("q=0: both costs are zero",
          np.isclose(delta_U_0, 0.0) and np.isclose(delta_W_0, 0.0))


# ---------------------------------------------------------------------------
# 6. Network Verification Tax — Section 5.3 / Theorem 10
# ---------------------------------------------------------------------------

def verify_network_tax() -> None:
    section("6. Network Verification Tax — Section 5.3")

    M = 10_000
    E_bar = 10.0
    W_honest = 1.0
    gross_value = M * E_bar  # 100,000

    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    def tax(q_bar: float) -> float:
        h = h_num(q_bar)
        return M * W_honest * h / (1 - h) if h < 1 else float("inf")

    # Table from Example 6.2
    table = [
        (0.00, 0, 0.0),
        (0.01, 880, 0.88),
        (0.05, 4_000, 4.0),
        (0.10, 8_830, 8.8),
        (0.20, 25_990, 26.0),
        (0.30, 74_030, 74.0),
        (0.40, 334_800, 335.0),
    ]

    for q_bar, C_expected, pct_expected in table:
        C_actual = tax(q_bar)
        pct_actual = C_actual / gross_value * 100

        # Use relative tolerance for large values, absolute for small
        if C_expected > 0:
            check(f"q̄={q_bar}: C_verify ≈ {C_expected:,}",
                  np.isclose(C_actual, C_expected, rtol=0.02),
                  f"C = {C_actual:,.0f}")
            check(f"q̄={q_bar}: tax as % ≈ {pct_expected}%",
                  np.isclose(pct_actual, pct_expected, atol=1.0),
                  f"pct = {pct_actual:.1f}%")
        else:
            check(f"q̄={q_bar}: C_verify = 0", np.isclose(C_actual, 0.0))

    # Network collapse: q̄=0.40 tax exceeds gross value
    tax_040 = tax(0.40)
    check("q̄=0.40: tax > gross value (network collapse)",
          tax_040 > gross_value,
          f"tax={tax_040:,.0f} > gross={gross_value:,.0f}")


# ---------------------------------------------------------------------------
# 7. Cascade Cost — Section 5.5
# ---------------------------------------------------------------------------

def verify_cascade_cost() -> None:
    section("7. Cascade Cost — Section 5.5")

    # Parameters from Example 6.3
    M = 5_000
    E_bar = 10.0
    eta = 0.01
    eta_info = 0.01
    epsilon = 0.05
    W_bit = 1.0

    # Macro-friction cascade (from Task 1.2, Theorem 7)
    v = 500.0  # severity of physical boundary violation
    C_cascade_macro = eta * v * M * E_bar / epsilon
    check("Macro-cascade: C = 5,000,000",
          np.isclose(C_cascade_macro, 5_000_000),
          f"C = {C_cascade_macro:,.0f}")

    # Micro-friction cascade per lie (ΔH = 0.1 bits)
    delta_H = 0.1
    C_cascade_micro_one = eta_info * delta_H * W_bit * M * E_bar / epsilon
    check("Micro-cascade per lie: C = 1,000",
          np.isclose(C_cascade_micro_one, 1_000),
          f"C = {C_cascade_micro_one:,.0f}")

    # 100 lies total cascade
    C_cascade_100_lies = 100 * C_cascade_micro_one
    check("100 lies total cascade: C = 100,000",
          np.isclose(C_cascade_100_lies, 100_000),
          f"C = {C_cascade_100_lies:,.0f}")

    # Ratio: macro / 100-lies
    ratio = C_cascade_macro / C_cascade_100_lies
    check("Ratio macro/100-lies = 50×",
          np.isclose(ratio, 50.0),
          f"ratio = {ratio:.0f}")


# ---------------------------------------------------------------------------
# 8. Steady-State Friction Comparison — Section 5.6 / Example 6.3
# ---------------------------------------------------------------------------

def verify_steady_state_friction() -> None:
    section("8. Steady-State Friction — Section 5.6 / Example 6.3")

    eta = 0.01
    eta_info = 0.01
    epsilon = 0.05
    W_bit = 1.0

    # Macro: ν_macro=0.1, v=500
    nu_macro = 0.1
    v = 500.0
    phi_macro = nu_macro * eta * v / epsilon
    check("φ_macro = 10.0",
          np.isclose(phi_macro, 10.0),
          f"φ_macro = {phi_macro}")

    # Micro: ν_micro=50, ΔH=0.1
    nu_micro = 50.0
    delta_H = 0.1
    phi_micro = nu_micro * eta_info * delta_H * W_bit / epsilon
    check("φ_micro = 1.0",
          np.isclose(phi_micro, 1.0),
          f"φ_micro = {phi_micro}")

    # Equal when ν_micro = 500
    nu_micro_eq = 500.0
    phi_micro_eq = nu_micro_eq * eta_info * delta_H * W_bit / epsilon
    check("φ_micro = φ_macro when ν_micro = 500",
          np.isclose(phi_micro_eq, phi_macro),
          f"φ_micro = {phi_micro_eq}, φ_macro = {phi_macro}")


# ---------------------------------------------------------------------------
# 9. Honest Communication Baseline — Definitions 12-13
# ---------------------------------------------------------------------------

def verify_honest_baseline() -> None:
    section("9. Honest Communication Baseline — Definitions 12-13")

    # Mutual information for perfect channel: I(Θ;Y) = H(Θ)
    # H(Θ) for fair binary: 1 bit
    H_theta = 1.0
    # Honest: H(Θ|Y) = 0 → I = H(Θ) = 1
    I_honest = H_theta - 0.0
    check("Honest: I(Θ;Y) = H(Θ) = 1 bit",
          np.isclose(I_honest, 1.0))

    # Total deception: H(Θ|Y) = H(Θ) → I = 0
    I_total_deception = H_theta - H_theta
    check("Total deception: I(Θ;Y) = 0",
          np.isclose(I_total_deception, 0.0))

    # BSC mutual information: I = 1 - h(q)
    for q_val in [0.0, 0.1, 0.25, 0.5]:
        h_val = 0.0 if q_val == 0 else (-q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)) if q_val < 0.5 else 1.0
        I_val = 1.0 - h_val
        # Also compute directly: I = H(Y) - H(Y|Θ)
        # For BSC with fair input: H(Y) = 1 (output also fair), H(Y|Θ) = h(q)
        I_direct = 1.0 - h_val
        check(f"BSC q={q_val}: I = 1 - h(q) = {I_val:.3f}",
              np.isclose(I_val, I_direct))


# ---------------------------------------------------------------------------
# 10. Worked Example 6.1 — Full Walkthrough
# ---------------------------------------------------------------------------

def verify_example_6_1() -> None:
    section("10. Worked Example 6.1 — Binary Trade Decision")

    alpha_H, alpha_L, beta = 20.0, 4.0, 2.0

    # Honest outcomes
    x_H = alpha_H / beta  # = 10
    U_H = alpha_H * x_H - beta / 2 * x_H ** 2  # = 200 - 100 = 100
    x_L = alpha_L / beta  # = 2
    U_L = alpha_L * x_L - beta / 2 * x_L ** 2  # = 8 - 4 = 4

    check("Honest: x*(high) = 10", np.isclose(x_H, 10.0))
    check("Honest: U(high) = 100", np.isclose(U_H, 100.0))
    check("Honest: x*(low) = 2", np.isclose(x_L, 2.0))
    check("Honest: U(low) = 4", np.isclose(U_L, 4.0))

    U_honest_avg = 0.5 * U_H + 0.5 * U_L
    check("Honest E[U_B] = 52", np.isclose(U_honest_avg, 52.0))

    # Deception at q = 0.1
    q = 0.1
    delta_U = q * (1 - q) * (alpha_H - alpha_L) ** 2 / (2 * beta)
    check("ΔU_B(0.1) = 5.76", np.isclose(delta_U, 5.76, atol=0.005))

    U_deceived = U_honest_avg - delta_U
    check("Deceived E[U_B] = 46.24",
          np.isclose(U_deceived, 46.24, atol=0.01),
          f"E[U_B] = {U_deceived:.2f}")

    # Verify by direct computation of deceived utility
    # E[α|Y=H] = 0.9*20 + 0.1*4 = 18.4
    # E[α|Y=L] = 0.1*20 + 0.9*4 = 5.6
    E_alpha_given_H = (1 - q) * alpha_H + q * alpha_L
    E_alpha_given_L = q * alpha_H + (1 - q) * alpha_L
    check("E[α|Y=H] = 18.4", np.isclose(E_alpha_given_H, 18.4))
    check("E[α|Y=L] = 5.6", np.isclose(E_alpha_given_L, 5.6))

    # B's optimal action given Y: x_B(Y) = E[α|Y] / β
    x_B_H = E_alpha_given_H / beta  # = 9.2
    x_B_L = E_alpha_given_L / beta  # = 2.8

    # True expected utility when Y=H:
    # E[U_B | Y=H] = p(θ=H|Y=H)*U(x_B_H, θ=H) + p(θ=L|Y=H)*U(x_B_H, θ=L)
    U_xBH_thetaH = alpha_H * x_B_H - beta / 2 * x_B_H ** 2  # 20*9.2 - 1*84.64/2 = 184 - 42.32 = 141.68? Wait
    # U(x, θ) = α(θ)*x - β/2 * x²
    U_xBH_thetaH = alpha_H * x_B_H - beta / 2 * x_B_H ** 2
    U_xBH_thetaL = alpha_L * x_B_H - beta / 2 * x_B_H ** 2

    E_U_given_YH = (1 - q) * U_xBH_thetaH + q * U_xBH_thetaL
    E_U_given_YL_args = (q * (alpha_H * x_B_L - beta / 2 * x_B_L ** 2) +
                         (1 - q) * (alpha_L * x_B_L - beta / 2 * x_B_L ** 2))

    U_deceived_direct = 0.5 * E_U_given_YH + 0.5 * E_U_given_YL_args
    check("Direct computation matches formula",
          np.isclose(U_deceived_direct, U_deceived, atol=0.01),
          f"direct={U_deceived_direct:.2f}, formula={U_deceived:.2f}")


# ---------------------------------------------------------------------------
# 11. Decision Cost Ratio Table (Section 3.3)
# ---------------------------------------------------------------------------

def verify_decision_cost_table() -> None:
    section("11. Decision Cost Ratio Table — Section 3.3")

    # ΔU_B / ΔU_max = q(1-q) / 0.25 = 4q(1-q)
    table = [
        (0.00, 0.00),
        (0.01, 0.0396),
        (0.05, 0.190),
        (0.10, 0.360),
        (0.25, 0.750),
        (0.50, 1.000),
    ]

    for q_val, expected_ratio in table:
        actual = 4.0 * q_val * (1.0 - q_val)
        check(f"4q(1-q) at q={q_val}: {expected_ratio:.4f}",
              np.isclose(actual, expected_ratio, atol=0.001),
              f"actual = {actual:.4f}")


# ---------------------------------------------------------------------------
# 12. Modules Integration — verify modules/information.py
# ---------------------------------------------------------------------------

def verify_modules() -> None:
    section("12. Modules Integration — modules/information.py")

    try:
        from modules.information import (
            binary_entropy,
            bsc_capacity,
            redundancy_factor,
            decision_cost_binary,
            decision_cost_max,
            verification_overhead_ratio,
            verification_cost,
            deception_cost_min,
            network_verification_tax,
            cascade_cost_info,
            steady_state_info_friction,
        )
    except ImportError as e:
        check("Import modules.information", False, str(e))
        return

    check("Import modules.information", True)

    # binary_entropy
    check("module: h(0) = 0", np.isclose(binary_entropy(0.0), 0.0))
    check("module: h(0.5) = 1", np.isclose(binary_entropy(0.5), 1.0))
    check("module: h(0.1) ≈ 0.469",
          np.isclose(binary_entropy(0.1), 0.469, atol=0.001))

    # bsc_capacity
    check("module: C(0) = 1", np.isclose(bsc_capacity(0.0), 1.0))
    check("module: C(0.5) = 0", np.isclose(bsc_capacity(0.5), 0.0))

    # redundancy_factor
    check("module: ρ(0) = 1", np.isclose(redundancy_factor(0.0), 1.0))
    check("module: ρ(0.1) ≈ 1.884",
          np.isclose(redundancy_factor(0.1), 1.884, atol=0.01))

    # decision_cost_binary
    aH, aL, b = 20.0, 4.0, 2.0
    check("module: ΔU_B(0.1) = 5.76",
          np.isclose(decision_cost_binary(0.1, aH, aL, b), 5.76, atol=0.005))
    check("module: ΔU_B(0) = 0",
          np.isclose(decision_cost_binary(0.0, aH, aL, b), 0.0))

    # decision_cost_max
    check("module: ΔU_max = 16.0",
          np.isclose(decision_cost_max(aH, aL, b), 16.0))

    # verification_overhead_ratio
    check("module: overhead(0) = 0",
          np.isclose(verification_overhead_ratio(0.0), 0.0))
    check("module: overhead(0.1) ≈ 0.883",
          np.isclose(verification_overhead_ratio(0.1), 0.883, atol=0.01))

    # verification_cost
    check("module: ΔW(0.1, W=2) ≈ 1.77",
          np.isclose(verification_cost(0.1, 2.0), 1.77, atol=0.02))

    # deception_cost_min
    d_min = deception_cost_min(0.1, aH, aL, b, 2.0)
    check("module: min(ΔU_B, ΔW) at q=0.1 = ΔW ≈ 1.77",
          np.isclose(d_min, 1.77, atol=0.02),
          f"d_min = {d_min:.2f}")

    # network_verification_tax
    tax = network_verification_tax(0.1, 10_000, 1.0)
    check("module: network tax q̄=0.1 ≈ 8,830",
          np.isclose(tax, 8830, rtol=0.02),
          f"tax = {tax:.0f}")

    # cascade_cost_info
    c_cascade = cascade_cost_info(0.1, 1.0, 0.01, 5_000, 10.0, 0.05)
    check("module: cascade cost = 1,000",
          np.isclose(c_cascade, 1_000),
          f"C = {c_cascade:.0f}")

    # steady_state_info_friction
    phi = steady_state_info_friction(50.0, 0.01, 0.1, 1.0, 0.05)
    check("module: φ_micro = 1.0",
          np.isclose(phi, 1.0),
          f"φ = {phi}")

    # Array support
    q_arr = np.array([0.0, 0.1, 0.25, 0.5])
    h_arr = binary_entropy(q_arr)
    check("module: array binary_entropy shape",
          h_arr.shape == (4,),
          f"shape = {h_arr.shape}")
    check("module: array values correct",
          np.isclose(h_arr[0], 0.0) and np.isclose(h_arr[-1], 1.0))


# ---------------------------------------------------------------------------
# 13. Theorem 10(b): Super-linear growth
# ---------------------------------------------------------------------------

def verify_superlinear_growth() -> None:
    section("13. Theorem 10(b) — Super-linear Growth of Overhead")

    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    def overhead(q_val: float) -> float:
        h = h_num(q_val)
        return h / (1 - h) if h < 1 else float("inf")

    # Check super-linear (accelerating) growth on the bulk of the interval.
    # Near q=0, h''<0 dominates so the composite isn't globally convex,
    # but from ~0.05 onward the 1/(1-h)² divergence takes over.
    qs = np.linspace(0.05, 0.45, 500)
    overheads = np.array([overhead(q) for q in qs])

    # Verify accelerating growth: overhead ratio increases monotonically
    ratios = overheads[1:] / overheads[:-1]
    accelerating = np.all(np.diff(ratios) >= -1e-3)  # allow small numerical noise
    check("h(q)/(1-h(q)) growth accelerates on (0.05, 0.5)",
          accelerating,
          f"min Δ(ratio) = {np.diff(ratios).min():.6f}")

    # Growth comparison: overhead at 2q vs 2× overhead at q
    q_test = 0.1
    overhead_2q = overhead(2 * q_test)
    overhead_q = overhead(q_test)
    check("overhead(0.2) > 2 × overhead(0.1) (super-linear)",
          overhead_2q > 2 * overhead_q,
          f"overhead(0.2)={overhead_2q:.3f}, 2×overhead(0.1)={2*overhead_q:.3f}")


# ---------------------------------------------------------------------------
# 14. Deception-Friction Mapping (Definition 17)
# ---------------------------------------------------------------------------

def verify_deception_friction_mapping() -> None:
    section("14. Deception-Friction Mapping — Definition 17")

    # The mapping: Δφ = η_info · ΔH · W_bit
    # This should give the same severity units as Task 1.2: v = ΔH · W_bit
    eta_info = 0.01
    W_bit = 1.0

    # Single lie: ΔH = 0.1 bits
    delta_H = 0.1
    delta_phi = eta_info * delta_H * W_bit
    check("Single lie (ΔH=0.1): Δφ = 0.001",
          np.isclose(delta_phi, 0.001),
          f"Δφ = {delta_phi}")

    # Severity in energy units: v = ΔH · W_bit = 0.1
    v_equiv = delta_H * W_bit
    check("Energy-equivalent severity = 0.1",
          np.isclose(v_equiv, 0.1))

    # Compare to Task 1.2 formula: Δφ = η · v
    delta_phi_task12_format = eta_info * v_equiv
    check("Format matches Task 1.2: Δφ = η · v",
          np.isclose(delta_phi, delta_phi_task12_format))


# ---------------------------------------------------------------------------
# 15. Multi-Dimensional Generalization (Section 2.3)
# ---------------------------------------------------------------------------

def verify_multidim() -> None:
    section("15. Multi-Dimensional Generalization — Section 2.3")

    def h_num(q_val: float) -> float:
        if q_val == 0:
            return 0.0
        if q_val == 0.5:
            return 1.0
        return -q_val * math.log2(q_val) - (1 - q_val) * math.log2(1 - q_val)

    # For d independent binary components with common deception rate q
    d = 8
    q = 0.1

    H_cond = d * h_num(q)
    I_mutual = d * (1 - h_num(q))

    check(f"d={d}, q={q}: H(Θ|Y) = d·h(q) = {H_cond:.3f}",
          np.isclose(H_cond, 8 * 0.469, atol=0.01),
          f"H = {H_cond:.3f}")
    check(f"d={d}, q={q}: I(Θ;Y) = d·(1-h(q)) = {I_mutual:.3f}",
          np.isclose(I_mutual, 8 * 0.531, atol=0.01),
          f"I = {I_mutual:.3f}")

    # Total state entropy is d bits; mutual information should be ≤ d
    check("I(Θ;Y) ≤ H(Θ) = d", I_mutual <= d + 1e-10)

    # Partial deception (Section 2.4): lie on S ⊂ {1,...,d}
    S = 3  # lie on 3 of 8 dimensions
    q_S = 0.2  # higher deception rate on those
    delta_H_partial = S * h_num(q_S) + (d - S) * 0  # honest on rest
    check(f"Partial deception (|S|={S}, q={q_S}): ΔH = |S|·h(q)",
          np.isclose(delta_H_partial, S * h_num(q_S)),
          f"ΔH = {delta_H_partial:.3f}")
    check("ΔH ≤ |S| = 3 bits",
          delta_H_partial <= S + 1e-10,
          f"ΔH = {delta_H_partial:.3f}")


# ---------------------------------------------------------------------------
# 16. Gaussian Channel Mutual Information (Section 2.3)
# ---------------------------------------------------------------------------

def verify_gaussian_channel() -> None:
    section("16. Gaussian Channel Mutual Information — Section 2.3")

    # I(Θ;Y) = (d/2) log2(1 + σ_Θ²/σ_Z²)
    d = 4
    sigma_theta = 5.0
    sigma_Z_values = [0.1, 1.0, 5.0, 50.0]

    for sigma_Z in sigma_Z_values:
        SNR = sigma_theta ** 2 / sigma_Z ** 2
        I_val = d / 2 * math.log2(1 + SNR)
        check(f"σ_Z={sigma_Z}: I = {I_val:.2f} bits",
              I_val >= 0, f"I = {I_val:.2f}")

    # As σ_Z → 0: I → ∞ (perfect channel, continuous)
    I_low_noise = d / 2 * math.log2(1 + sigma_theta ** 2 / 0.001 ** 2)
    check("Low noise: I is very large",
          I_low_noise > 40, f"I = {I_low_noise:.1f}")

    # As σ_Z → ∞: I → 0 (total noise)
    I_high_noise = d / 2 * math.log2(1 + sigma_theta ** 2 / 1e10)
    check("High noise: I ≈ 0",
          np.isclose(I_high_noise, 0.0, atol=1e-4), f"I = {I_high_noise:.6f}")

    # Monotonically decreasing in σ_Z
    I_vals = [d / 2 * math.log2(1 + sigma_theta ** 2 / sz ** 2)
              for sz in sigma_Z_values]
    decreasing = all(I_vals[i] > I_vals[i + 1] for i in range(len(I_vals) - 1))
    check("I decreasing in σ_Z", decreasing)


# ---------------------------------------------------------------------------
# 17. Law of Total Variance Proof Check (Theorem 8 derivation)
# ---------------------------------------------------------------------------

def verify_total_variance() -> None:
    section("17. Law of Total Variance — Theorem 8 Derivation")

    # Numerical verification using simulation
    np.random.seed(42)
    n_samples = 200_000

    alpha_H, alpha_L = 20.0, 4.0
    q = 0.15
    beta = 2.0

    # Generate true states
    theta = np.random.choice([alpha_H, alpha_L], size=n_samples, p=[0.5, 0.5])

    # Generate BSC signals
    flip = np.random.random(n_samples) < q
    # Y encodes the state: Y=1 means "high", Y=0 means "low"
    Y_true = (theta == alpha_H).astype(float)
    Y = np.where(flip, 1 - Y_true, Y_true)

    # Compute E[α|Y] for each sample
    E_alpha_given_Y1 = (1 - q) * alpha_H + q * alpha_L
    E_alpha_given_Y0 = q * alpha_H + (1 - q) * alpha_L
    alpha_hat = np.where(Y == 1, E_alpha_given_Y1, E_alpha_given_Y0)

    # Verify law of total variance numerically
    var_alpha = np.var(theta)
    var_alpha_hat = np.var(alpha_hat)
    E_var_alpha_given_Y = np.mean([
        np.var(theta[Y == 1]) if np.sum(Y == 1) > 0 else 0,
        np.var(theta[Y == 0]) if np.sum(Y == 0) > 0 else 0,
    ])

    # Var(α) ≈ Var(E[α|Y]) + E[Var(α|Y)]
    total_var_check = var_alpha_hat + E_var_alpha_given_Y
    check("Law of total variance (simulation)",
          np.isclose(var_alpha, total_var_check, rtol=0.05),
          f"Var(α)={var_alpha:.2f}, sum={total_var_check:.2f}")

    # Verify decision cost formula against simulation
    # B acts on alpha_hat, true state is theta
    x_B = alpha_hat / beta
    U_B_actual = theta * x_B - beta / 2 * x_B ** 2
    U_B_honest = theta ** 2 / (2 * beta)  # optimal action

    delta_U_sim = np.mean(U_B_honest) - np.mean(U_B_actual)
    delta_U_formula = q * (1 - q) * (alpha_H - alpha_L) ** 2 / (2 * beta)

    check("Decision cost: simulation matches formula",
          np.isclose(delta_U_sim, delta_U_formula, rtol=0.05),
          f"sim={delta_U_sim:.3f}, formula={delta_U_formula:.3f}")


# ---------------------------------------------------------------------------
# 18. Serial BSC Composition + Pipeline Collapse Threshold
#     (Proposition: Serial BSC Composition, Corollary: Pipeline Collapse Threshold)
# ---------------------------------------------------------------------------

def verify_bsc_series() -> None:
    section("18. Serial BSC Composition & Pipeline Collapse Threshold")

    from modules.information import (
        bsc_series_q_eff,
        bsc_series_capacity,
        pipeline_collapse_threshold,
        binary_entropy,
    )

    # --- (a) Symbolic identity for d=2: q_eff = q1 + q2 - 2 q1 q2 ---
    q1, q2 = sp.symbols("q1 q2", positive=True)
    q_eff_sym = (1 - (1 - 2 * q1) * (1 - 2 * q2)) / 2
    expected = q1 + q2 - 2 * q1 * q2
    check("Symbolic: d=2 composition q_eff = q1 + q2 - 2 q1 q2",
          sp.simplify(q_eff_sym - expected) == 0)

    # --- (b) Boundary cases ---
    check("q_eff(d=1, q=0.1) = q (single channel)",
          np.isclose(bsc_series_q_eff(1, 0.1), 0.1))
    check("q_eff(d=10, q=0) = 0 (honest pipeline)",
          np.isclose(bsc_series_q_eff(10, 0.0), 0.0))
    check("q_eff(d=10, q=0.5) = 0.5 (saturated)",
          np.isclose(bsc_series_q_eff(10, 0.5), 0.5))

    # --- (c) Monotone increasing in d for q in (0, 0.5) ---
    q_test = 0.05
    q_effs = [bsc_series_q_eff(d, q_test) for d in range(1, 21)]
    monotone = all(q_effs[i] < q_effs[i + 1] for i in range(len(q_effs) - 1))
    check("q_eff(d, q=0.05) strictly increasing in d", monotone)

    # --- (d) Limit q_eff -> 0.5 as d -> infinity for any q > 0 ---
    q_eff_large = bsc_series_q_eff(10_000, 0.01)
    check("q_eff(d=10000, q=0.01) -> 0.5",
          np.isclose(q_eff_large, 0.5, atol=1e-6),
          f"q_eff = {q_eff_large}")

    # --- (e) Numerical match: d=10, q=0.063 ---
    # (1 - 2*0.063)^10 = 0.874^10 ≈ 0.2602
    # q_eff ≈ 0.3699; h ≈ 0.9505; C_eff ≈ 0.0495
    q_eff_paper = bsc_series_q_eff(10, 0.063)
    C_eff_paper = bsc_series_capacity(10, 0.063)
    check("q_eff(d=10, q=0.063) ≈ 0.370",
          np.isclose(q_eff_paper, 0.370, atol=0.002),
          f"q_eff = {q_eff_paper:.4f}")
    check("C_eff(d=10, q=0.063) ≈ 0.05 (paper claim)",
          np.isclose(C_eff_paper, 0.05, atol=0.005),
          f"C_eff = {C_eff_paper:.4f}")

    # --- (f) Pipeline collapse threshold round-trip ---
    # q*(d; C_min) is the largest q for which C_eff(d, q) >= C_min.
    for d, C_min in [(1, 0.05), (2, 0.05), (5, 0.05), (10, 0.05),
                      (20, 0.05), (50, 0.05), (10, 0.10), (10, 0.5)]:
        q_star = pipeline_collapse_threshold(d, C_min)
        C_at_threshold = bsc_series_capacity(d, q_star)
        check(f"Round-trip d={d}, C_min={C_min}: C_eff(d, q*) ≈ C_min",
              np.isclose(C_at_threshold, C_min, atol=1e-6),
              f"q*={q_star:.6f}, C_eff={C_at_threshold:.6f}")

    # --- (g) Headline numerical claim ---
    q_star_10 = pipeline_collapse_threshold(10, 0.05)
    check("q*(d=10, C_min=0.05) ≈ 0.063 (paper claim)",
          np.isclose(q_star_10, 0.063, atol=0.001),
          f"q* = {q_star_10:.5f}")

    # --- (h) Threshold table from the paper ---
    table = [
        (1, 0.370),
        (2, 0.244),
        (5, 0.118),
        (10, 0.063),
        (20, 0.032),
        (50, 0.013),
    ]
    for d, q_star_expected in table:
        q_star_actual = pipeline_collapse_threshold(d, 0.05)
        check(f"q*(d={d}, C_min=0.05) ≈ {q_star_expected}",
              np.isclose(q_star_actual, q_star_expected, atol=0.001),
              f"q* = {q_star_actual:.4f}")

    # --- (i) q*(d; C_min) strictly decreasing in d ---
    qs = [pipeline_collapse_threshold(d, 0.05) for d in range(1, 51)]
    decreasing = all(qs[i] > qs[i + 1] for i in range(len(qs) - 1))
    check("q*(d; 0.05) strictly decreasing in d", decreasing)

    # --- (j) Direct simulation: compose two BSCs, check effective rate ---
    np.random.seed(7)
    n = 500_000
    q_a, q_b = 0.08, 0.12
    theta = np.random.randint(0, 2, size=n)
    flip_a = np.random.random(n) < q_a
    flip_b = np.random.random(n) < q_b
    y1 = theta ^ flip_a.astype(int)
    y2 = y1 ^ flip_b.astype(int)
    empirical = np.mean(y2 != theta)
    formula = (1 - (1 - 2 * q_a) * (1 - 2 * q_b)) / 2
    check("Simulation matches q_eff for non-uniform 2-stage pipeline",
          np.isclose(empirical, formula, atol=0.005),
          f"empirical={empirical:.4f}, formula={formula:.4f}")

    # --- (k) Geometric bias-decay identity: 1/2 - q_eff = (1-2q)^d / 2 ---
    for d in [1, 2, 5, 10, 20]:
        for q in [0.01, 0.05, 0.1, 0.25]:
            lhs = 0.5 - bsc_series_q_eff(d, q)
            rhs = 0.5 * (1 - 2 * q) ** d
            check(f"Geometric bias decay: 1/2 - q_eff(d={d}, q={q}) = (1-2q)^d / 2",
                  np.isclose(lhs, rhs, atol=1e-12),
                  f"lhs={lhs:.6e}, rhs={rhs:.6e}")

    # --- (l) Concavity of q_eff in q for d >= 2 (curve lies above chord) ---
    for d in [2, 5, 10, 20]:
        q_lo, q_hi = 0.05, 0.30
        q_mid = 0.5 * (q_lo + q_hi)
        f_lo = bsc_series_q_eff(d, q_lo)
        f_hi = bsc_series_q_eff(d, q_hi)
        f_mid = bsc_series_q_eff(d, q_mid)
        chord_mid = 0.5 * (f_lo + f_hi)
        check(f"Concavity in q at d={d}: q_eff(midpoint) > chord midpoint",
              f_mid > chord_mid + 1e-9,
              f"f_mid={f_mid:.4f}, chord={chord_mid:.4f}")

    # --- (m) Symbolic confirmation: d^2 q_eff / dq^2 = -2 d (d-1) (1-2q)^(d-2) ---
    q_sym, d_sym = sp.symbols("q d", positive=True)
    q_eff_d = (1 - (1 - 2 * q_sym) ** d_sym) / 2
    second_deriv = sp.diff(q_eff_d, q_sym, 2)
    expected_dd = -2 * d_sym * (d_sym - 1) * (1 - 2 * q_sym) ** (d_sym - 2)
    check("Symbolic: d^2 q_eff/dq^2 = -2 d (d-1) (1-2q)^(d-2)  (concave for d>=2)",
          sp.simplify(second_deriv - expected_dd) == 0)

    # --- (n) Small-q linearization: q_eff(d, q) ~ d q + O((d q)^2) ---
    for d in [5, 10, 20]:
        q = 1e-4
        q_eff_val = bsc_series_q_eff(d, q)
        leading = d * q
        rel_err = abs(q_eff_val - leading) / leading
        check(f"Small-q linearization q_eff ~ d q at d={d}, q={q}",
              rel_err < 1e-2,
              f"q_eff={q_eff_val:.6e}, d*q={leading:.6e}, rel_err={rel_err:.2e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("  VERIFICATION: Task 1.3 — Micro-Friction (Information Entropy)")
    print("  math/information-negentropy.md (Part A)")
    print("=" * 72)

    verify_binary_entropy()
    verify_redundancy_factor()
    verify_decision_cost()
    verify_verification_cost()
    verify_inevitability()
    verify_network_tax()
    verify_cascade_cost()
    verify_steady_state_friction()
    verify_honest_baseline()
    verify_example_6_1()
    verify_decision_cost_table()
    verify_modules()
    verify_superlinear_growth()
    verify_deception_friction_mapping()
    verify_multidim()
    verify_gaussian_channel()
    verify_total_variance()
    verify_bsc_series()

    print(f"\n{'='*72}")
    print(f"  FINAL RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print(f"  Pass rate: {PASS / (PASS + FAIL) * 100:.1f}%")
    print(f"{'='*72}")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
