"""Lagrangian constraint models for rights and resource allocation.

Task 1.1: Lagrangian Constraints — Rights as Inequality Constraints

Core functions:
  quadratic_utility(x, alpha, beta) — U(x) = alpha*x - (beta/2)*x^2
  marginal_utility(x, alpha, beta)  — dU/dx = alpha - beta*x
  unconstrained_optimum(alpha, beta) — x° = alpha/beta
  ve_two_agent(alpha_A, beta_A, alpha_B, beta_B, R) — Variational Equilibrium
  shadow_price_two_agent(...)       — Shadow price at VE
  social_welfare(allocations, params) — Sum of utilities
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Quadratic Utility Model
# ---------------------------------------------------------------------------

def quadratic_utility(x: float, alpha: float, beta: float) -> float:
    """Quadratic utility: U(x) = alpha*x - (beta/2)*x^2."""
    return alpha * x - (beta / 2.0) * x ** 2


def marginal_utility(x: float, alpha: float, beta: float) -> float:
    """Marginal utility: dU/dx = alpha - beta*x."""
    return alpha - beta * x


def unconstrained_optimum(alpha: float, beta: float) -> float:
    """Unconstrained optimum: x° = alpha / beta."""
    if beta <= 0:
        raise ValueError("beta must be positive")
    return alpha / beta


# ---------------------------------------------------------------------------
# Two-Agent Variational Equilibrium (Theorem 3)
# ---------------------------------------------------------------------------

@dataclass
class VEResult:
    """Result of a two-agent Variational Equilibrium computation."""
    x_A: float          # VE allocation to agent A
    x_B: float          # VE allocation to agent B
    shadow_price: float  # Shared shadow price lambda*
    U_A: float          # Utility of A at VE
    U_B: float          # Utility of B at VE
    total_welfare: float # U_A + U_B


def ve_two_agent(
    alpha_A: float, beta_A: float,
    alpha_B: float, beta_B: float,
    R: float,
) -> VEResult:
    """Compute the two-agent Variational Equilibrium with shared constraint.

    Agents have quadratic utilities U_i(x_i) = alpha_i*x_i - (beta_i/2)*x_i^2
    subject to the shared resource constraint x_A + x_B <= R.

    The VE shadow price (Lagrange multiplier) is:
        lambda* = (x_A° + x_B° - R) / (1/beta_A + 1/beta_B)
    
    VE allocations:
        x_i* = (alpha_i - lambda*) / beta_i

    Parameters
    ----------
    alpha_A, beta_A : float
        Agent A's utility parameters.
    alpha_B, beta_B : float
        Agent B's utility parameters.
    R : float
        Total shared resource.

    Returns
    -------
    VEResult
    """
    x_A_opt = unconstrained_optimum(alpha_A, beta_A)
    x_B_opt = unconstrained_optimum(alpha_B, beta_B)

    excess = x_A_opt + x_B_opt - R
    if excess <= 0:
        # Constraint is not binding
        lam = 0.0
        x_A_star = x_A_opt
        x_B_star = x_B_opt
    else:
        lam = excess / (1.0 / beta_A + 1.0 / beta_B)
        x_A_star = (alpha_A - lam) / beta_A
        x_B_star = (alpha_B - lam) / beta_B

    U_A = quadratic_utility(x_A_star, alpha_A, beta_A)
    U_B = quadratic_utility(x_B_star, alpha_B, beta_B)

    return VEResult(
        x_A=x_A_star,
        x_B=x_B_star,
        shadow_price=lam,
        U_A=U_A,
        U_B=U_B,
        total_welfare=U_A + U_B,
    )


def shadow_price_binding(
    alpha_A: float, beta_A: float,
    alpha_B: float, beta_B: float,
    R: float,
) -> float:
    """Compute the shadow price assuming the constraint binds.

    lambda* = (x_A° + x_B° - R) / (1/beta_A + 1/beta_B)
    """
    excess = (alpha_A / beta_A) + (alpha_B / beta_B) - R
    return max(0.0, excess / (1.0 / beta_A + 1.0 / beta_B))


def social_welfare(
    allocations: list[float],
    params: list[tuple[float, float]],
) -> float:
    """Compute total social welfare for a list of (allocation, (alpha, beta)) pairs.

    Parameters
    ----------
    allocations : list of float
        Resource allocations to each agent.
    params : list of (alpha, beta)
        Utility parameters for each agent.

    Returns
    -------
    float
        Sum of quadratic utilities.
    """
    return sum(
        quadratic_utility(x, alpha, beta)
        for x, (alpha, beta) in zip(allocations, params)
    )


# ---------------------------------------------------------------------------
# Floor Constraint (Minimum Wage / Boundary Constraint)
# ---------------------------------------------------------------------------

def shadow_price_floor(
    alpha: float, beta: float,
    x_floor: float, R: float,
    alpha_other: float, beta_other: float,
) -> float:
    """Shadow price of a floor constraint x_B >= x_floor.

    When the floor binds: x_B = x_floor, x_A = R - x_floor,
    and mu* = alpha_A - beta_A * x_A (marginal utility of the constrained agent).
    
    This is a simplified version; the full problem may have both the resource
    constraint and the floor constraint active simultaneously.
    """
    x_A = R - x_floor
    return marginal_utility(x_A, alpha, beta)
