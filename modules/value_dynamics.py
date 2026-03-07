"""Value dynamics models for coexistence potential and orbital mechanics.

Task 1.6: Value Dynamics — Orbital Mechanics of Ethical Relationships

Core functions:
  coexistence_potential(r, M, G, tau, gamma_Bi) — V(r) potential
  optimal_coupling(tau, G)                     — r* = 2τ/G
  well_depth(G, M, tau)                        — D = G²M / (4τ)
  min_hec_mass(gamma_Bi, tau, G)               — M_min for bound orbit
  discriminant(G, M, gamma_Bi, tau)            — Δ = G²M² - 4γBiτM
  coexistence_band(G, M, gamma_Bi, tau)        — (r_-, r_+) thresholds
  freedom_bandwidth(G, M, gamma_Bi, tau)       — w = r_+ - r_-
  gini_to_r(gini) / r_to_gini(r)              — Gini ↔ coupling mapping
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Gini ↔ coupling-distance mapping
# ---------------------------------------------------------------------------

def gini_to_r(gini: float) -> float:
    """Map Gini coefficient to coupling distance: r = g / (1 - g).

    Parameters
    ----------
    gini : float
        Gini coefficient in [0, 1).

    Returns
    -------
    float
        Coupling distance r >= 0.
    """
    if gini < 0 or gini >= 1:
        raise ValueError(f"Gini must be in [0, 1), got {gini}")
    return gini / (1.0 - gini)


def r_to_gini(r: float) -> float:
    """Map coupling distance to Gini: g = r / (1 + r).

    Parameters
    ----------
    r : float
        Coupling distance (>= 0).

    Returns
    -------
    float
        Gini coefficient in [0, 1).
    """
    if r < 0:
        raise ValueError(f"r must be >= 0, got {r}")
    return r / (1.0 + r)


# ---------------------------------------------------------------------------
# Coexistence Potential (Definition 37, Theorem 24)
# ---------------------------------------------------------------------------

def coexistence_potential(
    r: float,
    M: float,
    G: float = 1.0,
    tau: float = 0.214,
    gamma_Bi: float = 0.1,
) -> float:
    """Coexistence potential V(r) = τM/r² − GM/r + γBi.

    Parameters
    ----------
    r : float
        Coupling distance (> 0).
    M : float
        HEC mass (GDP or energy).
    G : float
        Gravitational coupling strength.
    tau : float
        Autonomy drive (centrifugal-like parameter).
    gamma_Bi : float
        Boundary maintenance cost (γ·Bi product).
    """
    return tau * M / r**2 - G * M / r + gamma_Bi


def optimal_coupling(tau: float, G: float) -> float:
    """Stable equilibrium coupling distance: r* = 2τ/G."""
    return 2.0 * tau / G


def well_depth(G: float, M: float, tau: float) -> float:
    """Potential well depth at the attractor: D = G²M / (4τ)."""
    return G**2 * M / (4.0 * tau)


def min_hec_mass(gamma_Bi: float, tau: float, G: float) -> float:
    """Minimum HEC mass for a bound orbit: M_min = 4γBi·τ / G²."""
    return 4.0 * gamma_Bi * tau / G**2


# ---------------------------------------------------------------------------
# Coexistence Band (Theorem 24)
# ---------------------------------------------------------------------------

@dataclass
class CoexistenceBand:
    """Result of coexistence band computation."""
    discriminant: float     # Δ = G²M² - 4γBiτM
    r_minus: float          # Inner boundary (dissolution threshold)
    r_plus: float           # Outer boundary (starvation threshold)
    bandwidth: float        # w = r_+ - r_-
    gini_minus: float       # Gini at r_-
    gini_plus: float        # Gini at r_+
    bound: bool             # True if Δ > 0 (bound orbit exists)


def discriminant(G: float, M: float, gamma_Bi: float, tau: float) -> float:
    """Coexistence discriminant: Δ = G²M² - 4γBi·τ·M."""
    return G**2 * M**2 - 4.0 * gamma_Bi * tau * M


def coexistence_band(
    G: float,
    M: float,
    gamma_Bi: float,
    tau: float,
) -> CoexistenceBand:
    """Compute the stable coexistence band [r_-, r_+].

    The band boundaries come from setting V(r) = 0 (the viability boundary)
    and solving the resulting quadratic in r.

    r_± = (GM ± √Δ) / (2γBi)  where Δ = G²M² - 4γBiτM.
    """
    Delta = discriminant(G, M, gamma_Bi, tau)
    if Delta < 0:
        return CoexistenceBand(
            discriminant=Delta,
            r_minus=float('nan'),
            r_plus=float('nan'),
            bandwidth=0.0,
            gini_minus=float('nan'),
            gini_plus=float('nan'),
            bound=False,
        )
    sqrt_Delta = math.sqrt(Delta)
    denom = 2.0 * gamma_Bi
    r_minus = (G * M - sqrt_Delta) / denom
    r_plus = (G * M + sqrt_Delta) / denom

    return CoexistenceBand(
        discriminant=Delta,
        r_minus=r_minus,
        r_plus=r_plus,
        bandwidth=r_plus - r_minus,
        gini_minus=r_to_gini(r_minus) if r_minus >= 0 else float('nan'),
        gini_plus=r_to_gini(r_plus) if r_plus >= 0 else float('nan'),
        bound=True,
    )


def freedom_bandwidth(G: float, M: float, gamma_Bi: float, tau: float) -> float:
    """Freedom bandwidth w = √Δ / γBi = r_+ - r_-."""
    Delta = discriminant(G, M, gamma_Bi, tau)
    if Delta < 0:
        return 0.0
    return math.sqrt(Delta) / gamma_Bi
