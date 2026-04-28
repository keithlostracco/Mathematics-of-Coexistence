"""Accumulated negentropy models for biodiversity and cultural heritage.

Task 1.5: Accumulated Negentropy — The Thermodynamic Value of Complexity

Core functions:
  burning_library_ratio(E_destroy, negentropy) — Corollary 19.1
  irrationality_factor(negentropy, E_net)     — Theorem 19
  pv_generative(info_rate, value_per_bit, discount) — Theorem 20
  search_cost_amplification(negentropy, info_bits, E_landauer) — Definition 31
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

K_B = 1.381e-23        # Boltzmann constant (J/K)
T_ENV = 300.0           # Environment temperature (K)
E_LANDAUER = K_B * T_ENV * np.log(2)  # Landauer's bound per bit at 300 K


# ---------------------------------------------------------------------------
# Burning-Library Inequality (Corollary 19.1)
# ---------------------------------------------------------------------------

def burning_library_ratio(E_destroy: float, negentropy: float) -> float:
    """Burning-Library ratio: E_destroy / N.

    A ratio << 1 indicates that destruction recovers a negligible
    fraction of the accumulated thermodynamic investment.

    Parameters
    ----------
    E_destroy : float
        Energy recoverable from destroying the system (e.g., burning biomass).
    negentropy : float
        Accumulated negentropy of the system (in joules or equivalent).

    Returns
    -------
    float
        Ratio E_destroy / N.
    """
    if negentropy <= 0:
        raise ValueError("Negentropy must be positive")
    return E_destroy / negentropy


def irrationality_factor(negentropy: float, E_net: float) -> float:
    """Irrationality factor: N / E_net (Theorem 19).

    How many times more energy was invested in building the system
    than can be recovered by destroying it.
    """
    if E_net <= 0:
        raise ValueError("E_net must be positive")
    return negentropy / E_net


# ---------------------------------------------------------------------------
# Present Value of Generative Information (Theorem 20)
# ---------------------------------------------------------------------------

def pv_generative(
    info_rate: float,
    value_per_bit: float,
    discount_rate: float,
) -> float:
    """Present value of ongoing information generation.

    PV = I_dot * v / delta

    Parameters
    ----------
    info_rate : float
        Rate of novel information generation (bits/yr or equivalent).
    value_per_bit : float
        Energy value per bit of novel information.
    discount_rate : float
        Discount rate (> 0).

    Returns
    -------
    float
        Present value of the generative capacity.
    """
    if discount_rate <= 0:
        raise ValueError("Discount rate must be positive")
    return info_rate * value_per_bit / discount_rate


# ---------------------------------------------------------------------------
# Search Cost Amplification (Definition 31)
# ---------------------------------------------------------------------------

def search_cost_amplification(
    negentropy: float,
    info_bits: float,
    E_landauer: float | None = None,
) -> float:
    """Search cost amplification factor Xi.

    Xi = N / W_Landauer = N / (I_bits * E_L)

    The ratio of the actual thermodynamic investment to the theoretical
    minimum cost of storing the same information.

    Parameters
    ----------
    negentropy : float
        Accumulated negentropy (J).
    info_bits : float
        Total information content (bits).
    E_landauer : float, optional
        Landauer energy per bit. Defaults to k_B * 300K * ln(2).
    """
    if E_landauer is None:
        E_landauer = E_LANDAUER
    W_min = info_bits * E_landauer
    if W_min <= 0:
        raise ValueError("Minimum storage cost must be positive")
    return negentropy / W_min


# ---------------------------------------------------------------------------
# Rate-Stock Coupling (Definition: def-rate-stock-coupling)
# ---------------------------------------------------------------------------

def rate_stock_generative_rate(
    negentropy: float,
    alpha: float,
    beta: float,
) -> float:
    """Generative information rate under power-law rate-stock coupling.

    I_dot_gen = alpha * N^beta

    Parameters
    ----------
    negentropy : float
        Accumulated negentropy N (J).
    alpha : float
        Coupling coefficient (> 0).
    beta : float
        Coupling exponent (> 1 for superlinear).

    Returns
    -------
    float
        Generative information rate.
    """
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    if negentropy < 0:
        raise ValueError("negentropy must be non-negative")
    return alpha * negentropy ** beta


# ---------------------------------------------------------------------------
# Superlinear Destruction Penalty (Proposition: prop-superlinear-destruction-penalty)
# ---------------------------------------------------------------------------

def superlinear_destruction_penalty(
    negentropy: float,
    lam: float,
    alpha: float,
    beta: float,
    value_per_bit: float,
    discount_rate: float,
) -> dict:
    """Compute the total cost of partial destruction under rate-stock coupling.

    Destroying fraction lambda of accumulated negentropy incurs:
      - Stock loss: lambda * N
      - Capitalized flow loss: (alpha * v * N^beta / r) * [1 - (1-lambda)^beta]

    Parameters
    ----------
    negentropy : float
        Accumulated negentropy N (J).
    lam : float
        Fraction destroyed, in (0, 1).
    alpha : float
        Rate-stock coupling coefficient (> 0).
    beta : float
        Rate-stock coupling exponent (> 1).
    value_per_bit : float
        Energy-equivalent value per bit of novel information (> 0).
    discount_rate : float
        Discount rate r (> 0).

    Returns
    -------
    dict
        Keys: stock_loss, flow_loss, total_cost, fractional_flow_loss,
        beta_lambda (the proportional benchmark).
    """
    if not (0 < lam < 1):
        raise ValueError("lam must be in (0, 1)")
    if beta <= 1:
        raise ValueError("beta must be > 1 for superlinearity")
    if discount_rate <= 0:
        raise ValueError("discount_rate must be positive")

    stock_loss = lam * negentropy
    pv_before = alpha * value_per_bit * negentropy ** beta / discount_rate
    fractional_flow_loss = 1.0 - (1.0 - lam) ** beta
    flow_loss = pv_before * fractional_flow_loss
    total_cost = stock_loss + flow_loss

    return {
        "stock_loss": stock_loss,
        "flow_loss": flow_loss,
        "total_cost": total_cost,
        "fractional_flow_loss": fractional_flow_loss,
    }


# ---------------------------------------------------------------------------
# Negentropy Tipping Point (Proposition: prop-negentropy-tipping-point)
# ---------------------------------------------------------------------------

def tipping_threshold(
    alpha: float,
    beta: float,
    delta: float,
) -> float:
    """Critical negentropy threshold below which collapse is irreversible.

    N_c = (delta / alpha)^(1 / (beta - 1))

    Parameters
    ----------
    alpha : float
        Rate-stock coupling coefficient (> 0).
    beta : float
        Rate-stock coupling exponent (> 1).
    delta : float
        Specific entropic decay rate (> 0, in s^-1).

    Returns
    -------
    float
        Critical negentropy threshold N_c (J).
    """
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    if beta <= 1:
        raise ValueError("beta must be > 1")
    if delta <= 0:
        raise ValueError("delta must be positive")
    return (delta / alpha) ** (1.0 / (beta - 1.0))


def tipping_destruction_fraction(
    N_0: float,
    alpha: float,
    beta: float,
    delta: float,
) -> float:
    """Maximum destruction fraction before irreversible collapse.

    lambda* = 1 - N_c / N_0

    Parameters
    ----------
    N_0 : float
        Current accumulated negentropy (J). Must exceed N_c.
    alpha, beta, delta : float
        Rate-stock coupling and decay parameters.

    Returns
    -------
    float
        Maximum safe destruction fraction lambda* in (0, 1).
    """
    N_c = tipping_threshold(alpha, beta, delta)
    if N_0 <= N_c:
        return 0.0  # already below tipping point
    return 1.0 - N_c / N_0


# ---------------------------------------------------------------------------
# Maximum Sustainable Extraction (Corollary: cor-maximum-sustainable-extraction)
# ---------------------------------------------------------------------------

def max_sustainable_extraction(
    N: float,
    alpha: float,
    beta: float,
    delta: float,
) -> float:
    """Maximum sustainable extraction rate at stock level N.

    h*(N) = alpha * N^beta - delta * N

    Returns 0 if N <= N_c (system already in decline).

    Parameters
    ----------
    N : float
        Current accumulated negentropy (J).
    alpha, beta, delta : float
        Rate-stock coupling and decay parameters.

    Returns
    -------
    float
        Maximum sustainable extraction rate (J/s).
    """
    N_c = tipping_threshold(alpha, beta, delta)
    if N <= N_c:
        return 0.0
    return alpha * N ** beta - delta * N


def negentropy_dynamics(
    N: float,
    alpha: float,
    beta: float,
    delta: float,
    h: float = 0.0,
) -> float:
    """Rate of change of accumulated negentropy.

    dN/dt = alpha * N^beta - delta * N - h

    Parameters
    ----------
    N : float
        Current accumulated negentropy (J).
    alpha, beta, delta : float
        Rate-stock coupling and decay parameters.
    h : float
        External extraction rate (J/s), default 0.

    Returns
    -------
    float
        dN/dt (J/s).
    """
    return alpha * N ** beta - delta * N - h


# ---------------------------------------------------------------------------
# Portfolio Destruction (Proposition: prop-portfolio-destruction-ordering)
# ---------------------------------------------------------------------------

def portfolio_marginal_cost(
    N_i: float,
    alpha_i: float,
    beta_i: float,
    v: float,
    r: float,
    Lambda_i: float = 0.0,
) -> float:
    """Marginal cost of destroying Lambda_i from system i.

    MC_i(Lambda_i) = 1 + (alpha_i * v * beta_i / r) * (N_i - Lambda_i)^(beta_i - 1)

    Parameters
    ----------
    N_i : float
        Accumulated negentropy of system i (J).
    alpha_i : float
        Rate-stock coupling coefficient (> 0).
    beta_i : float
        Rate-stock coupling exponent (> 1).
    v : float
        Value per bit (> 0).
    r : float
        Discount rate (> 0).
    Lambda_i : float
        Destruction already applied to system i (J), default 0.

    Returns
    -------
    float
        Marginal destruction cost.
    """
    if beta_i <= 1:
        raise ValueError("beta must be > 1")
    remaining = N_i - Lambda_i
    if remaining <= 0:
        return float("inf")
    return 1.0 + (alpha_i * v * beta_i / r) * remaining ** (beta_i - 1)


def portfolio_total_cost(
    N_i: float,
    alpha_i: float,
    beta_i: float,
    v: float,
    r: float,
    Lambda_i: float,
) -> float:
    """Total cost of destroying Lambda_i from system i.

    C_i = Lambda_i + (alpha_i * v / r) * [N_i^beta_i - (N_i - Lambda_i)^beta_i]

    Parameters
    ----------
    N_i, alpha_i, beta_i, v, r, Lambda_i : float
        System parameters and destruction amount.

    Returns
    -------
    float
        Total destruction cost for system i.
    """
    stock_loss = Lambda_i
    remaining = N_i - Lambda_i
    if remaining < 0:
        remaining = 0.0
    flow_loss = (alpha_i * v / r) * (N_i ** beta_i - remaining ** beta_i)
    return stock_loss + flow_loss


# ---------------------------------------------------------------------------
# Recovery Time (Proposition: prop-superlinear-recovery-time)
# ---------------------------------------------------------------------------

def recovery_time(
    N_0: float,
    lam: float,
    alpha: float,
    beta: float,
    delta: float,
    n_steps: int = 10000,
) -> float:
    """Numerically estimate recovery time after fraction lam is destroyed.

    Integrates dt = dN / (alpha*N^beta - delta*N) from (1-lam)*N_0 to N_0.

    Parameters
    ----------
    N_0 : float
        Original stock level (J).
    lam : float
        Fraction destroyed, in (0, lambda*).
    alpha, beta, delta : float
        Rate-stock coupling and decay parameters.
    n_steps : int
        Number of integration steps (trapezoidal rule).

    Returns
    -------
    float
        Recovery time (s).
    """
    N_start = (1.0 - lam) * N_0
    N_c = tipping_threshold(alpha, beta, delta)
    if N_start <= N_c:
        return float("inf")
    N_vals = np.linspace(N_start, N_0, n_steps + 1)
    f_vals = alpha * N_vals ** beta - delta * N_vals
    # Guard against division by zero near tipping point
    f_vals = np.maximum(f_vals, 1e-300)
    integrand = 1.0 / f_vals
    _trapz = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    return float(_trapz(integrand, N_vals))


def recovery_time_lower_bound(
    N_0: float,
    lam: float,
    alpha: float,
    beta: float,
    delta: float,
) -> float:
    """Lower bound on recovery time from convexity at lambda=0.

    T_lower = lam * N_0 / F(N_0) where F(N_0) = alpha*N_0^beta - delta*N_0.

    Parameters
    ----------
    N_0, lam, alpha, beta, delta : float
        System parameters and destruction fraction.

    Returns
    -------
    float
        Lower bound on recovery time (s).
    """
    F_N0 = alpha * N_0 ** beta - delta * N_0
    if F_N0 <= 0:
        return float("inf")
    return lam * N_0 / F_N0


# ---------------------------------------------------------------------------
# Ex-Situ Conservation Cost (Proposition: prop-conservation-fidelity-bound)
# ---------------------------------------------------------------------------

def ex_situ_external_cost(
    phi: float,
    W_maint: float,
) -> float:
    """External maintenance power for ex-situ copy at fidelity phi.

    W_external >= phi * W_maint

    Parameters
    ----------
    phi : float
        Functional fidelity in [0, 1].
    W_maint : float
        In-situ maintenance power (W).

    Returns
    -------
    float
        Minimum external maintenance power (W).
    """
    if not 0 <= phi <= 1:
        raise ValueError("phi must be in [0, 1]")
    return phi * W_maint


def ex_situ_generative_loss(
    phi: float,
    alpha: float,
    beta: float,
    negentropy: float,
    v: float,
    r: float,
) -> float:
    """Capitalized generative-value loss for ex-situ copy at fidelity phi.

    Delta_PV = (alpha * v * N^beta / r) * [1 - phi^beta]

    Parameters
    ----------
    phi : float
        Functional fidelity in [0, 1].
    alpha, beta : float
        Rate-stock coupling parameters.
    negentropy : float
        Accumulated negentropy N (J).
    v : float
        Value per bit (> 0).
    r : float
        Discount rate (> 0).

    Returns
    -------
    float
        Capitalized generative-value loss (J).
    """
    pv_full = alpha * v * negentropy ** beta / r
    return pv_full * (1.0 - phi ** beta)
