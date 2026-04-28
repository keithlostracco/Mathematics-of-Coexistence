"""Information theory models for micro-friction and accumulated negentropy.

Task 1.3: Micro-Friction — Information Entropy of Subtle Wrongs
Task 1.5: Accumulated Negentropy (placeholder for future)

Core functions:
  binary_entropy(q)         — h(q) = -q log2 q - (1-q) log2(1-q)
  bsc_capacity(q)           — C = 1 - h(q)
  redundancy_factor(q)      — rho = 1/C(q)
  decision_cost_binary(q, alpha_H, alpha_L, beta) — Theorem 8
  verification_overhead(q)  — Theorem 9 (relative to honest cost)
  deception_cost_min(q, ...)       — Corollary 9.1
  network_verification_tax(q_bar, M, W_honest) — Section 5.3
  cascade_cost_info(delta_H, W_bit, eta_info, M, E_bar, epsilon) — Section 5.5
  steady_state_info_friction(nu_micro, eta_info, delta_H, W_bit, epsilon) — Section 5.6
  bsc_series_q_eff(d, q)        — Proposition: Serial BSC Composition
  bsc_series_capacity(d, q)     — End-to-end capacity for serial pipelines
  pipeline_collapse_threshold(d, C_min) — Corollary: Pipeline Collapse Threshold

All logarithms are base-2 (bits) unless otherwise noted.
"""

from __future__ import annotations

import numpy as np


# --------------------------------------------------------------------------- #
# 1. Shannon Information Theory Primitives
# --------------------------------------------------------------------------- #

def binary_entropy(q: float | np.ndarray) -> float | np.ndarray:
    """Binary entropy function h(q) = -q log2(q) - (1-q) log2(1-q).

    Parameters
    ----------
    q : float or array
        Error probability in [0, 0.5].  Values at the boundary (0 or 0.5)
        are handled with the convention 0 log 0 = 0.

    Returns
    -------
    h : float or array
        Binary entropy in bits.
    """
    q = np.asarray(q, dtype=float)
    h = np.zeros_like(q)
    mask = (q > 0) & (q < 1)
    h[mask] = -q[mask] * np.log2(q[mask]) - (1 - q[mask]) * np.log2(1 - q[mask])
    return float(h) if h.ndim == 0 else h


def bsc_capacity(q: float | np.ndarray) -> float | np.ndarray:
    """BSC channel capacity: C(q) = 1 - h(q).

    Parameters
    ----------
    q : float or array
        Error probability in [0, 0.5].

    Returns
    -------
    C : float or array
        Capacity in bits per channel use.
    """
    return 1.0 - binary_entropy(q)


def redundancy_factor(q: float | np.ndarray) -> float | np.ndarray:
    """Redundancy factor rho(q) = 1 / C(q) = 1 / (1 - h(q)).

    Parameters
    ----------
    q : float or array
        Error probability in [0, 0.5).  At q=0.5, capacity is 0 and
        the redundancy factor is infinite.

    Returns
    -------
    rho : float or array
        Number of observations per bit of state information.
    """
    C = bsc_capacity(q)
    C = np.asarray(C, dtype=float)
    result = np.where(C > 0, 1.0 / C, np.inf)
    return float(result) if result.ndim == 0 else result


# --------------------------------------------------------------------------- #
# 2. Decision Cost (Theorem 8)
# --------------------------------------------------------------------------- #

def decision_cost_binary(
    q: float | np.ndarray,
    alpha_H: float,
    alpha_L: float,
    beta: float,
) -> float | np.ndarray:
    """Decision cost of deception in the binary-state quadratic model (Theorem 8).

    ΔU_B(q) = q(1-q)(α_H - α_L)² / (2β)

    Parameters
    ----------
    q : float or array
        Deception rate (BSC error probability).
    alpha_H : float
        High marginal yield.
    alpha_L : float
        Low marginal yield.
    beta : float
        Diminishing-returns parameter.

    Returns
    -------
    delta_U : float or array
        Decision cost in energy units.
    """
    q = np.asarray(q, dtype=float)
    return q * (1 - q) * (alpha_H - alpha_L) ** 2 / (2 * beta)


def decision_cost_max(
    alpha_H: float,
    alpha_L: float,
    beta: float,
) -> float:
    """Maximum decision cost (at q=0.5): (α_H - α_L)² / (8β)."""
    return (alpha_H - alpha_L) ** 2 / (8 * beta)


# --------------------------------------------------------------------------- #
# 3. Verification Cost (Theorem 9)
# --------------------------------------------------------------------------- #

def verification_overhead_ratio(q: float | np.ndarray) -> float | np.ndarray:
    """Verification overhead as a ratio of honest processing cost.

    ΔW / W_honest = h(q) / (1 - h(q))

    Parameters
    ----------
    q : float or array
        Deception rate in [0, 0.5).

    Returns
    -------
    ratio : float or array
        Dimensionless verification overhead ratio.
    """
    h = binary_entropy(q)
    h = np.asarray(h, dtype=float)
    denom = 1.0 - h
    result = np.where(denom > 0, h / denom, np.inf)
    return float(result) if result.ndim == 0 else result


