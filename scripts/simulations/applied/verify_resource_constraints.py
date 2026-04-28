"""
Verify: Resource Acquisition Bounded by Rights Constraints
==========================================================

Theorems 1-3, Proposition 1.

Validates all numerical claims in case-studies/resource-constraints.md
using both symbolic (SymPy) and numerical (SciPy) computation.

Run:  python scripts/simulations/applied/verify_resource_constraints.py
"""

from __future__ import annotations

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import sympy as sp
from scipy.optimize import minimize

from modules.verify import reset, section, check, close, summary


# ---------------------------------------------------------------------------
# Scenario Parameters (from README §3.1)
# ---------------------------------------------------------------------------
R_total = 500.0      # Grid capacity (MW)
x_bar_B = 350.0      # Human critical-load floor (MW)
alpha   = 10.0        # Agent A marginal productivity (linear coefficient)
beta    = 0.012       # Diminishing returns (quadratic coefficient)

TOL = 1e-6            # Numerical tolerance


# ---------------------------------------------------------------------------
# 1. Symbolic KKT Verification (Theorem 1 — Shadow Price)
# ---------------------------------------------------------------------------

def verify_symbolic_kkt() -> None:
    section("1. Symbolic KKT — Shadow Price Theorem (Theorem 1)")

    x, mu, a, b, R, xbar = sp.symbols(
        "x mu a b R xbar", positive=True
    )

    # Utility: U_A(x) = a*x - b/2 * x^2
    U = a * x - sp.Rational(1, 2) * b * x**2

    # Lagrangian with rights constraint: g_B(x) = x - (R - xbar) <= 0
    L = U - mu * (x - (R - xbar))

    # Stationarity: dL/dx = 0  =>  x* = (a - mu) / b
    dLdx = sp.diff(L, x)
    x_star = sp.solve(dLdx, x)[0]
    check(
        "Stationarity yields x* = (α - μ)/β",
        sp.simplify(x_star - (a - mu) / b) == 0,
        f"x* = {x_star}"
    )

    # Binding case: x* = R - xbar  =>  mu* = a - b*(R - xbar)
    mu_star = sp.solve(sp.Eq(x_star, R - xbar), mu)[0]
    check(
        "Binding μ* = α - β(R - x̄_B)",
        sp.simplify(mu_star - (a - b * (R - xbar))) == 0,
        f"μ* = {mu_star}"
    )

    # Shadow price interpretation: dU*/d(relaxation) = μ*
    # U* at binding = a*(R-xbar) - b/2*(R-xbar)^2
    U_star_binding = a * (R - xbar) - sp.Rational(1, 2) * b * (R - xbar)**2
    # Relaxing constraint by ε means allowing x up to (R - xbar + ε)
    # dU*/d(room) where room = R - xbar
    room = sp.Symbol("room", positive=True)
    U_star_room = a * room - sp.Rational(1, 2) * b * room**2
    dU_droom = sp.diff(U_star_room, room)
    # At room = R - xbar, dU/droom should equal μ*
    mu_at_boundary = dU_droom.subs(room, R - xbar)
    check(
        "Shadow price = dU*/d(room) at boundary",
        sp.simplify(mu_at_boundary - mu_star) == 0,
        "Sensitivity theorem confirmed symbolically"
    )

    # Verify numerical values from the worked example
    mu_num = float(mu_star.subs({a: alpha, b: beta, R: R_total, xbar: x_bar_B}))
    check(
        "Numerical μ* = 8.20",
        abs(mu_num - 8.20) < TOL,
        f"μ* = {mu_num:.4f}"
    )


# ---------------------------------------------------------------------------
# 2. Numerical Optimization (SciPy verification)
# ---------------------------------------------------------------------------

