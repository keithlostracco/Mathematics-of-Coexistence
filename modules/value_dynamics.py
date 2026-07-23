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

The active dissipative boundary (B_i as a state variable):
  CANONICAL_KAPPA / COLLAPSE_FLOOR_FRACTION    — the CHOSEN calibration (not the paper's)
  boundary_scale(B_declared)                   — (B̄, B_min) from declared integrity
  structural_capacity(B_i, B_min, B_bar)       — ζ(B_i) ∈ [0, 1]
  mobility(B_i, mu_0, B_min, B_bar)            — μ(B_i) = μ₀·ζ(B_i)
  net_energy_rate(...)                         — Π(r) at current integrity
  assimilation_rate(r, M, sigma)               — D_assimilate = σM/r³
  repair_rate(...)                             — R_repair = (ρ/κ)·ζ·max(Π,0)
  coupling_velocity(...) / boundary_velocity(...) — the coupled ODE
  floor_net_rate(...) / floor_drain(...)       — Π₀(r), d₀(r)
  repair_capacity_density(rho, kappa, ...)     — q = ρ/(κ(B̄ - B_min))
  repair_viability_margin(...) / is_repair_viable(...)
  boundary_equilibria(...)                     — roots B_u < B_i*, eigenvalues
  surplus_ceiling(...)                         — Π̄ = G²M/(4τ) - γB_min
  basin_of_no_return(...)                      — B_c   (+ _approx variant)
  collapse_envelope(...)                       — h(B_i) >= dB_i/dt
  dissolution_radius(...)                      — r_d   (distinct from r_-)
  penetration_decline_rate(...)                — α
  critical_penetration_depth(...)              — ℓ_c
  starvation_time(...) / basin_crossing_time(...) — t*, t_c
  ActiveBoundary                               — parameter bundle + integrator

Multi-dimensional reduction (TC-XIII):
  omega_norm(r_vec, Omega)                     — ||r||_Omega = sqrt(r^T Omega r)
  in_dissolution_region(r_vec, Omega, r_d)     — Omega-ellipsoidal ball membership
  (the scalar r_d / B_c / Pi_bar / assimilation formulas apply verbatim at r = ||r||_Omega)

Note on the γ/B_i split: the attractor/band functions above take the PRODUCT
`gamma_Bi` because B_i is a constant there.  In the active-dissipative model
B_i is a state variable, so the functions below take `gamma` and `B_i`
separately.  Both conventions are correct in their own scope; do not unify.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Shared numerics
# ---------------------------------------------------------------------------

def _parabola_roots(
    a: float,
    b: float,
    c: float,
    sqrt_disc: float,
) -> tuple[float, float]:
    """Roots x_- <= x_+ of a·x² - b·x + c = 0, evaluated without cancellation.

    Three results in this module are this same parabola and so share these
    numerics:
      * the band boundaries r_±  (a = γBi, b = GM,       c = τM)
      * the fixed-r equilibria   (a = qγ,  b = q·Π₀ - γ, c = d₀)
      * the basin bound B_c      (a = qγ,  b = q·Π̄ - γ,  c = γB_min)
    The basin is the d₀ -> γB_min, Π₀ -> Π̄ limit of the equilibria, in which
    the assimilation drain is dropped.

    The textbook (b ∓ √disc)/(2a) catastrophically cancels on the MINUS branch
    when b² >> 4ac — the q·Π >> γ regime in which the smaller root hugs the
    collapse floor (cf. ``basin_of_no_return_approx``), and the large-M regime
    in which r_- hugs the asymptote τ/G.  There b and √disc agree to nearly
    every bit, so their difference keeps only the few digits that survive the
    subtraction, and the root's DISTANCE from the asymptote — the quantity of
    interest — is what gets destroyed.  So take whichever branch b's sign makes
    an addition, and recover its partner from Vieta's x_-·x_+ = c/a instead of
    subtracting.  Both roots then carry full precision, and the two forms are
    algebraically identical.

    ``sqrt_disc`` is supplied by the caller rather than recomputed here so that
    a single discriminant — the one the caller has already sign-checked —
    governs; re-deriving it from a, b, c could differ in the last ulp and turn
    a marginal disc = 0 into a domain error.
    """
    u = 0.5 * (b + math.copysign(sqrt_disc, b))
    if u == 0.0:                    # b = c = 0: the double root at the origin
        return 0.0, 0.0
    x_1, x_2 = u / a, c / u         # x_1 is the stable branch, x_2 its partner
    return min(x_1, x_2), max(x_1, x_2)


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
    """Compute the stable coexistence band (r_-, r_+).

    The band boundaries come from setting V(r) = 0 (the viability boundary)
    and solving the resulting quadratic in r.

    r_± = (GM ± √Δ) / (2γBi)  where Δ = G²M² - 4γBiτM.

    — the DEFINITION, not the evaluation.  Setting V(r) = 0 clears to the
    parabola γBi·r² - GM·r + τM = 0, so the roots come from
    ``_parabola_roots``: the ∓ form loses r_- to cancellation once G²M² >> 4γBiτM,
    which is the large-M regime in which r_- hugs its asymptote τ/G.  (At
    G=1, γBi=15, τ=0.5 the textbook form is already 0.7% wrong in r_- - τ/G at
    M=1e8 and returns exactly τ/G — correction term entirely gone — by M=1e10.)

    The band is the OPEN set {r > 0 : V(r) < 0}, so it exists only when
    Δ > 0 strictly (equivalently M > M_min).  At M = M_min the band is
    EMPTY: V(r) >= 0 everywhere with equality only at r*, which is marginal
    and non-surviving since survival requires Π(r) > 0 strictly.  Hence the
    existence predicate is `Delta > 0`, not `Delta >= 0`.
    """
    Delta = discriminant(G, M, gamma_Bi, tau)
    if Delta <= 0:
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
    r_minus, r_plus = _parabola_roots(gamma_Bi, G * M, tau * M, sqrt_Delta)

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


# ---------------------------------------------------------------------------
# The Coupled Agent-Boundary System
# (def-structural-capacity, def-boundary-regeneration-rate,
#  def-boundary-degradation-rate)
#
# The boundary is an ACTIVE DISSIPATIVE STRUCTURE, not a passive reservoir:
# the machinery that performs repair — and that executes the coupling
# adjustments of the gradient dynamics — is itself part of the structure it
# maintains, so both capacities degrade with the boundary.  Consequences that
# the code must respect:
#
#   * ζ multiplies BOTH equations (repair AND mobility).  Dropping it from
#     r_dot would let the gradient pull a dying agent home for free.
#   * The collapse endpoint is B_min > 0, never 0.  {B_i <= B_min} is
#     ABSORBING; integrity never reaches zero.
#   * Repair costs κ per unit integrity restored, so the rate is (ρ/κ)·…,
#     never ρ alone.  ρ ∈ (0,1), κ > 1 strictly.
#   * Repair saturates at the reference integrity B̄ (clamp in the integrator).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CALIBRATION CONVENTION FOR THE BOUNDARY PARAMETERS
#
# !! THE NUMBERS BELOW ARE NOT FROM THE PAPER. !!
#
# TC-VI gives NO numeric value for ANY parameter of the active dissipative
# model — σ, ρ, κ, B_min, B̄, μ₀ — and therefore none for the quantities derived
# from them either (B_c, r_d, Π̄, ζ, ℓ_c, α).  Its three worked examples predate
# the boundary rebuild and use only B, γ, M, G, τ.  That silence is deliberate,
# not an oversight, so every claim built on these values must be an ANALYTIC
# property (root ordering, residuals, eigenvalue signs, identities, finite-time
# bounds) rather than a paper-blessed magic number.
#
# What is unified here is only the CONVENTION — the two constants below and the
# B̄/B_min mapping in ``boundary_scale`` — so that there is exactly one place to
# change and audit.  A scenario's own geometry (M, G, τ, γ) and its own σ, ρ, μ₀
# remain that scenario's to choose; they are NOT TC-VI's to unify.
#
# DO NOT cite these as canonical TC-VI parameters.
# ---------------------------------------------------------------------------

CANONICAL_KAPPA = 2.0
"""Repair multiplier κ — !! NOT FROM THE PAPER; CHOSEN. !!

The TC-IV/TC-V baseline (κ = 1 + κ_clear + κ_pen + κ_irr > 1 strictly, so κ = 1
is inadmissible).  Load-bearing, not cosmetic: r_d scales as κ^(1/3), and in the
institutional-collapse scenario κ >= 4 pushes r_d past r* = 1.0 and inverts the
case study into unconditional dissolution.
"""

COLLAPSE_FLOOR_FRACTION = 0.02
"""B_min as a fraction of B̄ — !! NOT FROM THE PAPER; CHOSEN. !!

The collapse floor is 2% of the reference integrity.  Not arbitrary: in the
institutional-collapse and power-concentration scenarios (B̄ = 50) it reproduces
the floor B_min = 1.0 those scripts already used before the boundary rebuild —
their starvation loop halted at B_i = 1.0 and their pre-existing constant
t = ln(B_i⁰)/γ ≈ 13.04 is then exactly the paper's t* = (1/γ)·ln(B_i⁰/B_min).
"""


def boundary_scale(
    B_declared: float,
    floor_fraction: float = COLLAPSE_FLOOR_FRACTION,
) -> tuple[float, float]:
    """Map a scenario's declared integrity to (B̄, B_min) — the ONE door.

    Convention: **the declared B IS the fully-intact reference**, so B̄ =
    B_declared and ζ(B_i⁰) = 1 at t = 0 — the agent starts healthy — and then
    B_min = floor_fraction · B̄.  Callers derive both boundary parameters through
    this function rather than hardcoding their own, so the convention has a
    single point of change and audit.

    The alternative convention (B̄ = 2·B_declared, i.e. the declared integrity is
    half-depleted at t = 0) was rejected by MEASUREMENT, not taste: in the
    institutional-collapse scenario it gives B_u(r*) = 80.2 > B_i = 50, putting
    the institution BELOW the unstable root — it would collapse even parked at
    the attractor, inverting the case study.

    !! The convention and the default fraction are CHOSEN, not paper-sourced —
    see the module comment above. !!

    Parameters
    ----------
    B_declared : float
        The scenario's declared boundary integrity (> 0), read as B̄.
    floor_fraction : float
        B_min/B̄, in (0, 1).  Defaults to ``COLLAPSE_FLOOR_FRACTION``.

    Returns
    -------
    (B_bar, B_min) : tuple[float, float]
        Satisfying 0 < B_min < B_bar, the domain ``structural_capacity`` needs.
    """
    if B_declared <= 0.0:
        raise ValueError(f"B_declared must be > 0, got {B_declared}")
    if not 0.0 < floor_fraction < 1.0:
        raise ValueError(f"floor_fraction must be in (0, 1), got {floor_fraction}")
    return B_declared, floor_fraction * B_declared


def structural_capacity(B_i: float, B_min: float, B_bar: float) -> float:
    """Structural-capacity factor ζ(B_i) = max((B_i - B_min)/(B̄ - B_min), 0).

    The fraction of full repair and mobility capacity retained at integrity
    B_i: ζ(B_min) = 0, ζ(B̄) = 1, increasing on [B_min, B̄].

    Parameters
    ----------
    B_i : float
        Current boundary integrity.  Domain is (B_min, B_bar]; the dynamics
        saturate at the reference integrity, so callers integrating the ODE
        must clamp B_i at B_bar (see ``ActiveBoundary.simulate``).
    B_min : float
        Collapse floor, in (0, B_bar).  Reaching it IS dissolution.
    B_bar : float
        Reference integrity: embodied energy of the fully intact boundary.
    """
    if not 0.0 < B_min < B_bar:
        raise ValueError(f"need 0 < B_min < B_bar, got {B_min}, {B_bar}")
    return max((B_i - B_min) / (B_bar - B_min), 0.0)


def mobility(B_i: float, mu_0: float, B_min: float, B_bar: float) -> float:
    """Health-dependent adjustment rate μ(B_i) = μ₀·ζ(B_i).

    Adjusting the coupling distance is work performed by the same structural
    machinery that performs repair, so mobility dies with the boundary.
    (The stronger variant with a -c_move·|r_dot| drain on B_i is deliberately
    NOT adopted; the capacity factor already carries the essential effect.)
    """
    return mu_0 * structural_capacity(B_i, B_min, B_bar)


def net_energy_rate(
    r: float,
    M: float,
    G: float,
    tau: float,
    gamma: float,
    B_i: float,
) -> float:
    """Net energy rate Π(r) = GM/r - τM/r² - γB_i, read at CURRENT integrity.

    This is -V(r); since B_i is now a state variable, Π and everything defined
    from it (V, r_±, M_min) move as the boundary degrades.  The attractor
    r* = 2τ/G is independent of B_i.
    """
    return G * M / r - tau * M / r**2 - gamma * B_i


def assimilation_rate(r: float, M: float, sigma: float) -> float:
    """Boundary degradation from HEC assimilation: D_assimilate = σM/r³.

    Short-range dominant: 1/r³ decays faster than the 1/r² dissolution cost,
    so active boundary destruction requires closer coupling than autonomy loss.
    """
    return sigma * M / r**3


def repair_rate(
    r: float,
    B_i: float,
    M: float,
    G: float,
    tau: float,
    gamma: float,
    rho: float,
    kappa: float,
    B_min: float,
    B_bar: float,
) -> float:
    """Boundary regeneration rate R_repair = (ρ/κ)·ζ(B_i)·max(Π(r), 0).

    Two mechanisms distinguish this from passive refilling.  Restoring ΔB of
    boundary costs κ·ΔB of energy, so allocated power ρ·max(Π,0) yields
    integrity at rate (ρ/κ)·max(Π,0).  And repair is AUTOCATALYTIC — performed
    by the boundary's own machinery — so R_repair → 0 as B_i → B_min
    regardless of Π: a depleted structure cannot rebuild itself even when
    surplus energy is available.

    Parameters
    ----------
    rho : float
        Repair allocation fraction, in (0, 1).
    kappa : float
        Repair multiplier κ = 1 + κ_clear + κ_pen + κ_irr > 1 (TC-IV).
    """
    if not 0.0 < rho < 1.0:
        raise ValueError(f"rho must be in (0, 1), got {rho}")
    if kappa <= 1.0:
        raise ValueError(f"kappa must be > 1, got {kappa}")
    Pi = net_energy_rate(r, M, G, tau, gamma, B_i)
    zeta = structural_capacity(B_i, B_min, B_bar)
    return (rho / kappa) * zeta * max(Pi, 0.0)


def coupling_velocity(
    r: float,
    B_i: float,
    M: float,
    G: float,
    tau: float,
    mu_0: float,
    B_min: float,
    B_bar: float,
) -> float:
    """Coupling dynamics r_dot = -μ₀·ζ(B_i)·V'(r), with V'(r) = M(Gr - 2τ)/r³.

    ζ appears here as well as in the repair term: a depleted agent cannot
    afford the migration back to the attractor.
    """
    Vp = M * (G * r - 2.0 * tau) / r**3
    return -mu_0 * structural_capacity(B_i, B_min, B_bar) * Vp


def boundary_velocity(
    r: float,
    B_i: float,
    M: float,
    G: float,
    tau: float,
    gamma: float,
    sigma: float,
    rho: float,
    kappa: float,
    B_min: float,
    B_bar: float,
) -> float:
    """Boundary dynamics dB_i/dt = R_repair - D_assimilate - γB_i.

    Valid for B_i > B_min; the state {B_i <= B_min} is absorbing.
    """
    return (
        repair_rate(r, B_i, M, G, tau, gamma, rho, kappa, B_min, B_bar)
        - assimilation_rate(r, M, sigma)
        - gamma * B_i
    )


# ---------------------------------------------------------------------------
# The Healthy Equilibrium (prop-healthy-boundary-equilibrium)
#
# At fixed r the boundary dynamics are quadratic in x = B_i - B_min:
#     dB_i/dt = -q·γ·x² + (q·Π₀(r) - γ)·x - d₀(r)
# a downward parabola with value -d₀ < 0 at x = 0.
# ---------------------------------------------------------------------------

@dataclass
class BoundaryEquilibria:
    """Fixed-r roots of dB_i/dt = 0 (prop-healthy-boundary-equilibrium)."""
    viable: bool        # repair-viability condition holds at this r
    margin: float       # q·Π₀ - (γ + 2√(qγd₀)); > 0 iff viable
    disc: float         # (q·Π₀ - γ)² - 4qγd₀
    B_u: float          # unstable root  B_min + x_-
    B_star: float       # stable root    B_min + x_+  (before B̄ saturation)
    eig_u: float        # +√disc  (unstable: parabola slope at x_-)
    eig_star: float     # -√disc  (stable:   parabola slope at x_+)


def floor_net_rate(
    r: float,
    M: float,
    G: float,
    tau: float,
    gamma: float,
    B_min: float,
) -> float:
    """Floor-level net rate Π₀(r) = GM/r - τM/r² - γB_min."""
    return G * M / r - tau * M / r**2 - gamma * B_min


def floor_drain(
    r: float,
    M: float,
    sigma: float,
    gamma: float,
    B_min: float,
) -> float:
    """Floor-level drain d₀(r) = σM/r³ + γB_min."""
    return sigma * M / r**3 + gamma * B_min


def repair_capacity_density(
    rho: float,
    kappa: float,
    B_min: float,
    B_bar: float,
) -> float:
    """Repair-capacity density q = ρ / (κ(B̄ - B_min))."""
    if not 0.0 < B_min < B_bar:
        raise ValueError(f"need 0 < B_min < B_bar, got {B_min}, {B_bar}")
    return rho / (kappa * (B_bar - B_min))


def repair_viability_margin(
    Pi_0: float,
    d_0: float,
    q: float,
    gamma: float,
) -> float:
    """Slack in the repair-viability condition q·Π₀ > γ + 2√(qγd₀).

    Returns q·Π₀ - (γ + 2√(qγd₀)); the condition holds iff this is > 0.
    It is exactly equivalent to {positive linear coefficient} AND {positive
    discriminant} for the fixed-r parabola, i.e. to the existence of two
    positive roots.
    """
    return q * Pi_0 - (gamma + 2.0 * math.sqrt(q * gamma * d_0))


def is_repair_viable(Pi_0: float, d_0: float, q: float, gamma: float) -> bool:
    """True iff the repair-viability condition holds: q·Π₀ > γ + 2√(qγd₀)."""
    return repair_viability_margin(Pi_0, d_0, q, gamma) > 0.0


def boundary_equilibria(
    Pi_0: float,
    d_0: float,
    q: float,
    gamma: float,
    B_min: float,
) -> BoundaryEquilibria:
    """Roots of dB_i/dt = 0 at fixed r: B_u = B_min + x_-, B_i* = B_min + x_+.

        x_∓ = ((q·Π₀ - γ) ∓ √((q·Π₀ - γ)² - 4qγd₀)) / (2qγ)

    B_i* is locally asymptotically stable with Π(r) > 0 there; B_u is unstable
    (dB_i/dt < 0 on (B_min, B_u), > 0 on (B_u, min(B_i*, B̄))).  The parabola's
    slope at x_∓ is ∓√disc, which gives the two eigenvalues.

    That closed form is the DEFINITION, not the evaluation: x_- is computed via
    ``_parabola_roots``, since the ∓ form loses B_u to cancellation once
    q·Π₀ >> γ.

    If x_+ > B̄ - B_min the equilibrium saturates at the reference integrity B̄;
    the ``B_star`` returned here is the unsaturated root, so callers wanting the
    realised equilibrium should take min(B_star, B_bar).

    When the repair-viability condition fails there are no roots in
    (B_min, ∞); ``viable`` is False and the roots are NaN.
    """
    margin = repair_viability_margin(Pi_0, d_0, q, gamma)
    b = q * Pi_0 - gamma
    disc = b**2 - 4.0 * q * gamma * d_0
    if margin <= 0.0:
        return BoundaryEquilibria(
            viable=False,
            margin=margin,
            disc=disc,
            B_u=float('nan'),
            B_star=float('nan'),
            eig_u=float('nan'),
            eig_star=float('nan'),
        )
    sqrt_disc = math.sqrt(disc)
    x_minus, x_plus = _parabola_roots(q * gamma, b, d_0, sqrt_disc)
    return BoundaryEquilibria(
        viable=True,
        margin=margin,
        disc=disc,
        B_u=B_min + x_minus,
        B_star=B_min + x_plus,
        eig_u=+sqrt_disc,
        eig_star=-sqrt_disc,
    )


# ---------------------------------------------------------------------------
# The Basin of No Return (thm-basin-of-no-return)
# ---------------------------------------------------------------------------

def surplus_ceiling(
    M: float,
    G: float,
    tau: float,
    gamma: float,
    B_min: float,
) -> float:
    """Surplus ceiling Π̄ = G²M/(4τ) - γB_min.

    The largest net energy rate available at ANY coupling distance to an agent
    at the collapse floor.  Anchored at B_min — NOT at the agent's initial
    integrity.  (The old Pi_max = G²M/(4τ) - γB_i⁰ was anchored at initial
    integrity and has been removed; the re-anchoring is what makes the basin
    bound trajectory-independent.)
    """
    return G**2 * M / (4.0 * tau) - gamma * B_min


def basin_of_no_return(
    Pi_bar: float,
    q: float,
    gamma: float,
    B_min: float,
) -> float:
    """Critical integrity B_c below which collapse is unconditional.

        B_c = B_min + ((q·Π̄ - γ) - √((q·Π̄ - γ)² - 4qγ²B_min)) / (2qγ)

    — the DEFINITION, not the evaluation: the subtraction cancels away the
    basin thickness B_c - B_min once q·Π̄ >> γ, so the root itself comes from
    ``_parabola_roots``.  It is the smaller root of
    q(B_i - B_min)(G²M/(4τ) - γB_i) = γB_i.  Below B_c,
    dB_i/dt < 0 for all t REGARDLESS of the path r(t) — the bound already
    grants the agent the maximal surplus at every instant — and B_i reaches
    B_min in finite time.

    B_c is a certified INNER bound of the basin: below B_c collapse is
    unconditional; between B_c and B_u(r(t)) the outcome depends on the full
    trajectory.  If repair-viability holds at some r then B_min < B_c <= B_u(r).

    NOTE: B_c < B̄ requires the VIABLE-AGENT condition (repair-viability at r*
    AND B_u(r*) < B̄).  Bare repair-viability does not imply it — see the
    counterexample in the verification script.
    """
    b = q * Pi_bar - gamma
    disc = b**2 - 4.0 * q * gamma**2 * B_min
    if disc < 0.0:
        return float('nan')
    x_minus, _ = _parabola_roots(q * gamma, b, gamma * B_min, math.sqrt(disc))
    return B_min + x_minus


def basin_of_no_return_approx(
    Pi_bar: float,
    q: float,
    gamma: float,
    B_min: float,
) -> float:
    """Asymptotic B_c ≈ B_min·(1 + γ/(q·Π̄ - γ)), valid when q·Π̄ >> γ.

    For agents with a large surplus ceiling the basin is a thin layer above the
    collapse floor; it thickens as Π̄ falls toward γ/q = γκ(B̄ - B_min)/ρ.
    """
    return B_min * (1.0 + gamma / (q * Pi_bar - gamma))


def collapse_envelope(
    B_i: float,
    Pi_bar: float,
    q: float,
    gamma: float,
    B_min: float,
) -> float:
    """Envelope h(B_i) >= dB_i/dt, used for the finite-time collapse bound.

        h(B_i) = q(B_i - B_min)(G²M/(4τ) - γB_i) - γB_i
               = -qγx² + (q·Π̄ - γ)x - γB_min       for x = B_i - B_min

    Obtained by taking ζ <= 1, max(Π(r),0) <= max(G²M/(4τ) - γB_i, 0), and
    dropping the assimilation drain.  Valid wherever G²M/(4τ) - γB_i >= 0, in
    particular on (B_min, B_c].  h(B_min) = -γB_min < 0.

    From B_0 < B_c the agent reaches B_min no later than
    t_0 + (B_0 - B_min)/|h(B_0)|.
    """
    well = Pi_bar + gamma * B_min          # = G²M/(4τ)
    return q * (B_i - B_min) * (well - gamma * B_i) - gamma * B_i


def collapse_time_bound(
    B_0: float,
    Pi_bar: float,
    q: float,
    gamma: float,
    B_min: float,
) -> float:
    """Finite-time collapse bound (B_0 - B_min)/|h(B_0)| for B_0 < B_c."""
    h = collapse_envelope(B_0, Pi_bar, q, gamma, B_min)
    if h >= 0.0:
        return float('inf')
    return (B_0 - B_min) / abs(h)


# ---------------------------------------------------------------------------
# Irreversibility of Dissolution (thm-irreversibility-dissolution)
# ---------------------------------------------------------------------------

def dissolution_radius(
    M: float,
    gamma: float,
    sigma: float,
    rho: float,
    kappa: float,
    B_min: float,
    Pi_bar: float,
) -> float:
    """Dissolution threshold r_d = (κσM / (ρΠ̄ + κγB_min))^(1/3).

    Equivalently σM/r_d³ = (ρ/κ)Π̄ + γB_min.  Whenever r(t) < r_d, EVERY
    admissible integrity B_i ∈ (B_min, B̄] satisfies dB_i/dt < -γ(B_i + B_min)
    < 0; sustained coupling below r_d dissolves the agent in finite time
    t_d <= t_0 + (B_i(t_0) - B_min)/(2γB_min).

    NAMING: r_d is NOT r_- .  The energetic inner band edge r_- and this
    dissolution threshold are distinct quantities and either ordering can
    occur — when r_d > r_- the dissolution zone extends into the viable band
    (the assimilation trap: positive Π while the boundary degrades).  The MyST
    label `def-dissolution-threshold` still points at r_- for reference
    stability, which is why this function is not named after it.
    """
    return (kappa * sigma * M / (rho * Pi_bar + kappa * gamma * B_min)) ** (1.0 / 3.0)


def penetration_decline_rate(
    M: float,
    tau: float,
    gamma: float,
    sigma: float,
    rho: float,
    kappa: float,
    B_min: float,
    Pi_bar: float,
    mu_0: float,
) -> float:
    """Uniform decline rate α with dB_i/dr <= -α inside the dissolution zone.

        α = σκγB_min / (2μ₀τ(ρΠ̄ + κγB_min))  =  γB_min·r_d³ / (2μ₀τM)

    (the two forms are algebraically identical; the script asserts they agree).
    Integrating gives B_i(r) <= B_i⁰ - α(r - r_0).

    The bound is conservative on three counts: the envelope 2τ - Gr <= 2τ, the
    omission of the maintenance drain γB_i, and above all ζ(B_i) <= 1 in the
    escape velocity — along the true trajectory the decline per unit escape
    distance grows without bound as B_i → B_min, because mobility dies with the
    boundary while assimilation persists.
    """
    return sigma * kappa * gamma * B_min / (
        2.0 * mu_0 * tau * (rho * Pi_bar + kappa * gamma * B_min)
    )


def critical_penetration_depth(B_i_0: float, B_c: float, alpha: float) -> float:
    """Critical penetration depth ℓ_c = (B_i⁰ - B_c)/α.

    If the agent starts at r_0 with penetration depth ℓ = r_d - r_0 > ℓ_c, then
    B_i falls below B_c before r can reach r_d and collapse is irreversible
    regardless of the subsequent trajectory.  Sufficient, but far from
    necessary.
    """
    return (B_i_0 - B_c) / alpha


# ---------------------------------------------------------------------------
# The Starvation Spiral (thm-starvation-spiral)
# ---------------------------------------------------------------------------

def starvation_time(B_i_0: float, B_min: float, gamma: float) -> float:
    """Isolation-limit dissolution time t* = (1/γ)·ln(B_i⁰ / B_min).

    Outside the band Π < 0, so R_repair = 0 and dB_i/dt = -D_assimilate - γB_i.
    In the isolation limit (r >> r_+, assimilation negligible) the decline is
    exactly exponential: the exponential never reaches zero, but dissolution
    requires only reaching B_min > 0, which happens at the finite time t*.
    """
    return math.log(B_i_0 / B_min) / gamma


def basin_crossing_time(B_i_0: float, B_c: float, gamma: float) -> float:
    """Latest time t_c = (1/γ)·ln(B_i⁰ / B_c) at which a starving agent
    crosses the basin boundary B_c, if the deficit persists."""
    return math.log(B_i_0 / B_c) / gamma


def reentry_time_bound(r_0: float, R: float, M: float, G: float, mu_0: float) -> float:
    """Minimum time (r_0³ - R³)/(3μ₀MG) to drift inward from r_0 to R.

    Since 0 < V'(r) = M(Gr - 2τ)/r³ <= MG/r² and ζ <= 1, |r_dot| <= μ₀MG/r²,
    so d(r³)/dt >= -3μ₀MG and r(t)³ >= r_0³ - 3μ₀MG·t.
    """
    if R >= r_0:
        return 0.0
    return (r_0**3 - R**3) / (3.0 * mu_0 * M * G)


def irreversible_starvation(
    r_0: float,
    B_i_0: float,
    B_c: float,
    r_plus_at_Bc: float,
    M: float,
    G: float,
    gamma: float,
    mu_0: float,
) -> bool:
    """Sufficient condition for irreversible starvation (thm-starvation-spiral d):

        r_0³ >= r_+(B_c)³ + (3μ₀MG/γ)·ln(B_i⁰ / B_c)

    Re-entry must be measured against r_+(B_c) — the MOVING outer boundary at
    the basin integrity — not against r_+(B_i⁰).  As B_i falls the maintenance
    load drops and r_+ moves outward toward the agent, but while B_i > B_c the
    boundary stays inside r_+(B_c), so that is the target to beat.

    When it holds, repair capacity and mobility vanish together (ζ → 0), the
    inward drift stalls before re-entry, and B_i reaches B_min in finite time.
    Conversely a briefly starved agent above the basin can recover: starvation
    becomes fatal not when the band is exited but when depletion crosses B_c.
    """
    if B_i_0 <= B_c:
        return True
    return r_0**3 >= r_plus_at_Bc**3 + (3.0 * mu_0 * M * G / gamma) * math.log(B_i_0 / B_c)


# ---------------------------------------------------------------------------
# Multi-dimensional reduction (TC-XIII, def-multidimensional-boundary-dynamics)
# ---------------------------------------------------------------------------
#
# TC-XIII lifts the scalar active-dissipative boundary to a k-dimensional
# coupling vector r.  Per `01-model-setup.md`, the structural-capacity factor
# zeta(B_i) is the SAME scalar (it rescales every coupling channel uniformly),
# and the boundary thresholds "apply verbatim in the norm coordinate": the
# assimilation drain, dissolution radius r_d, surplus ceiling Pi_bar and basin
# threshold B_c are the scalar formulas evaluated at the weighted norm
#
#     r = ||r_vec||_Omega = sqrt(r_vec^T Omega r_vec),   Omega SPD.
#
# So NO new boundary math is introduced: feed omega_norm(...) to the scalar
# surplus_ceiling / dissolution_radius / basin_of_no_return / assimilation_rate
# / repair_capacity_density, all of which are already dimension-agnostic.  The
# only genuinely new object is Omega itself and the induced norm.  (Same
# standing caveat as the scalar model: TC-XIII gives NO numeric values for the
# boundary parameters; only structure is verifiable.)

def omega_norm(r_vec: "np.ndarray", Omega: "np.ndarray") -> float:
    """Weighted (Omega-)norm ||r||_Omega = sqrt(r^T Omega r) of a coupling vector.

    Omega must be symmetric positive definite (the scalar-reduction weight of
    TC-XIII def-vector-coupling-space; renamed from W in the v4 correction
    round).  This is the scalar coupling coordinate the multi-dim boundary
    thresholds are read at.  For k = 1 with Omega = [[1]] it reduces to |r|.
    """
    r_vec = np.asarray(r_vec, dtype=float)
    Omega = np.asarray(Omega, dtype=float)
    if Omega.shape != (r_vec.shape[0], r_vec.shape[0]):
        raise ValueError(f"Omega must be {r_vec.shape[0]}x{r_vec.shape[0]}, got {Omega.shape}")
    if not np.allclose(Omega, Omega.T):
        raise ValueError("Omega must be symmetric")
    quad = float(r_vec @ Omega @ r_vec)
    if quad < 0.0:
        raise ValueError("Omega must be positive definite (got r^T Omega r < 0)")
    return math.sqrt(quad)


def in_dissolution_region(r_vec: "np.ndarray", Omega: "np.ndarray", r_d: float) -> bool:
    """True iff r_vec lies in the Omega-ellipsoidal dissolution ball {||r||_Omega < r_d}.

    The multi-dim dissolution region of TC-XIII is the ellipsoid the weighted
    norm cuts out; membership is exactly the scalar test ||r||_Omega < r_d with
    r_d from ``dissolution_radius`` (evaluated at the same reduced coordinate).
    """
    return omega_norm(r_vec, Omega) < r_d


# ---------------------------------------------------------------------------
# Parameter bundle + integrator for the coupled system
# ---------------------------------------------------------------------------

@dataclass
class Trajectory:
    """Result of integrating the coupled agent-boundary system."""
    t: float                # final time (dissolution time if dissolved)
    r: float                # final coupling distance
    B_i: float              # final boundary integrity
    dissolved: bool         # True iff B_i reached the collapse floor B_min
    r_max: float            # largest coupling distance visited
    r_min: float            # smallest coupling distance visited


@dataclass
class ActiveBoundary:
    """Parameters of the coupled agent-boundary system.

    Bundles the ten parameters of the active dissipative model and delegates
    every formula to the module-level functions above (single source of truth).

    Parameters
    ----------
    M, G, tau, gamma : float
        HEC value mass, resource coupling, autonomy drive, entropy leakage.
    sigma : float
        Assimilation intensity (> 0).
    rho : float
        Repair allocation fraction, in (0, 1).
    kappa : float
        Repair multiplier, > 1.
    B_min : float
        Collapse floor, in (0, B_bar).  Absorbing.
    B_bar : float
        Reference integrity (repair saturates here).
    mu_0 : float
        Baseline mobility (> 0).
    """
    M: float
    G: float
    tau: float
    gamma: float
    sigma: float
    rho: float
    kappa: float
    B_min: float
    B_bar: float
    mu_0: float

    # -- algebraic quantities -------------------------------------------------

    @property
    def r_star(self) -> float:
        """Attractor r* = 2τ/G (independent of B_i)."""
        return optimal_coupling(self.tau, self.G)

    @property
    def q(self) -> float:
        """Repair-capacity density q = ρ/(κ(B̄ - B_min))."""
        return repair_capacity_density(self.rho, self.kappa, self.B_min, self.B_bar)

    @property
    def Pi_bar(self) -> float:
        """Surplus ceiling Π̄ = G²M/(4τ) - γB_min."""
        return surplus_ceiling(self.M, self.G, self.tau, self.gamma, self.B_min)

    @property
    def B_c(self) -> float:
        """Basin of no return B_c."""
        return basin_of_no_return(self.Pi_bar, self.q, self.gamma, self.B_min)

    @property
    def r_d(self) -> float:
        """Dissolution threshold r_d (NOT the energetic inner edge r_-)."""
        return dissolution_radius(
            self.M, self.gamma, self.sigma, self.rho, self.kappa,
            self.B_min, self.Pi_bar,
        )

    @property
    def alpha(self) -> float:
        """Uniform decline rate α inside the dissolution zone."""
        return penetration_decline_rate(
            self.M, self.tau, self.gamma, self.sigma, self.rho, self.kappa,
            self.B_min, self.Pi_bar, self.mu_0,
        )

    def zeta(self, B_i: float) -> float:
        """Structural capacity ζ(B_i)."""
        return structural_capacity(B_i, self.B_min, self.B_bar)

    def mu(self, B_i: float) -> float:
        """Health-dependent mobility μ(B_i) = μ₀ζ(B_i)."""
        return mobility(B_i, self.mu_0, self.B_min, self.B_bar)

    def Pi(self, r: float, B_i: float) -> float:
        """Net energy rate Π(r) at current integrity."""
        return net_energy_rate(r, self.M, self.G, self.tau, self.gamma, B_i)

    def Pi_0(self, r: float) -> float:
        """Floor-level net rate Π₀(r)."""
        return floor_net_rate(r, self.M, self.G, self.tau, self.gamma, self.B_min)

    def d_0(self, r: float) -> float:
        """Floor-level drain d₀(r)."""
        return floor_drain(r, self.M, self.sigma, self.gamma, self.B_min)

    def D_assimilate(self, r: float) -> float:
        """Assimilation degradation σM/r³."""
        return assimilation_rate(r, self.M, self.sigma)

    def R_repair(self, r: float, B_i: float) -> float:
        """Boundary regeneration (ρ/κ)ζ(B_i)max(Π(r), 0)."""
        return repair_rate(
            r, B_i, self.M, self.G, self.tau, self.gamma,
            self.rho, self.kappa, self.B_min, self.B_bar,
        )

    def r_dot(self, r: float, B_i: float) -> float:
        """Coupling velocity -μ₀ζ(B_i)V'(r)."""
        return coupling_velocity(
            r, B_i, self.M, self.G, self.tau, self.mu_0, self.B_min, self.B_bar,
        )

    def B_dot(self, r: float, B_i: float) -> float:
        """Boundary velocity R_repair - D_assimilate - γB_i."""
        return boundary_velocity(
            r, B_i, self.M, self.G, self.tau, self.gamma, self.sigma,
            self.rho, self.kappa, self.B_min, self.B_bar,
        )

    def equilibria(self, r: float) -> BoundaryEquilibria:
        """Fixed-r boundary equilibria at coupling distance r."""
        return boundary_equilibria(
            self.Pi_0(r), self.d_0(r), self.q, self.gamma, self.B_min,
        )

    def h(self, B_i: float) -> float:
        """Collapse envelope h(B_i) >= dB_i/dt."""
        return collapse_envelope(B_i, self.Pi_bar, self.q, self.gamma, self.B_min)

    def r_plus(self, B_i: float) -> float:
        """Outer band edge r_+(B_i) = (GM + √Δ)/(2γB_i) at integrity B_i."""
        return coexistence_band(self.G, self.M, self.gamma * B_i, self.tau).r_plus

    def is_viable_agent(self) -> bool:
        """Viable-agent condition: repair-viability at r* AND B_u(r*) < B̄.

        This — not bare repair-viability — is what guarantees B_c < B̄ and a
        healthy equilibrium strictly above the collapse floor.
        """
        eq = self.equilibria(self.r_star)
        return eq.viable and eq.B_u < self.B_bar

    # -- integration ----------------------------------------------------------

    def simulate(
        self,
        r_0: float,
        B_i_0: float,
        dt: float = 0.001,
        t_max: float = 1000.0,
    ) -> Trajectory:
        """Explicit-Euler integration of the coupled system.

        Enforces the two structural invariants of the model: {B_i <= B_min} is
        ABSORBING (integration stops there — the agent is dissolved, and B_i
        never approaches 0), and B_i is CLAMPED at the reference integrity B̄
        (repair cannot overshoot the intact boundary).
        """
        r_val, B_val, t = r_0, min(B_i_0, self.B_bar), 0.0
        r_lo = r_hi = r_val
        n_steps = int(t_max / dt)
        for _ in range(n_steps):
            dr = self.r_dot(r_val, B_val)
            dB = self.B_dot(r_val, B_val)
            r_val += dr * dt
            B_val = min(B_val + dB * dt, self.B_bar)   # saturate at B̄
            t += dt
            r_lo, r_hi = min(r_lo, r_val), max(r_hi, r_val)
            if B_val <= self.B_min:                    # absorbing: dissolved
                return Trajectory(t, r_val, self.B_min, True, r_hi, r_lo)
        return Trajectory(t, r_val, B_val, False, r_hi, r_lo)