def verification_cost(
    q: float | np.ndarray,
    W_honest: float,
) -> float | np.ndarray:
    """Absolute verification overhead energy (Theorem 9).

    ΔW(q) = W_honest · h(q) / (1 - h(q))
    """
    return W_honest * verification_overhead_ratio(q)


# --------------------------------------------------------------------------- #
# 4. Deception Cost Minimum (Corollary 9.1)
# --------------------------------------------------------------------------- #

def deception_cost_min(
    q: float,
    alpha_H: float,
    alpha_L: float,
    beta: float,
    W_honest: float,
) -> float:
    """Minimum unavoidable cost of deception (Corollary 9.1).

    D_B(q) = min(ΔU_B(q), ΔW(q))

    The victim pays at least this much — either in bad decisions or verification.
    """
    du = float(decision_cost_binary(q, alpha_H, alpha_L, beta))
    dw = float(verification_cost(q, W_honest))
    return min(du, dw)


# --------------------------------------------------------------------------- #
# 5. Network-Level Costs (Section 5)
# --------------------------------------------------------------------------- #

def network_verification_tax(
    q_bar: float,
    M: int | float,
    W_honest: float,
) -> float:
    """Aggregate verification tax per period (Section 5.3).

    C_verify = M · W_honest · h(q̄) / (1 - h(q̄))
    """
    return M * verification_cost(q_bar, W_honest)


def cascade_cost_info(
    delta_H: float,
    W_bit: float,
    eta_info: float,
    M: int | float,
    E_bar: float,
    epsilon: float,
) -> float:
    """Cascading cost from a single deceptive act (Section 5.5).

    C_cascade = η_info · ΔH · W_bit · M · Ē / ε
    """
    return eta_info * delta_H * W_bit * M * E_bar / epsilon


def steady_state_info_friction(
    nu_micro: float,
    eta_info: float,
    delta_H: float,
    W_bit: float,
    epsilon: float,
) -> float:
    """Steady-state informational friction coefficient (Section 5.6).

    φ_info = ν_micro · η_info · ΔH · W_bit / ε
    """
    return nu_micro * eta_info * delta_H * W_bit / epsilon


# --------------------------------------------------------------------------- #
# 6. Serial BSC Composition (Proposition: Serial BSC Composition,
#    Corollary: Pipeline Collapse Threshold)
# --------------------------------------------------------------------------- #

def bsc_series_q_eff(
    d: int,
    q: float | np.ndarray,
) -> float | np.ndarray:
    """Effective error rate of d BSCs in series with uniform per-stage rate q.

    q_eff(d, q) = (1 - (1 - 2q)^d) / 2

    Parameters
    ----------
    d : int
        Number of stages (pipeline depth), d >= 1.
    q : float or array
        Per-stage error probability in [0, 0.5].

    Returns
    -------
    q_eff : float or array
        Effective end-to-end error probability of the composite BSC.
    """
    if d < 1:
        raise ValueError("Pipeline depth d must be >= 1")
    q = np.asarray(q, dtype=float)
    q_eff = (1.0 - (1.0 - 2.0 * q) ** d) / 2.0
    return float(q_eff) if q_eff.ndim == 0 else q_eff


def bsc_series_capacity(
    d: int,
    q: float | np.ndarray,
) -> float | np.ndarray:
    """End-to-end capacity of d BSCs in series with uniform per-stage rate q.

    C_eff(d, q) = 1 - h(q_eff(d, q))
    """
    return 1.0 - binary_entropy(bsc_series_q_eff(d, q))


def _binary_entropy_inverse(target_h: float) -> float:
    """Inverse of the binary entropy function on [0, 0.5].

    Returns the unique q in [0, 0.5] satisfying h(q) = target_h, where
    target_h in [0, 1]. Uses bisection to floating-point tolerance.
    """
    if not 0.0 <= target_h <= 1.0:
        raise ValueError("target_h must be in [0, 1]")
    if target_h == 0.0:
        return 0.0
    if target_h == 1.0:
        return 0.5
    lo, hi = 0.0, 0.5
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if float(binary_entropy(mid)) < target_h:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def pipeline_collapse_threshold(
    d: int,
    C_min: float,
) -> float:
    """Maximum per-stage corruption rate q*(d; C_min) preserving end-to-end capacity.

    q*(d; C_min) = (1 - (1 - 2 q_max)^(1/d)) / 2,    q_max = h^{-1}(1 - C_min)

    The pipeline of depth d retains C_eff(d, q) >= C_min iff q <= q*(d; C_min).

    Parameters
    ----------
    d : int
        Pipeline depth, d >= 1.
    C_min : float
        Minimum acceptable end-to-end channel capacity in (0, 1).

    Returns
    -------
    q_star : float
        Critical per-stage error probability; the pipeline collapses (C_eff < C_min)
        for any per-stage rate q > q_star.
    """
    if d < 1:
        raise ValueError("Pipeline depth d must be >= 1")
    if not 0.0 < C_min < 1.0:
        raise ValueError("C_min must be in (0, 1)")
    q_max = _binary_entropy_inverse(1.0 - C_min)
    return (1.0 - (1.0 - 2.0 * q_max) ** (1.0 / d)) / 2.0