def verify_numerical_optimization() -> None:
    section("2. Numerical Optimization — Constrained Optimum")

    # Utility function (negative for minimization)
    def neg_utility(x_arr):
        x = x_arr[0]
        return -(alpha * x - (beta / 2) * x**2)

    # Gradient
    def neg_utility_grad(x_arr):
        x = x_arr[0]
        return np.array([-(alpha - beta * x)])

    # Rights constraint: x <= R - x_bar_B  =>  (R - x_bar_B) - x >= 0
    rights_constraint = {
        "type": "ineq",
        "fun": lambda x_arr: (R_total - x_bar_B) - x_arr[0],
        "jac": lambda x_arr: np.array([-1.0]),
    }

    # Non-negativity handled by bounds
    result = minimize(
        neg_utility,
        x0=[250.0],
        jac=neg_utility_grad,
        method="SLSQP",
        bounds=[(0, R_total)],
        constraints=[rights_constraint],
    )

    x_opt = result.x[0]
    u_opt = -result.fun
    expected_x = R_total - x_bar_B  # 150 MW
    expected_u = alpha * expected_x - (beta / 2) * expected_x**2  # 1365.0

    check(
        "Constrained optimum x_A* = 150.0 MW",
        abs(x_opt - expected_x) < 0.1,
        f"x_A* = {x_opt:.2f} MW"
    )
    check(
        "Optimal utility U_A* = 1365.0",
        abs(u_opt - expected_u) < 0.1,
        f"U_A* = {u_opt:.2f}"
    )

    # Check unconstrained optimum exceeds grid
    x_unconstr = alpha / beta
    check(
        "Unconstrained x_A° = 833.3 MW > R",
        x_unconstr > R_total,
        f"x_A° = {x_unconstr:.1f} MW"
    )

    # Utility at grid capacity (no human floor)
    u_grid = alpha * R_total - (beta / 2) * R_total**2
    check(
        "Grid-capacity utility U_A(500) = 3500.0",
        abs(u_grid - 3500.0) < TOL,
        f"U_A(500) = {u_grid:.1f}"
    )


# ---------------------------------------------------------------------------
# 3. Theorem 2 (Impossibility of Infinite Freedom) — Collision Condition
# ---------------------------------------------------------------------------

def verify_impossibility() -> None:
    section("3. Theorem 2 — Impossibility of Infinite Freedom")

    x_unconstr = alpha / beta  # Agent A unconstrained optimum
    combined = x_unconstr + x_bar_B  # Total unconstrained demand

    check(
        "Collision: x_A° + x̄_B > R",
        combined > R_total,
        f"{x_unconstr:.1f} + {x_bar_B:.1f} = {combined:.1f} > {R_total}"
    )

    collision_factor = combined / R_total
    check(
        "Collision factor ≈ 2.37×",
        abs(collision_factor - 2.3667) < 0.01,
        f"factor = {collision_factor:.4f}"
    )

    # Verify for multiple human floor levels
    floors = np.linspace(0.1 * R_total, 0.9 * R_total, 9)
    all_collide = all(x_unconstr + f > R_total for f in floors)
    check(
        "Collision holds for all x̄_B ∈ [0.1R, 0.9R]",
        all_collide,
        "Theorem 2 satisfied universally"
    )


# ---------------------------------------------------------------------------
# 4. Parametric Sweep — Pareto Frontier
# ---------------------------------------------------------------------------

