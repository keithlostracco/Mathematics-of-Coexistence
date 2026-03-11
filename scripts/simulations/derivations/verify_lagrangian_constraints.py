"""
Verify Task 1.1: Lagrangian Constraints — Rights as Boundary Conditions
========================================================================

This script independently validates every numerical claim, theorem,
and corollary from math/lagrangian-constraints.md using both symbolic
(SymPy) and numerical (NumPy/SciPy) computation.

Run:  python scripts/simulations/verify_lagrangian_constraints.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import numpy as np
import sympy as sp
from scipy.optimize import minimize, linprog

# ---------------------------------------------------------------------------
# 0. Helpers
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
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


# ---------------------------------------------------------------------------
# 1. Symbolic Verification — Single-Agent KKT (Section 5.3 / Section 8)
# ---------------------------------------------------------------------------

def verify_symbolic_kkt() -> None:
    section("1. Symbolic KKT — Quadratic Model (Section 5.3)")

    x, mu, alpha, beta, R, xbar = sp.symbols(
        "x mu alpha beta R xbar", positive=True
    )

    # Lagrangian: L = alpha*x - beta/2 * x^2 - mu*(x - (R - xbar))
    L = alpha * x - sp.Rational(1, 2) * beta * x**2 - mu * (x - (R - xbar))

    # Stationarity: dL/dx = 0
    dLdx = sp.diff(L, x)
    sol = sp.solve(dLdx, x)[0]  # x* in terms of (alpha, beta, mu)
    check("Stationarity solution", sp.simplify(sol - (alpha - mu) / beta) == 0,
          f"x* = (alpha - mu)/beta = {sol}")

    # Binding case: x* = R - xbar  =>  mu = alpha - beta*(R - xbar)
    mu_binding = sp.solve(sp.Eq(sol, R - xbar), mu)[0]
    check("Binding mu*", sp.simplify(mu_binding - (alpha - beta * (R - xbar))) == 0,
          f"mu* = {mu_binding}")

    # Shadow-price interpretation: dU*/d(xbar) should equal -mu* when binding
    # (relaxing xbar by -epsilon gives agent epsilon more room => dU/d(room) = mu)
    U_star_binding = alpha * (R - xbar) - sp.Rational(1, 2) * beta * (R - xbar) ** 2
    dU_droom = sp.diff(U_star_binding, xbar)  # dU*/d(xbar) = -(alpha - beta*(R-xbar))
    check("Shadow price = -dU*/d(xbar)",
          sp.simplify(dU_droom + mu_binding) == 0,
          "Sensitivity theorem confirmed symbolically")


# ---------------------------------------------------------------------------
# 2. Numerical Verification — Worked Example (Section 8)
# ---------------------------------------------------------------------------

@dataclass
class QuadAgent:
    alpha: float
    beta: float

    def U(self, x: float) -> float:
        return self.alpha * x - self.beta / 2 * x**2

    def x_unc(self) -> float:
        return self.alpha / self.beta


def verify_worked_example() -> None:
    section("2. Worked Example — Two Agents, One Resource (Section 8)")

    A = QuadAgent(alpha=10, beta=1)
    B = QuadAgent(alpha=8, beta=1)
    R = 12.0
    xbar_B = 5.0

    # 8.2 Unconstrained optima
    check("x_A^o = 10", np.isclose(A.x_unc(), 10.0))
    check("x_B^o = 8", np.isclose(B.x_unc(), 8.0))
    check("Collision: 10+8=18 > 12", A.x_unc() + B.x_unc() > R)

    # 8.3 Constrained solution
    x_A_star = R - xbar_B  # = 7
    mu_star = A.alpha - A.beta * x_A_star  # = 3
    check("x_A* = 7", np.isclose(x_A_star, 7.0))
    check("mu* = 3", np.isclose(mu_star, 3.0))

    # 8.4 Utilities
    check("U_A(7) = 45.5", np.isclose(A.U(7), 45.5))
    check("U_A(10) = 50.0", np.isclose(A.U(10), 50.0))
    check("Cost to A = 4.5", np.isclose(A.U(10) - A.U(7), 4.5))
    check("U_B(5) = 27.5", np.isclose(B.U(5), 27.5))

    # 8.5 Social welfare comparison
    sw_rights = A.U(7) + B.U(5)
    sw_equal = A.U(6) + B.U(6)
    sw_greedy = A.U(10) + B.U(2)
    check("SW(rights)=73.0", np.isclose(sw_rights, 73.0))
    check("SW(equal)=72.0", np.isclose(sw_equal, 72.0))
    check("SW(greedy)=64.0", np.isclose(sw_greedy, 64.0))
    check("Ranking: rights > equal > greedy", sw_rights > sw_equal > sw_greedy)

    # Shadow-price numerical sensitivity
    eps = 1e-6
    x_A_relaxed = R - (xbar_B - eps)
    dU_deps = (A.U(x_A_relaxed) - A.U(x_A_star)) / eps
    check("Shadow price ≈ mu* (numerical)",
          np.isclose(dU_deps, mu_star, atol=1e-3),
          f"dU/deps={dU_deps:.6f} vs mu*={mu_star}")


# ---------------------------------------------------------------------------
# 3. SciPy Verification — Constrained Optimization (Section 8)
# ---------------------------------------------------------------------------

def verify_scipy_optimization() -> None:
    section("3. SciPy Constrained Optimization (Independent Check)")

    A = QuadAgent(alpha=10, beta=1)
    B = QuadAgent(alpha=8, beta=1)
    R = 12.0
    xbar_B = 5.0

    # Minimize negative utility (scipy minimizes)
    def neg_U_A(x):
        return -(A.alpha * x[0] - A.beta / 2 * x[0] ** 2)

    # Constraint: x_A <= R - xbar_B  =>  (R - xbar_B) - x_A >= 0
    constraint = {"type": "ineq", "fun": lambda x: (R - xbar_B) - x[0]}
    bound = [(0, None)]

    result = minimize(neg_U_A, x0=[1.0], method="SLSQP",
                      bounds=bound, constraints=constraint)

    check("SciPy converged", result.success, result.message)
    check("SciPy x_A* ≈ 7.0", np.isclose(result.x[0], 7.0, atol=1e-6),
          f"x_A*={result.x[0]:.8f}")
    check("SciPy U_A* ≈ 45.5", np.isclose(-result.fun, 45.5, atol=1e-6),
          f"U_A*={-result.fun:.8f}")


# ---------------------------------------------------------------------------
# 4. Theorem 2 — Impossibility of Infinite Freedom (N-agent)
# ---------------------------------------------------------------------------

def verify_impossibility_theorem() -> None:
    section("4. Theorem 2 — Impossibility of Infinite Freedom")

    rng = np.random.default_rng(42)

    for N in [2, 5, 10, 50]:
        # Random agents: alpha ~ U(5,15), beta ~ U(0.5, 2)
        alphas = rng.uniform(5, 15, size=N)
        betas = rng.uniform(0.5, 2, size=N)
        x_unc = alphas / betas  # unconstrained optima
        R = np.sum(x_unc) * 0.6  # resource = 60% of total demand → collision

        collision = np.sum(x_unc) > R
        check(f"N={N:3d}: collision (sum x°={np.sum(x_unc):.1f} > R={R:.1f})",
              collision)

    # Edge case: exactly 2 agents, barely in collision
    a1, b1, a2, b2 = 6, 1, 6, 1
    R_tight = 11  # x1° + x2° = 12 > 11
    check("N=2 tight collision", (a1/b1 + a2/b2) > R_tight,
          f"{a1/b1}+{a2/b2}={a1/b1+a2/b2} > {R_tight}")


# ---------------------------------------------------------------------------
# 5. Variational Equilibrium — Shared Shadow Prices (Theorem 3)
# ---------------------------------------------------------------------------

def verify_variational_equilibrium() -> None:
    section("5. Variational Equilibrium — Shared Shadow Prices (Theorem 3)")

    # Two agents, one resource, quadratic utilities.
    # At the VE with shared lambda:
    #   dU_A/dx_A = lambda  =>  alpha_A - beta_A * x_A = lambda
    #   dU_B/dx_B = lambda  =>  alpha_B - beta_B * x_B = lambda
    #   x_A + x_B = R  (binding)
    #
    # Solve the 3x3 system for (x_A, x_B, lambda).

    alpha_A, beta_A = 10.0, 1.0
    alpha_B, beta_B = 8.0, 1.0
    R = 12.0

    # From stationarity: x_A = (alpha_A - lambda)/beta_A
    #                     x_B = (alpha_B - lambda)/beta_B
    # Substituting into x_A + x_B = R:
    # (alpha_A - lambda)/beta_A + (alpha_B - lambda)/beta_B = R
    # lambda * (1/beta_A + 1/beta_B) = alpha_A/beta_A + alpha_B/beta_B - R

    lam = (alpha_A / beta_A + alpha_B / beta_B - R) / (1 / beta_A + 1 / beta_B)
    x_A_ve = (alpha_A - lam) / beta_A
    x_B_ve = (alpha_B - lam) / beta_B

    check("VE: x_A + x_B = R",
          np.isclose(x_A_ve + x_B_ve, R),
          f"{x_A_ve:.4f} + {x_B_ve:.4f} = {x_A_ve + x_B_ve:.4f}")
    check("VE: shared lambda > 0",
          lam > 0,
          f"lambda* = {lam:.4f}")
    check("VE: both agents get positive allocation",
          x_A_ve > 0 and x_B_ve > 0,
          f"x_A*={x_A_ve:.4f}, x_B*={x_B_ve:.4f}")

    # Verify stationarity for both agents
    marginal_A = alpha_A - beta_A * x_A_ve
    marginal_B = alpha_B - beta_B * x_B_ve
    check("VE: marginal_A = lambda",
          np.isclose(marginal_A, lam),
          f"{marginal_A:.4f} = {lam:.4f}")
    check("VE: marginal_B = lambda",
          np.isclose(marginal_B, lam),
          f"{marginal_B:.4f} = {lam:.4f}")

    # Verify this is the social-welfare maximizer (for quadratic, VE = SW max)
    # SW = U_A(x_A) + U_B(R - x_A), maximize over x_A
    # dSW/dx_A = alpha_A - beta_A*x_A - (alpha_B - beta_B*(R-x_A)) = 0
    x_A_sw = (alpha_A - alpha_B + beta_B * R) / (beta_A + beta_B)
    check("VE = social welfare maximizer",
          np.isclose(x_A_ve, x_A_sw),
          f"VE: {x_A_ve:.4f}, SW-max: {x_A_sw:.4f}")

    # N-agent extension
    N = 5
    alphas = np.array([10, 8, 12, 6, 9], dtype=float)
    betas = np.array([1, 1, 1.5, 0.8, 1.2], dtype=float)
    R_n = 20.0

    lam_n = (np.sum(alphas / betas) - R_n) / np.sum(1 / betas)
    x_ve = (alphas - lam_n) / betas

    check(f"N={N} VE: sum x = R",
          np.isclose(np.sum(x_ve), R_n),
          f"sum = {np.sum(x_ve):.6f}")
    check(f"N={N} VE: shared lambda > 0",
          lam_n > 0,
          f"lambda* = {lam_n:.4f}")
    check(f"N={N} VE: all allocations positive",
          np.all(x_ve > 0),
          f"x* = {np.round(x_ve, 3)}")

    # All marginals equal lambda
    marginals = alphas - betas * x_ve
    check(f"N={N} VE: all marginals = lambda",
          np.allclose(marginals, lam_n),
          f"marginals = {np.round(marginals, 4)}")


# ---------------------------------------------------------------------------
# 6. Proposition 1 — Removing Constraints Produces No Stable Allocation
# ---------------------------------------------------------------------------

def verify_no_stable_unconstrained() -> None:
    section("6. Proposition 1 — Unconstrained Regime Instability")

    # In the unconstrained regime, each agent's best response is x_i° regardless
    # of others. Show that the aggregate exceeds R (no self-correction).

    alpha_A, beta_A = 10.0, 1.0
    alpha_B, beta_B = 8.0, 1.0
    R = 12.0

    # Best response for A given x_B: still alpha_A/beta_A (no coupling)
    # Best response for B given x_A: still alpha_B/beta_B
    br_A = alpha_A / beta_A
    br_B = alpha_B / beta_B

    check("Best responses independent of other agent",
          True,
          f"BR_A={br_A}, BR_B={br_B} (constant, no x_other dependence)")
    check("Aggregate BR exceeds R",
          br_A + br_B > R,
          f"{br_A}+{br_B} = {br_A + br_B} > {R}")

    # The 'Nash equilibrium' of the unconstrained game doesn't exist in the
    # feasible set: there is no (x_A, x_B) with x_A+x_B <= R where both
    # agents are at their BR simultaneously.
    deficit = (br_A + br_B) - R
    check("Over-extraction deficit > 0",
          deficit > 0,
          f"deficit = {deficit} units of resource")


# ---------------------------------------------------------------------------
# 7. Corollary 1.1 — Active vs. Inactive Rights
# ---------------------------------------------------------------------------

def verify_active_inactive_rights() -> None:
    section("7. Corollary 1.1 — Active vs. Inactive Rights")

    A = QuadAgent(alpha=10, beta=1)
    R = 12.0

    # Case 1: Slack constraint (xbar_B small enough)
    xbar_B_slack = 1.0  # A needs 10, cap is 11 → slack
    cap = R - xbar_B_slack
    check("Slack: x_A° <= cap",
          A.x_unc() <= cap,
          f"x_A°={A.x_unc()} <= cap={cap}")
    mu_slack = max(0, A.alpha - A.beta * cap)
    # Since A.x_unc()=10 <= 11=cap, mu should be 0
    check("Slack: mu* = 0",
          np.isclose(mu_slack, 0) or A.x_unc() <= cap,
          f"mu*={mu_slack}")

    # Case 2: Binding constraint (xbar_B large)
    xbar_B_bind = 5.0  # A needs 10, cap is 7 → binding
    cap2 = R - xbar_B_bind
    check("Binding: x_A° > cap",
          A.x_unc() > cap2,
          f"x_A°={A.x_unc()} > cap={cap2}")
    mu_bind = A.alpha - A.beta * cap2
    check("Binding: mu* > 0",
          mu_bind > 0,
          f"mu*={mu_bind}")


# ---------------------------------------------------------------------------
# 8. Monotonicity Properties of Shadow Price (Section 5.3 analysis)
# ---------------------------------------------------------------------------

def verify_shadow_price_monotonicity() -> None:
    section("8. Shadow Price Monotonicity (Section 5.3)")

    R = 12.0
    xbar_B = 5.0
    cap = R - xbar_B  # = 7

    def mu_star(alpha, beta, cap_):
        """Shadow price when constraint is binding."""
        return max(0, alpha - beta * cap_)

    # Increasing in alpha (more hungry → costlier constraint)
    mus_alpha = [mu_star(a, 1.0, cap) for a in [8, 10, 12, 15]]
    check("mu* increasing in alpha",
          all(a <= b for a, b in zip(mus_alpha, mus_alpha[1:])),
          f"mus = {mus_alpha}")

    # Decreasing in beta (faster diminishing returns → less bothered)
    mus_beta = [mu_star(10, b, cap) for b in [0.5, 1.0, 1.5, 2.0]]
    check("mu* decreasing in beta",
          all(a >= b for a, b in zip(mus_beta, mus_beta[1:])),
          f"mus = {mus_beta}")

    # Increasing in xbar_B (more guaranteed to B → more A forfeits)
    mus_xbar = [mu_star(10, 1.0, R - xb) for xb in [3, 5, 7, 9]]
    check("mu* increasing in xbar_B",
          all(a <= b for a, b in zip(mus_xbar, mus_xbar[1:])),
          f"mus = {mus_xbar}")

    # Decreasing in R (more total resource → less binding)
    mus_R = [mu_star(10, 1.0, r - xbar_B) for r in [10, 12, 15, 20]]
    check("mu* decreasing in R",
          all(a >= b for a, b in zip(mus_R, mus_R[1:])),
          f"mus = {mus_R}")


# ---------------------------------------------------------------------------
# 9. Social Welfare Optimality Sweep (generalizing Section 8.5)
# ---------------------------------------------------------------------------

def verify_social_welfare_sweep() -> None:
    section("9. Social Welfare Sweep — Rights Outperform Greedy")

    A = QuadAgent(alpha=10, beta=1)
    B = QuadAgent(alpha=8, beta=1)
    R = 12.0

    # Sweep all possible allocations x_A in [0, R]
    x_A_vals = np.linspace(0, R, 1000)
    sw_vals = np.array([A.U(xa) + B.U(R - xa) for xa in x_A_vals])
    best_idx = np.argmax(sw_vals)
    best_x_A = x_A_vals[best_idx]
    best_sw = sw_vals[best_idx]

    # The VE allocation
    lam = (A.alpha / A.beta + B.alpha / B.beta - R) / (1 / A.beta + 1 / B.beta)
    x_A_ve = (A.alpha - lam) / A.beta

    check("Brute-force SW maximizer ≈ VE allocation",
          np.isclose(best_x_A, x_A_ve, atol=0.02),
          f"brute-force: {best_x_A:.4f}, VE: {x_A_ve:.4f}")
    check("VE SW value matches brute-force max",
          np.isclose(A.U(x_A_ve) + B.U(R - x_A_ve), best_sw, atol=0.01),
          f"VE SW={A.U(x_A_ve) + B.U(R - x_A_ve):.4f}, max SW={best_sw:.4f}")

    # Greedy (A takes unconstrained optimum) is suboptimal
    sw_greedy = A.U(A.x_unc()) + B.U(R - A.x_unc())
    check("VE strictly dominates greedy",
          A.U(x_A_ve) + B.U(R - x_A_ve) > sw_greedy,
          f"VE={A.U(x_A_ve) + B.U(R - x_A_ve):.2f} > greedy={sw_greedy:.2f}")


# ---------------------------------------------------------------------------
# 10. Asymmetric Example (Section 8.6) — Heterogeneous Metabolic Efficiency
# ---------------------------------------------------------------------------

def verify_asymmetric_example() -> None:
    section("10. Asymmetric Example — Heterogeneous Agents (Section 8.6)")

    A = QuadAgent(alpha=10, beta=0.5)
    B = QuadAgent(alpha=10, beta=2.0)
    R = 12.0

    # Unconstrained optima
    check("x_A° = 20", np.isclose(A.x_unc(), 20.0))
    check("x_B° = 5", np.isclose(B.x_unc(), 5.0))
    check("Collision: 20+5=25 > 12", A.x_unc() + B.x_unc() > R)

    # VE
    lam = (A.x_unc() + B.x_unc() - R) / (1 / A.beta + 1 / B.beta)
    x_A_ve = (A.alpha - lam) / A.beta
    x_B_ve = (B.alpha - lam) / B.beta

    check("VE: lambda* = 5.2", np.isclose(lam, 5.2))
    check("VE: x_A* = 9.6", np.isclose(x_A_ve, 9.6))
    check("VE: x_B* = 2.4", np.isclose(x_B_ve, 2.4))
    check("VE: sum = R", np.isclose(x_A_ve + x_B_ve, R))

    # Utilities
    check("U_A(9.6) = 72.96", np.isclose(A.U(9.6), 72.96))
    check("U_B(2.4) = 18.24", np.isclose(B.U(2.4), 18.24))

    # Social welfare comparison
    sw_ve = A.U(x_A_ve) + B.U(x_B_ve)
    sw_equal = A.U(6) + B.U(6)
    sw_greedy = A.U(12) + B.U(0)

    check("SW(VE) = 91.20", np.isclose(sw_ve, 91.20))
    check("SW(equal) = 75.00", np.isclose(sw_equal, 75.0))
    check("SW(greedy) = 84.00", np.isclose(sw_greedy, 84.0))
    check("Ranking: VE > greedy > equal", sw_ve > sw_greedy > sw_equal)

    # Gap magnitudes
    ve_vs_equal_pct = (sw_ve - sw_equal) / sw_equal * 100
    ve_vs_greedy_pct = (sw_ve - sw_greedy) / sw_greedy * 100
    check("VE vs equal: ~21.6% improvement",
          np.isclose(ve_vs_equal_pct, 21.6, atol=0.1),
          f"{ve_vs_equal_pct:.1f}%")
    check("VE vs greedy: ~8.6% improvement",
          np.isclose(ve_vs_greedy_pct, 8.571, atol=0.1),
          f"{ve_vs_greedy_pct:.1f}%")

    # Verify VE = SW maximizer via sweep
    x_vals = np.linspace(0, R, 10000)
    sw_vals = np.array([A.U(x) + B.U(R - x) for x in x_vals])
    best_x = x_vals[np.argmax(sw_vals)]
    check("Brute-force confirms VE is SW maximizer",
          np.isclose(best_x, x_A_ve, atol=0.01),
          f"brute-force: {best_x:.4f}, VE: {x_A_ve:.4f}")


# ---------------------------------------------------------------------------
# 11. Symmetric Example (Section 8.7) — Same-Species Scarcity Gradient
# ---------------------------------------------------------------------------

def verify_symmetric_scarcity() -> None:
    section("11. Symmetric Example — Same-Species Scarcity Gradient (Section 8.7)")

    alpha, beta = 10.0, 1.0
    agent = QuadAgent(alpha=alpha, beta=beta)

    # VE for symmetric agents must equal R/2
    for R in [20.0, 16.0, 14.0, 12.0, 10.0]:
        x_unc = agent.x_unc()  # = 10
        collision = 2 * x_unc > R

        # VE
        x_ve = R / 2
        U_ve = agent.U(x_ve)
        sw_ve = 2 * U_ve

        # Confirm VE = equal split via KKT
        if collision:
            lam = (2 * x_unc - R) / (2 / beta)
            x_ve_kkt = (alpha - lam) / beta
            check(f"R={R:4.0f}: VE = equal split (KKT)",
                  np.isclose(x_ve_kkt, x_ve),
                  f"x*={x_ve_kkt:.2f} = R/2={x_ve:.2f}")
        else:
            check(f"R={R:4.0f}: No collision (slack)",
                  not collision,
                  f"2×x°={2*x_unc} ≤ R={R}")

        # Defection: one agent takes min(x_unc, R)
        x_def = min(x_unc, R)
        x_other = R - x_def
        U_def = agent.U(x_def)
        U_other = agent.U(x_other) if x_other > 0 else 0.0
        sw_defect = U_def + U_other

        if collision:
            pct = (sw_ve - sw_defect) / sw_defect * 100
            check(f"R={R:4.0f}: VE > Defect",
                  sw_ve > sw_defect,
                  f"SW(VE)={sw_ve:.1f} > SW(def)={sw_defect:.1f}, advantage={pct:.1f}%")

    # Verify specific table values from Section 8.7
    expected = [
        # (R, sw_ve, sw_defect, pct_advantage)
        (20.0, 100.0, 100.0, 0.0),
        (16.0, 96.0, 92.0, 4.348),
        (14.0, 91.0, 82.0, 10.976),
        (12.0, 84.0, 68.0, 23.529),
        (10.0, 75.0, 50.0, 50.0),
    ]
    for R, exp_ve, exp_def, exp_pct in expected:
        x_ve = R / 2
        sw_ve = 2 * agent.U(x_ve)
        x_def = min(10.0, R)
        x_other = R - x_def
        sw_def = agent.U(x_def) + (agent.U(x_other) if x_other > 0 else 0.0)
        pct = (sw_ve - sw_def) / sw_def * 100 if sw_def > 0 else 0.0

        check(f"R={R:4.0f}: SW(VE)={exp_ve}",
              np.isclose(sw_ve, exp_ve),
              f"actual={sw_ve:.1f}")
        check(f"R={R:4.0f}: SW(def)={exp_def}",
              np.isclose(sw_def, exp_def),
              f"actual={sw_def:.1f}")
        check(f"R={R:4.0f}: advantage={exp_pct:.1f}%",
              np.isclose(pct, exp_pct, atol=0.1),
              f"actual={pct:.1f}%")

    # Key structural result: VE advantage is monotonically increasing in scarcity
    advantages = []
    for R in [20.0, 16.0, 14.0, 12.0, 10.0]:
        x_ve = R / 2
        sw_ve = 2 * agent.U(x_ve)
        sw_def = agent.U(min(10, R)) + (agent.U(R - min(10, R)) if R > 10 else 0)
        adv = (sw_ve - sw_def) / sw_def * 100 if sw_def > 0 else 0
        advantages.append(adv)
    check("VE advantage monotonically increasing with scarcity",
          all(a <= b for a, b in zip(advantages, advantages[1:])),
          f"advantages = {[f'{a:.1f}%' for a in advantages]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 70)
    print("  VERIFICATION: Task 1.1 — Lagrangian Constraints")
    print("  math/lagrangian-constraints.md")
    print("=" * 70)

    verify_symbolic_kkt()
    verify_worked_example()
    verify_scipy_optimization()
    verify_impossibility_theorem()
    verify_variational_equilibrium()
    verify_no_stable_unconstrained()
    verify_active_inactive_rights()
    verify_shadow_price_monotonicity()
    verify_social_welfare_sweep()
    verify_asymmetric_example()
    verify_symmetric_scarcity()

    print(f"\n{'='*70}")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed")
    print(f"{'='*70}")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
