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
