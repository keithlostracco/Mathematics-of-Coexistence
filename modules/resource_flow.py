"""Resource-flow gradient primitives for credit-as-resource-flow surface.

Implements the alignment coefficient c_iell and flip-boundary helpers
derived in S1 (cooperative-coupling alignment).

Key formula (S1 §4.3 c-def):
    c_iell = [pi*_iell - nu*_iell - (lambda*_ell - eta*_i * alpha_ell)] / phi'_i(M_i)
           = (1/phi'_i) * (dU_i/dx^out_iell)|_*

Sign conventions (S2 §2.3 — loss-form, L-layer):
    Producer loss: -pi*_iell * x^out_iell   (consumption reduces loss)
    Consumer loss: +p_k * x^in_ki            (drawing input raises loss)
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Alignment coefficient (S1 c-def)
# ---------------------------------------------------------------------------

def compute_c_iell(
    pi_star_iell: float,
    nu_star_iell: float,
    lambda_star_ell: float,
    eta_star_i: float,
    alpha_ell: float,
    phi_prime_i: float,
) -> float:
    """Compute the alignment coefficient c_iell.

    c_iell = [pi*_iell - nu*_iell - (lambda*_ell - eta*_i * alpha_ell)] / phi'_i(M_i)
           = (1/phi'_i) * dU_i/dx^out_iell|_*

    Parameters
    ----------
    pi_star_iell : float
        TC-VII flow-dependency price pi*_iell (network's marginal valuation
        of producer i's output ell at VE). >= 0.
    nu_star_iell : float
        Provision-obligation multiplier nu*_iell. >= 0; > 0 iff constraint
        is active per TC-VII thm-positive-constraint-necessity.
    lambda_star_ell : float
        Shared scarcity shadow price for resource ell (same for all agents
        at VE per TC-I cor-symmetry-scarcity).
    eta_star_i : float
        Agent i's admissibility multiplier eta*_i (joule-density unit cost).
    alpha_ell : float
        Energy density of resource ell [joules per unit]. > 0.
    phi_prime_i : float
        Derivative phi'_i(M_i) of the persistence-margin transform. > 0.

    Returns
    -------
    float
        Alignment coefficient c_iell. Non-negative in the canonical
        (unobligated, scarcer-than-joule-density) regime.
    """
    if phi_prime_i <= 0:
        raise ValueError(f"phi_prime_i must be > 0, got {phi_prime_i}")
    numerator = pi_star_iell - nu_star_iell - (lambda_star_ell - eta_star_i * alpha_ell)
    return numerator / phi_prime_i


# ---------------------------------------------------------------------------
# Flip boundaries (S1 §4.5)
# ---------------------------------------------------------------------------

def flip_boundary_a(
    pi_star: float,
    lambda_star: float,
    eta_star: float,
    alpha: float,
) -> float:
    """Channel-(a) obligated flip threshold for nu*_iell.

    The alignment coefficient c_iell < 0 via the obligated channel when:
        nu*_iell > pi*_iell - (lambda*_ell - eta*_i * alpha_ell)

    Returns the threshold nu*_iell value at which c_iell = 0.

    Parameters
    ----------
    pi_star : float    Flow-dependency price pi*_iell.
    lambda_star : float  Scarcity shadow price lambda*_ell.
    eta_star : float   Admissibility multiplier eta*_i.
    alpha : float      Energy density alpha_ell.

    Returns
    -------
    float
        The nu*_iell threshold. If nu*_iell < this value, c_iell > 0
        (aligned). If nu*_iell > this value, c_iell < 0 (flipped).
    """
    return pi_star - (lambda_star - eta_star * alpha)


def flip_boundary_b(
    lambda_star: float,
    eta_star: float,
    alpha: float,
) -> float:
    """Channel-(b) ample-resource flip boundary.

    The alignment coefficient flips via the ample-resource channel when:
        pi*_iell - (lambda*_ell - eta*_i * alpha_ell) <= 0
    i.e., when lambda*_ell <= eta*_i * alpha_ell.

    Returns the scarcity-admissibility gap (lambda* - eta* * alpha).
    Positive gap = scarcer-than-joule-density (canonical, aligned).
    Non-positive gap = ample-resource (flip boundary reached or crossed).

    Parameters
    ----------
    lambda_star : float  Scarcity shadow price.
    eta_star : float     Admissibility multiplier.
    alpha : float        Energy density.

    Returns
    -------
    float
        lambda*_ell - eta*_i * alpha_ell. Positive => scarce resource
        (canonical aligned regime). Zero => boundary. Negative => flip.
    """
    return lambda_star - eta_star * alpha


# ---------------------------------------------------------------------------
# Numerical gradient of U_i w.r.t. x^out (for formula validation V3)
# ---------------------------------------------------------------------------

def numerical_dU_dxout(
    utility_fn,
    x_out_base: float,
    eps: float = 1e-7,
) -> float:
    """Numerically compute dU_i / dx^out_iell at x_out_base.

    Parameters
    ----------
    utility_fn : callable
        U_i(x_out) — scalar function of the single output coordinate.
    x_out_base : float
        Point at which to differentiate.
    eps : float
        Step size for central difference.

    Returns
    -------
    float
        Numerical derivative dU_i/dx^out_iell.
    """
    return (utility_fn(x_out_base + eps) - utility_fn(x_out_base - eps)) / (2 * eps)


# ---------------------------------------------------------------------------
# Inner product alignment measure
# ---------------------------------------------------------------------------

def alignment_inner_product(
    c_iell: float,
    grad_flow_norm_sq: float,
    grad_task_norm_sq: float,
    cos_angle: float = 1.0,
) -> float:
    """Estimate <nabla^flow_i, nabla^task_i> up to the cross-coupling residual.

    Under the derivation's parallel-component assumption (R-2 bounded),
    the dominant contribution is c_iell * ||nabla x^out||^2 * tau_ell.
    This helper returns the signed scalar for sweep bookkeeping.

    Parameters
    ----------
    c_iell : float
        Alignment coefficient.
    grad_flow_norm_sq : float
        Squared norm of the flow gradient component ||nabla^flow_ell||^2.
    grad_task_norm_sq : float
        Squared norm of the task gradient component ||nabla^task_ell||^2.
    cos_angle : float
        Cosine of angle between gradient directions (default 1 = aligned).

    Returns
    -------
    float
        Scalar inner product proxy: c_iell * sqrt(flow_norm^2 * task_norm^2) * cos.
    """
    return c_iell * (grad_flow_norm_sq * grad_task_norm_sq) ** 0.5 * cos_angle