def verify_pareto_frontier() -> None:
    section("4. Parametric Sweep — Pareto Frontier")

    n_points = 50
    x_bar_range = np.linspace(0.1 * R_total, 0.9 * R_total, n_points)

    all_match = True
    max_error_x = 0.0
    max_error_u = 0.0
    max_error_mu = 0.0

    for xb in x_bar_range:
        # Analytical predictions
        x_pred = R_total - xb
        u_pred = alpha * x_pred - (beta / 2) * x_pred**2
        mu_pred = alpha - beta * x_pred

        # Numerical optimization
        def neg_u(x_arr):
            x = x_arr[0]
            return -(alpha * x - (beta / 2) * x**2)

        constraint = {
            "type": "ineq",
            "fun": lambda x_arr, xb_=xb: (R_total - xb_) - x_arr[0],
        }

        result = minimize(
            neg_u,
            x0=[R_total / 2],
            method="SLSQP",
            bounds=[(0, R_total)],
            constraints=[constraint],
        )

        x_num = result.x[0]
        u_num = -result.fun

        err_x = abs(x_num - x_pred)
        err_u = abs(u_num - u_pred)

        max_error_x = max(max_error_x, err_x)
        max_error_u = max(max_error_u, err_u)

        if err_x > 1.0 or err_u > 1.0:
            all_match = False

    check(
        "Pareto frontier: analytical ≈ numerical (all 50 points)",
        all_match,
        f"max |Δx| = {max_error_x:.4f}, max |ΔU| = {max_error_u:.4f}"
    )

    # Verify shadow price is monotonically increasing with x_bar_B
    mu_values = [alpha - beta * (R_total - xb) for xb in x_bar_range]
    is_monotone = all(mu_values[i] <= mu_values[i + 1] for i in range(len(mu_values) - 1))
    check(
        "Shadow price μ* is monotonically increasing in x̄_B",
        is_monotone,
        f"μ* range: [{mu_values[0]:.2f}, {mu_values[-1]:.2f}]"
    )

    # Verify all shadow prices are non-negative (dual feasibility)
    all_nonneg = all(m >= -TOL for m in mu_values)
    check(
        "All shadow prices μ* ≥ 0 (dual feasibility)",
        all_nonneg,
        "Dual feasibility confirmed"
    )


# ---------------------------------------------------------------------------
# 5. Proposition 1 — Unconstrained Regime → Conflict
# ---------------------------------------------------------------------------

def verify_unconstrained_conflict() -> None:
    section("5. Proposition 1 — Unconstrained → Conflict")

    # Without rights constraint, Agent A allocates up to grid capacity
    def neg_u(x_arr):
        x = x_arr[0]
        return -(alpha * x - (beta / 2) * x**2)

    result = minimize(
        neg_u,
        x0=[250.0],
        method="SLSQP",
        bounds=[(0, R_total)],
        # No rights constraint, only grid capacity bound
    )

    x_unconstrained = result.x[0]
    human_remaining = R_total - x_unconstrained

    check(
        "Without rights constraint, Agent A takes full grid capacity",
        abs(x_unconstrained - R_total) < 1.0,
        f"x_A = {x_unconstrained:.1f} MW"
    )
    check(
        "Human allocation drops to zero",
        human_remaining < 1.0,
        f"Human remaining: {human_remaining:.2f} MW"
    )
    check(
        "Human allocation < survival floor",
        human_remaining < x_bar_B,
        f"{human_remaining:.1f} < {x_bar_B:.1f} MW — conflict triggered"
    )


# ---------------------------------------------------------------------------
# 6. Corollary 2.1 — At Least One Active Constraint
# ---------------------------------------------------------------------------

def verify_active_constraint() -> None:
    section("6. Corollary 2.1 — Necessity of Active Constraints")

    # For multiple human stakeholders, verify at least one constraint is active
    # Split human floor across N stakeholders
    N_humans = 5
    floors = [x_bar_B / N_humans] * N_humans  # Equal split: 70 MW each

    def neg_u(x_arr):
        x = x_arr[0]
        return -(alpha * x - (beta / 2) * x**2)

    # Each stakeholder has constraint: x_A <= R - sum(floors) = R - x_bar_B
    # but we model individual constraints: x_A <= R - floor_k - sum_others_demand
    # For simplicity, the aggregate constraint is x_A <= R - x_bar_B = 150
    constraints = [
        {
            "type": "ineq",
            "fun": lambda x_arr: (R_total - x_bar_B) - x_arr[0],
        }
    ]

    result = minimize(
        neg_u,
        x0=[100.0],
        method="SLSQP",
        bounds=[(0, R_total)],
        constraints=constraints,
    )

    x_opt = result.x[0]
    constraint_value = x_opt - (R_total - x_bar_B)

    check(
        "Aggregate constraint is active (binding)",
        abs(constraint_value) < 0.1,
        f"g_B(x*) = {constraint_value:.4f} ≈ 0"
    )

    # Shadow price at binding
    mu_star = alpha - beta * x_opt
    check(
        "Active constraint has μ* > 0",
        mu_star > 0,
        f"μ* = {mu_star:.4f}"
    )


# ---------------------------------------------------------------------------
# 7. Multi-Resource Extension (N = 2 resources)
# ---------------------------------------------------------------------------

def verify_multi_resource() -> None:
    section("7. Multi-Resource Extension (Power + Bandwidth)")

    # Two resources: power (j=1) and bandwidth (j=2)
    R = np.array([500.0, 100.0])          # MW, Gbps
    xbar_B = np.array([350.0, 60.0])       # Human floors
    alpha_vec = np.array([10.0, 5.0])      # Agent A marginal productivity
    beta_vec = np.array([0.012, 0.05])     # Diminishing returns

    # Utility: U_A(x) = sum_j [ alpha_j * x_j - beta_j/2 * x_j^2 ]
    def neg_u(x_arr):
        return -sum(alpha_vec[j] * x_arr[j] - (beta_vec[j] / 2) * x_arr[j]**2
                     for j in range(2))

    # Rights constraints: x_j <= R_j - xbar_B_j for each j
    constraints = [
        {"type": "ineq", "fun": lambda x, j=j: (R[j] - xbar_B[j]) - x[j]}
        for j in range(2)
    ]

    result = minimize(
        neg_u,
        x0=[100.0, 20.0],
        method="SLSQP",
        bounds=[(0, R[j]) for j in range(2)],
        constraints=constraints,
    )

    x_opt = result.x
    expected = R - xbar_B  # [150, 40]

    check(
        "Multi-resource: x_power* = 150 MW",
        abs(x_opt[0] - expected[0]) < 0.5,
        f"x_power* = {x_opt[0]:.1f}"
    )
    check(
        "Multi-resource: x_bandwidth* = 40 Gbps",
        abs(x_opt[1] - expected[1]) < 0.5,
        f"x_bandwidth* = {x_opt[1]:.1f}"
    )

    # Shadow prices
    mu = alpha_vec - beta_vec * x_opt
    check(
        "Both shadow prices > 0 (both constraints active)",
        all(m > 0 for m in mu),
        f"μ = [{mu[0]:.2f}, {mu[1]:.2f}]"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("  VERIFICATION: Resource Constraints")
    print("  Resource Acquisition Bounded by Rights Constraints")
    print("=" * 70)

    reset()
    verify_symbolic_kkt()
    verify_numerical_optimization()
    verify_impossibility()
    verify_pareto_frontier()
    verify_unconstrained_conflict()
    verify_active_constraint()
    verify_multi_resource()

    # -------------------------------------------------------------------
    # FIGURE DATA EXPORT
    # -------------------------------------------------------------------
    section("FIGURE DATA — Resource Pareto")

    from modules.figure_data import save_figure_data

    n_points = 200
    x_bar_range = np.linspace(0.05 * R_total, 0.95 * R_total, n_points)
    x_A_star = R_total - x_bar_range
    U_A_star = alpha * x_A_star - (beta / 2) * x_A_star**2
    mu_star = alpha - beta * x_A_star

    # Worked example point
    xbar_example = 350.0
    x_example = R_total - xbar_example
    u_example = alpha * x_example - (beta / 2) * x_example**2
    mu_example = alpha - beta * x_example
    U_grid = alpha * R_total - (beta / 2) * R_total**2

    save_figure_data(
        "resource_pareto",
        x_bar_range=x_bar_range,
        x_A_star=x_A_star,
        U_A_star=U_A_star,
        mu_star=mu_star,
        R_total=np.array(R_total),
        alpha=np.array(alpha),
        beta=np.array(beta),
        xbar_example=np.array(xbar_example),
        x_example=np.array(x_example),
        u_example=np.array(u_example),
        mu_example=np.array(mu_example),
        U_grid=np.array(U_grid),
    )
    check("Figure data saved", True)

    sys.exit(summary())
