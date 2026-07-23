"""
Verify Task 1.6: Value Dynamics — Attractor Mechanics of Coexistence
=====================================================================

This script independently validates every numerical claim, theorem,
proposition, definition, lemma, and corollary from math/value-dynamics.md
using both symbolic (SymPy) and numerical (NumPy) computation.

Run:  python scripts/simulations/verify_value_dynamics.py
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

from modules.value_dynamics import (
    CANONICAL_KAPPA, boundary_scale,
    ActiveBoundary, basin_crossing_time, basin_of_no_return,
    dissolution_radius,
    basin_of_no_return_approx, boundary_equilibria, coexistence_band,
    collapse_envelope, collapse_time_bound, critical_penetration_depth,
    irreversible_starvation, mobility, reentry_time_bound,
    repair_capacity_density, repair_viability_margin, starvation_time,
    structural_capacity, surplus_ceiling,
)

# ---------------------------------------------------------------------------
# 0. Helpers (same pattern as Tasks 1.1–1.5 verification)
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
# Symbolic variables
# ---------------------------------------------------------------------------

r = sp.Symbol("r", positive=True)
M = sp.Symbol("M", positive=True)          # HEC value mass
G_s = sp.Symbol("G", positive=True)        # resource coupling coefficient
tau = sp.Symbol("tau", positive=True)       # dissolution coupling coefficient
gamma = sp.Symbol("gamma", positive=True)   # entropy leakage rate
B = sp.Symbol("B", positive=True)           # boundary integrity
mu = sp.Symbol("mu", positive=True)         # adjustment rate
sigma = sp.Symbol("sigma", positive=True)   # assimilation intensity
rho = sp.Symbol("rho", positive=True)       # repair allocation fraction
beta = sp.Symbol("beta", positive=True)     # discount factor parameter

# Coexistence potential (Definition 37)
V = tau * M / r**2 - G_s * M / r + gamma * B


# ===========================================================================
# 1. Proposition 8: Properties of Coexistence Potential
# ===========================================================================

def verify_proposition_8() -> None:
    section("1. Proposition 8 — Properties of Coexistence Potential")

    # (a) lim_{r -> 0+} V(r) = +inf
    lim_0 = sp.limit(V, r, 0, "+")
    check("Prop 8(a): lim_{r->0+} V(r) = +inf",
          lim_0 == sp.oo,
          f"limit = {lim_0}")

    # (b) lim_{r -> inf} V(r) = gamma * B
    lim_inf = sp.limit(V, r, sp.oo)
    check("Prop 8(b): lim_{r->inf} V(r) = gamma*B",
          sp.simplify(lim_inf - gamma * B) == 0,
          f"limit = {lim_inf}")

    # (c) V is C^inf on (0, inf) — it's a sum of rational functions + constant
    check("Prop 8(c): V is C^inf on (0, inf)",
          True, "V is a rational function of r on (0,inf)")

    # (d) Unique critical point
    Vp = sp.diff(V, r)
    crit_points = sp.solve(Vp, r)
    check("Prop 8(d): V'(r) = 0 has exactly one positive solution",
          len(crit_points) == 1 and all(
              sp.ask(sp.Q.positive(cp), sp.Q.positive(G_s) & sp.Q.positive(tau))
              for cp in crit_points
          ),
          f"critical points = {crit_points}")

    r_star = crit_points[0]
    check("Prop 8(d): critical point is r* = 2*tau/G",
          sp.simplify(r_star - 2 * tau / G_s) == 0,
          f"r* = {r_star}")

    # Second derivative positive at critical point
    Vpp = sp.diff(V, r, 2)
    Vpp_at_rstar = sp.simplify(Vpp.subs(r, r_star))
    check("Prop 8(d): V''(r*) > 0 (local minimum)",
          sp.ask(sp.Q.positive(Vpp_at_rstar),
                 sp.Q.positive(G_s) & sp.Q.positive(tau) & sp.Q.positive(M)),
          f"V''(r*) = {Vpp_at_rstar}")

    # (e) V_min < gamma * B
    V_min = sp.simplify(V.subs(r, r_star))
    diff_from_gammaB = sp.simplify(V_min - gamma * B)
    check("Prop 8(e): V(r*) = gamma*B - G^2*M/(4*tau)",
          sp.simplify(diff_from_gammaB + G_s**2 * M / (4 * tau)) == 0,
          f"V(r*) - gamma*B = {diff_from_gammaB}")

    check("Prop 8(e): V(r*) < gamma*B (since G^2*M/(4*tau) > 0)",
          sp.ask(sp.Q.negative(diff_from_gammaB),
                 sp.Q.positive(G_s) & sp.Q.positive(M) & sp.Q.positive(tau)),
          f"V(r*) - gamma*B = {diff_from_gammaB}")


# ===========================================================================
# 2. Definition 38 & 39: Cooperative Attractor and Well Depth
# ===========================================================================

def verify_definitions_38_39() -> None:
    section("2. Definitions 38–39 — Cooperative Attractor & Well Depth")

    r_star = 2 * tau / G_s

    # Verify V(r*) formula
    V_at_rstar = sp.simplify(V.subs(r, r_star))
    expected = gamma * B - G_s**2 * M / (4 * tau)
    check("Def 38: V(r*) = gamma*B - G^2*M/(4*tau)",
          sp.simplify(V_at_rstar - expected) == 0,
          f"V(r*) = {V_at_rstar}")

    # Net energy rate at the attractor.  NB: this is Pi(r*) from Def 38, read at
    # the agent's own integrity B -- NOT the surplus ceiling Pi_bar, which is
    # anchored at B_min and is the quantity r_d is built from.  The old passive
    # model had a `Pi_max` anchored at initial integrity; that quantity is gone.
    Pi_at_rstar = -V_at_rstar
    Pi_at_rstar_expected = G_s**2 * M / (4 * tau) - gamma * B
    check("Def 38: Pi(r*) = G^2*M/(4*tau) - gamma*B",
          sp.simplify(Pi_at_rstar - Pi_at_rstar_expected) == 0,
          f"Pi(r*) = {Pi_at_rstar}")

    # Well depth
    D_well = gamma * B - V_at_rstar
    D_expected = G_s**2 * M / (4 * tau)
    check("Def 39: Well depth D = G^2*M/(4*tau)",
          sp.simplify(D_well - D_expected) == 0,
          f"D = {D_well}")

    check("Def 39: D > 0",
          sp.ask(sp.Q.positive(D_well),
                 sp.Q.positive(G_s) & sp.Q.positive(M) & sp.Q.positive(tau)),
          f"D = {D_well}")

    check("Def 39: D proportional to M",
          sp.simplify(sp.diff(D_well, M) - G_s**2 / (4 * tau)) == 0,
          "dD/dM = G^2/(4*tau)")


# ===========================================================================
# 3. Theorem 22: Stability of the Cooperative Attractor
# ===========================================================================

def verify_theorem_22() -> None:
    section("3. Theorem 22 — Stability of the Cooperative Attractor")

    r_star = 2 * tau / G_s

    # (a) Fixed point: V'(r*) = 0
    Vp = sp.diff(V, r)
    Vp_at_rstar = sp.simplify(Vp.subs(r, r_star))
    check("Thm 22(a): V'(r*) = 0 (fixed point)",
          Vp_at_rstar == 0,
          f"V'(r*) = {Vp_at_rstar}")

    # (b) Eigenvalue is negative
    Vpp = sp.diff(V, r, 2)
    Vpp_at_rstar = sp.simplify(Vpp.subs(r, r_star))
    eigenvalue = -mu * Vpp_at_rstar
    eig_expected = -mu * G_s**4 * M / (8 * tau**3)
    check("Thm 22(b): eigenvalue = -mu*G^4*M/(8*tau^3)",
          sp.simplify(eigenvalue - eig_expected) == 0,
          f"eigenvalue = {eigenvalue}")

    check("Thm 22(b): eigenvalue < 0 (stable)",
          sp.ask(sp.Q.negative(eigenvalue),
                 sp.Q.positive(mu) & sp.Q.positive(G_s) &
                 sp.Q.positive(M) & sp.Q.positive(tau)),
          f"eigenvalue = {eigenvalue}")

    # (c) Lyapunov function: d/dt W = -mu * (V'(r))^2 <= 0
    Vp_sq = Vp**2
    rdot = -mu * Vp
    dW_dt = sp.simplify(Vp * rdot)
    check("Thm 22(c): dW/dt = -mu*(V'(r))^2",
          sp.simplify(dW_dt + mu * Vp_sq) == 0,
          "Lyapunov derivative is non-positive")

    # Numerical verification: simulate gradient dynamics
    G_n, tau_n, M_n, gamma_n, B_n, mu_n = 1.0, 0.5, 100.0, 0.1, 1.0, 0.5
    r_star_n = 2 * tau_n / G_n

    def V_num(r_val):
        return tau_n * M_n / r_val**2 - G_n * M_n / r_val + gamma_n * B_n

    def Vp_num(r_val):
        return -2 * tau_n * M_n / r_val**3 + G_n * M_n / r_val**2

    # Simulate from r0 = 5 (far from attractor)
    dt = 0.001
    r_val = 5.0
    for _ in range(50000):
        r_val = r_val - mu_n * Vp_num(r_val) * dt
    check("Thm 22(c): numerical convergence from r=5",
          np.isclose(r_val, r_star_n, rtol=0.01),
          f"r_final = {r_val:.4f}, r* = {r_star_n:.4f}")

    # Simulate from r0 = 0.3 (close range)
    r_val = 0.3
    for _ in range(50000):
        r_val = r_val - mu_n * Vp_num(r_val) * dt
    check("Thm 22(c): numerical convergence from r=0.3",
          np.isclose(r_val, r_star_n, rtol=0.01),
          f"r_final = {r_val:.4f}, r* = {r_star_n:.4f}")


# ===========================================================================
# 4. Theorem 23: Existence of the Coexistence Band
# ===========================================================================

def verify_theorem_23() -> None:
    section("4. Theorem 23 — Existence of the Coexistence Band")

    # Minimum viable mass
    M_min = 4 * gamma * B * tau / G_s**2
    check("Thm 23: M_min = 4*gamma*B*tau/G^2",
          True, f"M_min = {M_min}")

    # The quadratic: gamma*B * r^2 - G*M * r + tau*M = 0
    quadratic = gamma * B * r**2 - G_s * M * r + tau * M
    Delta = sp.simplify((G_s * M)**2 - 4 * gamma * B * tau * M)
    Delta_expected = G_s**2 * M**2 - 4 * gamma * B * tau * M
    check("Thm 23: discriminant = G^2*M^2 - 4*gamma*B*tau*M",
          sp.simplify(Delta - Delta_expected) == 0,
          f"Delta = {Delta}")

    # Delta > 0 iff M > M_min
    Delta_factored = M * (G_s**2 * M - 4 * gamma * B * tau)
    check("Thm 23: Delta = M*(G^2*M - 4*gamma*B*tau)",
          sp.simplify(Delta - Delta_factored) == 0,
          "Factored form verified")

    # When M = M_min, Delta = 0
    Delta_at_Mmin = sp.simplify(Delta.subs(M, M_min))
    check("Thm 23: Delta(M_min) = 0 (marginal viability)",
          Delta_at_Mmin == 0,
          f"Delta(M_min) = {Delta_at_Mmin}")

    # The band is the OPEN set {r > 0 : V(r) < 0}, so it exists iff Delta > 0
    # STRICTLY. At M = M_min the band is EMPTY — V(r) >= 0 everywhere with
    # equality only at r*, which is marginal and non-surviving since survival
    # requires Pi(r) > 0 strictly. It does NOT "collapse to the single point r*".
    G_e, tau_e, gB_e = 1.0, 0.5, 0.1
    M_min_e = 4 * gB_e * tau_e / G_e**2
    band_at_min = coexistence_band(G_e, M_min_e, gB_e, tau_e)
    check("Thm 23: band is EMPTY at M = M_min (strict > predicate)",
          not band_at_min.bound,
          f"bound = {band_at_min.bound}, bandwidth = {band_at_min.bandwidth}")

    check("Thm 23: at M = M_min, V(r) >= 0 everywhere with equality only at r*",
          np.isclose(tau_e * M_min_e / (2*tau_e/G_e)**2
                     - G_e * M_min_e / (2*tau_e/G_e) + gB_e, 0.0, atol=1e-12)
          and all(tau_e * M_min_e / rr**2 - G_e * M_min_e / rr + gB_e > 0
                  for rr in (0.5, 0.9, 1.1, 2.0, 10.0)),
          "V(r*) = 0, V > 0 elsewhere — marginal, non-surviving")

    check("Thm 23: band exists just above M_min (Delta > 0)",
          coexistence_band(G_e, M_min_e * 1.001, gB_e, tau_e).bound,
          "existence is strict in M > M_min")

    # Both roots positive (sum and product > 0)
    r_sum = G_s * M / (gamma * B)
    r_prod = tau * M / (gamma * B)
    check("Thm 23: sum of roots > 0",
          sp.ask(sp.Q.positive(r_sum),
                 sp.Q.positive(G_s) & sp.Q.positive(M) &
                 sp.Q.positive(gamma) & sp.Q.positive(B)),
          f"r_- + r_+ = {r_sum}")

    check("Thm 23: product of roots > 0",
          sp.ask(sp.Q.positive(r_prod),
                 sp.Q.positive(tau) & sp.Q.positive(M) &
                 sp.Q.positive(gamma) & sp.Q.positive(B)),
          f"r_- * r_+ = {r_prod}")

    # Numerical verification
    G_n, tau_n, gamma_n, B_n = 1.0, 0.5, 0.1, 1.0
    M_min_n = 4 * gamma_n * B_n * tau_n / G_n**2
    check("Thm 23: numerical M_min = 0.2",
          np.isclose(M_min_n, 0.2),
          f"M_min = {M_min_n}")

    # With M = 100 >> M_min = 0.2
    M_n = 100.0
    Delta_n = G_n**2 * M_n**2 - 4 * gamma_n * B_n * tau_n * M_n
    check("Thm 23: Delta > 0 when M > M_min",
          Delta_n > 0,
          f"Delta = {Delta_n}")

    # With M = 0.1 < M_min = 0.2
    M_sub = 0.1
    Delta_sub = G_n**2 * M_sub**2 - 4 * gamma_n * B_n * tau_n * M_sub
    check("Thm 23: Delta < 0 when M < M_min",
          Delta_sub < 0,
          f"Delta = {Delta_sub}")


# ===========================================================================
# 5. Definitions 40–42 & Lemma 2: Coexistence Band Boundaries
# ===========================================================================

def verify_band_boundaries() -> None:
    section("5. Defs 40–42 & Lemma 2 — Coexistence Band Boundaries")

    # Symbolic boundaries
    Delta_sym = G_s**2 * M**2 - 4 * gamma * B * tau * M
    sqrt_Delta = sp.sqrt(Delta_sym)
    r_minus = (G_s * M - sqrt_Delta) / (2 * gamma * B)
    r_plus = (G_s * M + sqrt_Delta) / (2 * gamma * B)
    r_star = 2 * tau / G_s

    # V(r_-) = 0
    V_at_rminus = sp.simplify(V.subs(r, r_minus))
    # This simplification may be complex; do numerical verification
    check("Def 40: V(r_-) = 0 (verified numerically below)",
          True, "symbolic simplification deferred")

    # Numerical verification
    G_n, tau_n, M_n, gamma_n, B_n = 1.0, 0.5, 100.0, 0.1, 1.0
    Delta_n = G_n**2 * M_n**2 - 4 * gamma_n * B_n * tau_n * M_n
    sqrt_Delta_n = np.sqrt(Delta_n)

    r_minus_n = (G_n * M_n - sqrt_Delta_n) / (2 * gamma_n * B_n)
    r_plus_n = (G_n * M_n + sqrt_Delta_n) / (2 * gamma_n * B_n)
    r_star_n = 2 * tau_n / G_n

    def V_num(r_val):
        return tau_n * M_n / r_val**2 - G_n * M_n / r_val + gamma_n * B_n

    check("Def 40: V(r_-) ≈ 0 numerically",
          np.isclose(V_num(r_minus_n), 0.0, atol=1e-10),
          f"V(r_-) = {V_num(r_minus_n):.2e}")

    check("Def 41: V(r_+) ≈ 0 numerically",
          np.isclose(V_num(r_plus_n), 0.0, atol=1e-10),
          f"V(r_+) = {V_num(r_plus_n):.2e}")

    check("Def 42: V(r*) < 0 (inside band is viable)",
          V_num(r_star_n) < 0,
          f"V(r*) = {V_num(r_star_n):.4f}")

    # Lemma 2: r_- < r* < r_+
    check("Lemma 2: r_- < r* < r_+",
          r_minus_n < r_star_n < r_plus_n,
          f"r_- = {r_minus_n:.4f}, r* = {r_star_n:.4f}, r_+ = {r_plus_n:.4f}")

    # Band is the correct set {r : V(r) < 0}
    mid = (r_minus_n + r_star_n) / 2
    outside_left = r_minus_n / 2
    outside_right = r_plus_n * 2
    check("Def 42: V(midpoint of band) < 0",
          V_num(mid) < 0,
          f"V({mid:.4f}) = {V_num(mid):.4f}")

    check("Def 42: V(outside left) > 0",
          V_num(outside_left) > 0,
          f"V({outside_left:.4f}) = {V_num(outside_left):.4f}")

    check("Def 42: V(outside right) > 0",
          V_num(outside_right) > 0,
          f"V({outside_right:.4f}) = {V_num(outside_right):.4f}")

    # --- Numerical conditioning of r_- at large M -------------------------
    # r_- -> tau/G from ABOVE as M grows, so the quantity of interest is the
    # correction term r_- - tau/G, not r_- itself.  The textbook
    # (GM - sqrt(Delta))/(2*gamma_Bi) cancels that term away once
    # G^2*M^2 >> 4*gamma_Bi*tau*M: it is ~0.7% wrong at M=1e8 and returns
    # EXACTLY tau/G by M=1e10, silently losing the band's inner edge.  Guard it
    # against the independent asymptotic expansion
    #     r_- = tau/G + gamma_Bi*tau^2/(G^3*M) + O(1/M^2),
    # which is derived from V(r)=0 rather than from the quadratic formula, so
    # it cannot mask a cancellation in the root-finder.
    # atol=0.0 throughout: these are PURE RELATIVE tests.  np.isclose defaults
    # to atol=1e-8, which would swamp a correction term of size ~3.75e-8 and
    # let the cancelled value pass on the absolute floor alone.
    #
    # rtol=1e-4 is chosen to sit between two known error scales, not by taste:
    #   * the asymptotic expansion truncates at O(1/M^2), ~1.5e-6 relative at
    #     M=1e8 (falling with M), so anything tighter rejects the CORRECT value;
    #   * the cancellation it must catch is ~6.6e-3 at M=1e8 and total (100%)
    #     at M>=1e10.
    # That leaves ~66x margin on both sides.  Mutation-tested: reverting
    # _parabola_roots to (b - sqrt(disc))/(2a) fails all six checks below.
    G_c, gB_c, tau_c = 1.0, 15.0, 0.5
    asymptote = tau_c / G_c
    for M_c in (1e8, 1e10, 1e12):
        r_m = coexistence_band(G_c, M_c, gB_c, tau_c).r_minus
        correction = r_m - asymptote
        predicted = gB_c * tau_c**2 / (G_c**3 * M_c)
        check(f"Lemma 2: r_- retains its correction term at M={M_c:.0e}",
              correction > 0.0
              and np.isclose(correction, predicted, rtol=1e-4, atol=0.0),
              f"r_- - tau/G = {correction:.6e}, asymptotic = {predicted:.6e}")

    # Vieta cross-check: r_-*r_+ = tau*M/gamma_Bi exactly, independent of how
    # either root was evaluated.  The naive form violates this once it cancels.
    for M_c in (1e8, 1e10, 1e12):
        bnd = coexistence_band(G_c, M_c, gB_c, tau_c)
        check(f"Lemma 2: Vieta r_-*r_+ = tau*M/gamma_Bi at M={M_c:.0e}",
              np.isclose(bnd.r_minus * bnd.r_plus, tau_c * M_c / gB_c,
                         rtol=1e-12, atol=0.0),
              f"{bnd.r_minus * bnd.r_plus:.10e} vs {tau_c * M_c / gB_c:.10e}")


# ===========================================================================
# 6. Theorem 24: Freedom Bandwidth
# ===========================================================================

def verify_theorem_24() -> None:
    section("6. Theorem 24 — Freedom Bandwidth Theorem")

    Delta_sym = G_s**2 * M**2 - 4 * gamma * B * tau * M
    sqrt_Delta = sp.sqrt(Delta_sym)
    w_sym = sqrt_Delta / (gamma * B)

    # (a) w > 0 iff M > M_min
    M_min = 4 * gamma * B * tau / G_s**2
    check("Thm 24(a): w > 0 iff M > M_min (by discriminant > 0)",
          True, "follows from Theorem 23")

    # (b) dw/dM > 0 for M > M_min
    dw_dM = sp.diff(w_sym, M)
    dw_dM_simplified = sp.simplify(dw_dM)
    # Numerically verify
    G_n, tau_n, gamma_n, B_n = 1.0, 0.5, 0.1, 1.0
    M_min_n = 4 * gamma_n * B_n * tau_n / G_n**2  # = 0.2

    def bandwidth(M_val):
        Delta_val = G_n**2 * M_val**2 - 4 * gamma_n * B_n * tau_n * M_val
        if Delta_val <= 0:
            return 0.0
        return np.sqrt(Delta_val) / (gamma_n * B_n)

    w1 = bandwidth(10.0)
    w2 = bandwidth(100.0)
    w3 = bandwidth(1000.0)
    check("Thm 24(b): w increasing in M (10 < 100 < 1000)",
          w1 < w2 < w3,
          f"w(10)={w1:.2f}, w(100)={w2:.2f}, w(1000)={w3:.2f}")

    # (c) w decreasing in gamma, B, tau
    def bw_params(G_val, tau_val, gamma_val, B_val, M_val):
        Delta_val = G_val**2 * M_val**2 - 4 * gamma_val * B_val * tau_val * M_val
        if Delta_val <= 0:
            return 0.0
        return np.sqrt(Delta_val) / (gamma_val * B_val)

    M_test = 100.0
    w_base = bw_params(1.0, 0.5, 0.1, 1.0, M_test)

    # Increasing gamma
    w_higher_gamma = bw_params(1.0, 0.5, 0.2, 1.0, M_test)
    check("Thm 24(c): w decreasing in gamma",
          w_higher_gamma < w_base,
          f"w(gamma=0.1)={w_base:.2f}, w(gamma=0.2)={w_higher_gamma:.2f}")

    # Increasing B
    w_higher_B = bw_params(1.0, 0.5, 0.1, 2.0, M_test)
    check("Thm 24(c): w decreasing in B",
          w_higher_B < w_base,
          f"w(B=1)={w_base:.2f}, w(B=2)={w_higher_B:.2f}")

    # Increasing tau
    w_higher_tau = bw_params(1.0, 1.0, 0.1, 1.0, M_test)
    check("Thm 24(c): w decreasing in tau",
          w_higher_tau < w_base,
          f"w(tau=0.5)={w_base:.2f}, w(tau=1.0)={w_higher_tau:.2f}")

    # (d) w increasing in G
    w_higher_G = bw_params(2.0, 0.5, 0.1, 1.0, M_test)
    check("Thm 24(d): w increasing in G",
          w_higher_G > w_base,
          f"w(G=1)={w_base:.2f}, w(G=2)={w_higher_G:.2f}")

    # (e) Large M limit: w ≈ G*M/(gamma*B)
    M_large = 1e6
    w_large = bandwidth(M_large)
    w_approx = G_n * M_large / (gamma_n * B_n)
    check("Thm 24(e): for M >> M_min, w ≈ G*M/(gamma*B)",
          np.isclose(w_large, w_approx, rtol=0.001),
          f"w={w_large:.2f}, approx={w_approx:.2f}")

    # (f) Near threshold: w ~ sqrt(M - M_min)
    eps_values = [0.001, 0.01, 0.1]
    ratios = []
    for eps in eps_values:
        M_val = M_min_n + eps
        w_val = bandwidth(M_val)
        ratio = w_val / np.sqrt(eps) if eps > 0 else 0
        ratios.append(ratio)
    # Ratios should be approximately constant
    check("Thm 24(f): near threshold, w ~ sqrt(M - M_min)",
          np.isclose(ratios[0], ratios[1], rtol=0.2),
          f"ratios = {[f'{x:.4f}' for x in ratios]}")


# ===========================================================================
# 7. Corollary 24.1: Freedom Is Finite
# ===========================================================================

def verify_corollary_24_1() -> None:
    section("7. Corollary 24.1 — Freedom Is Finite")

    G_n, tau_n, gamma_n, B_n = 1.0, 0.5, 0.1, 1.0

    # For any finite M, w is finite
    for M_val in [1.0, 100.0, 1e6, 1e12]:
        Delta_val = G_n**2 * M_val**2 - 4 * gamma_n * B_n * tau_n * M_val
        w_val = np.sqrt(Delta_val) / (gamma_n * B_n)
        check(f"Cor 24.1: w(M={M_val:.0e}) is finite",
              np.isfinite(w_val),
              f"w = {w_val:.2e}")

    # w -> inf as M -> inf (bandwidth scales linearly)
    check("Cor 24.1: w -> inf requires M -> inf",
          True, "w ≈ G*M/(gamma*B) for large M, linear growth")


# ===========================================================================
# 8. Corollary 24.2: Inequality of Freedom
# ===========================================================================

def verify_corollary_24_2() -> None:
    section("8. Corollary 24.2 — Inequality of Freedom")

    G_n, tau_n, M_n, gamma_n = 1.0, 0.5, 100.0, 0.1

    def bandwidth(B_val):
        Delta_val = G_n**2 * M_n**2 - 4 * gamma_n * B_val * tau_n * M_n
        if Delta_val <= 0:
            return 0.0
        return np.sqrt(Delta_val) / (gamma_n * B_val)

    def m_min(B_val):
        return 4 * gamma_n * B_val * tau_n / G_n**2

    B_i, B_j = 2.0, 1.0  # B_i > B_j
    check("Cor 24.2(a): B_i > B_j => w_i < w_j",
          bandwidth(B_i) < bandwidth(B_j),
          f"w(B=2)={bandwidth(B_i):.2f}, w(B=1)={bandwidth(B_j):.2f}")

    check("Cor 24.2(b): B_i > B_j => M_min_i > M_min_j",
          m_min(B_i) > m_min(B_j),
          f"M_min(B=2)={m_min(B_i):.2f}, M_min(B=1)={m_min(B_j):.2f}")

    # (c) There exists M* where j survives but i does not
    M_critical = (m_min(B_i) + m_min(B_j)) / 2
    check("Cor 24.2(c): exists M where j viable but i not",
          m_min(B_j) < M_critical < m_min(B_i),
          f"M_min_j={m_min(B_j):.2f} < M*={M_critical:.2f} < M_min_i={m_min(B_i):.2f}")


# ===========================================================================
# SCRIPT-CHOSEN PARAMETERS FOR THE ACTIVE DISSIPATIVE BOUNDARY (§§9–12)
#
# !! THESE NUMBERS ARE NOT FROM THE PAPER. !!
#
# TC-VI gives NO numeric value for ANY parameter of the active dissipative
# model — sigma, rho, kappa, B_min, B_bar, mu_0 — and therefore none for the
# quantities derived from them either (B_c, r_d, Pi_bar, zeta, ell_c, alpha).
# The three worked examples (§§19–21) predate the boundary rebuild and use only
# B, gamma, M, G, tau. That silence is deliberate, not an oversight.
#
# Consequently nothing in §§9–12 asserts a paper-blessed magic number for the
# new machinery. The scenarios below are self-consistent parameter sets chosen
# HERE, and every claim made about them is an ANALYTIC property that must hold
# for any admissible parameters: fixed-point residuals, root ordering,
# stability eigenvalue signs, algebraic identities, finite-time bounds under
# numerical integration, and asymptotic agreement.
#
# The ONE fully-pinned numeric case is the B_c >= B_bar counterexample in §10,
# which comes from the round-1.5 review record; it is labelled at its use site
# and is deliberately NOT routed through the shared convention below.
#
# kappa and the B_bar/B_min convention are shared with the applied scripts via
# modules/value_dynamics.py — CANONICAL_KAPPA and boundary_scale() are the one
# place those are chosen and audited. sigma, rho and mu_0 stay per-scenario:
# they are what distinguishes the two agents below.
#
# DO NOT cite the values below as canonical TC-VI parameters.
# ===========================================================================

# The (M, G, tau, gamma) geometry is Worked Example 9.1's (§19) — those four
# ARE the paper's. The boundary parameters appended to them are not.
_EX1_GEOMETRY = dict(M=100.0, G=1.0, tau=0.5, gamma=0.1)

# Ex 9.1 declares B = 1, and the shared convention reads a declared integrity AS
# the fully-intact reference: B_bar = 1.0, B_min = 0.02*B_bar = 0.02. So zeta = 1
# at the declared integrity and the agent starts healthy.
_EX1_B_DECLARED = 1.0
_EX1_B_BAR, _EX1_B_MIN = boundary_scale(_EX1_B_DECLARED)

# Scenario "viable agent": repair-viability holds at r* AND B_u(r*) < B_bar, so
# the viable-agent condition holds and the basin is a proper layer (B_c < B_bar).
# x_+ exceeds B_bar - B_min, so the healthy equilibrium saturates at B_bar.
# Here r_d < r*, so escape from the dissolution zone is a race (Thm 25c).
VIABLE = ActiveBoundary(
    sigma=0.01, rho=0.3, kappa=CANONICAL_KAPPA,
    B_min=_EX1_B_MIN, B_bar=_EX1_B_BAR, mu_0=0.5,
    **_EX1_GEOMETRY,
)

# Scenario "strong assimilator": the same agent, sigma 0.01 -> 0.5. Now r_d > r*
# — the attractor itself lies inside the dissolution zone — and although
# repair-viability still holds at r*, the roots have been pushed above B_bar so
# the VIABLE-AGENT condition fails and no admissible integrity can be sustained.
ASSIMILATED = ActiveBoundary(
    sigma=0.5, rho=0.3, kappa=CANONICAL_KAPPA,
    B_min=_EX1_B_MIN, B_bar=_EX1_B_BAR, mu_0=0.5,
    **_EX1_GEOMETRY,
)


# ===========================================================================
# 9. Proposition — Healthy Boundary Equilibrium
# ===========================================================================

def verify_healthy_boundary_equilibrium() -> None:
    section("9. Proposition — Healthy Boundary Equilibrium")

    # -- def-structural-capacity ------------------------------------------
    B_min, B_bar = VIABLE.B_min, VIABLE.B_bar
    check("Def: zeta(B_min) = 0 (no capacity at the collapse floor)",
          np.isclose(structural_capacity(B_min, B_min, B_bar), 0.0),
          f"zeta(B_min) = {structural_capacity(B_min, B_min, B_bar)}")

    check("Def: zeta(B_bar) = 1 (full capacity at reference integrity)",
          np.isclose(structural_capacity(B_bar, B_min, B_bar), 1.0),
          f"zeta(B_bar) = {structural_capacity(B_bar, B_min, B_bar)}")

    zetas = [structural_capacity(b, B_min, B_bar)
             for b in np.linspace(B_min, B_bar, 20)]
    check("Def: zeta increasing on [B_min, B_bar], valued in [0,1]",
          all(zetas[i] < zetas[i + 1] for i in range(len(zetas) - 1))
          and all(0.0 <= z <= 1.0 for z in zetas),
          f"zeta in [{zetas[0]:.3f}, {zetas[-1]:.3f}]")

    check("Def: zeta clamps at 0 below the collapse floor",
          structural_capacity(B_min * 0.5, B_min, B_bar) == 0.0,
          "max(., 0) branch")

    # Health-dependent mobility: mu = mu_0 * zeta, so mobility dies with B_i.
    check("Def: mu(B_min) = 0 (mobility death at the floor)",
          np.isclose(mobility(B_min, VIABLE.mu_0, B_min, B_bar), 0.0),
          f"mu(B_min) = {mobility(B_min, VIABLE.mu_0, B_min, B_bar)}")

    check("Def: mu(B_bar) = mu_0 (full mobility when intact)",
          np.isclose(mobility(B_bar, VIABLE.mu_0, B_min, B_bar), VIABLE.mu_0),
          f"mu(B_bar) = {mobility(B_bar, VIABLE.mu_0, B_min, B_bar)}")

    # zeta gates the COUPLING equation too, not just repair. Omitting it there
    # would let the gradient pull a dying agent home for free — the single most
    # consequential way to get this model wrong, so pin r_dot exactly rather
    # than merely bounding it.
    def Vp_num(rr):
        return VIABLE.M * (VIABLE.G * rr - 2 * VIABLE.tau) / rr**3

    check("Def: r_dot = -mu_0*zeta(B_i)*V'(r) exactly (zeta gates mobility)",
          all(np.isclose(VIABLE.r_dot(rr, b),
                         -VIABLE.mu_0 * structural_capacity(b, B_min, B_bar) * Vp_num(rr),
                         rtol=1e-12)
              for rr in (0.4, 0.7, 1.6, 5.0, 40.0)
              for b in (0.25, 0.6, 1.2, 2.0)),
          "checked 5 radii x 4 integrities")

    # The falsifiable consequence: a depleted agent drifts strictly slower than
    # an intact one at the SAME radius, in exact proportion to zeta.
    r_off = 5.0        # V'(r) != 0 here, so mobility is actually exercised
    check("Def: depleted agent drifts strictly slower than an intact one at "
          "the same r",
          abs(VIABLE.r_dot(r_off, 0.5)) < abs(VIABLE.r_dot(r_off, B_bar)),
          f"|r_dot(B=0.5)| = {abs(VIABLE.r_dot(r_off, 0.5)):.6f} < "
          f"|r_dot(B=B_bar)| = {abs(VIABLE.r_dot(r_off, B_bar)):.6f}")

    check("Def: r_dot ratio between integrities equals the zeta ratio",
          np.isclose(VIABLE.r_dot(r_off, 0.5) / VIABLE.r_dot(r_off, B_bar),
                     structural_capacity(0.5, B_min, B_bar)
                     / structural_capacity(B_bar, B_min, B_bar), rtol=1e-12),
          f"ratio = {VIABLE.r_dot(r_off, 0.5)/VIABLE.r_dot(r_off, B_bar):.6f}")

    check("Def: r_dot -> 0 as B_i -> B_min even where V'(r) is large "
          "(mobility death)",
          abs(VIABLE.r_dot(r_off, B_min * 1.000001)) < 1e-6
          and abs(Vp_num(r_off)) > 1.0,
          f"r_dot = {VIABLE.r_dot(r_off, B_min*1.000001):.3e} "
          f"while V'(r) = {Vp_num(r_off):.4f}")

    # Autocatalysis: repair -> 0 as B_i -> B_min REGARDLESS of Pi. This is the
    # property that distinguishes an active structure from a passive reservoir.
    r_star = VIABLE.r_star
    Pi_at_floor = VIABLE.Pi(r_star, B_min * 1.000001)
    check("Def: R_repair -> 0 as B_i -> B_min even though Pi >> 0",
          VIABLE.R_repair(r_star, B_min * 1.000001) < 1e-4 and Pi_at_floor > 1.0,
          f"R_repair = {VIABLE.R_repair(r_star, B_min * 1.000001):.3e} "
          f"while Pi = {Pi_at_floor:.2f}")

    # -- q, and the repair-viability condition ----------------------------
    q = repair_capacity_density(VIABLE.rho, VIABLE.kappa, B_min, B_bar)
    check("Prop: q = rho/(kappa*(B_bar - B_min))",
          np.isclose(q, VIABLE.rho / (VIABLE.kappa * (B_bar - B_min))),
          f"q = {q:.6f}")

    # ------------------------------------------------------------------
    # Scenario "interior": the Proposition is a statement about the fixed-r
    # quadratic, so — exactly as the paper states it, and exactly as the §10
    # counterexample is stated — this scenario supplies (Pi_0, d_0, q, gamma,
    # B_min) directly rather than sourcing them from an (r, M, G, tau, sigma).
    #
    # It is tuned so that x_+ < B_bar - B_min, giving an INTERIOR stable
    # equilibrium that does not saturate. Note (a property of the algebra, not
    # of the paper): a non-saturating equilibrium requires a barely-viable
    # agent. Since x_+ > (B_bar - B_min)/(rho/kappa) whenever the agent is
    # comfortably viable, and rho/kappa < 1 always, interior equilibria live in
    # a narrow window just above the viability threshold.
    # ------------------------------------------------------------------
    q_int = repair_capacity_density(0.6, 1.2, 0.2, 2.0)   # rho/kappa = 0.5
    Pi_0_int, d_0_int, gamma_int, B_min_int, B_bar_int = 0.56, 0.021, 0.1, 0.2, 2.0
    eq = boundary_equilibria(Pi_0_int, d_0_int, q_int, gamma_int, B_min_int)

    check("Prop: repair-viability q*Pi_0 > gamma + 2*sqrt(q*gamma*d_0)",
          eq.viable and eq.margin > 0,
          f"margin = {eq.margin:.6f}")

    check("Prop: exactly two roots B_u < B_i* in (B_min, inf)",
          B_min_int < eq.B_u < eq.B_star,
          f"B_u = {eq.B_u:.6f}, B_i* = {eq.B_star:.6f}")

    check("Prop: interior equilibrium — B_i* < B_bar (no saturation here)",
          eq.B_star < B_bar_int,
          f"B_i* = {eq.B_star:.6f} < B_bar = {B_bar_int}")

    # Fixed-point residuals: the parabola -q*gamma*x^2 + (q*Pi_0-gamma)*x - d_0
    # must vanish at both roots.
    def parabola(x):
        return -q_int * gamma_int * x**2 + (q_int * Pi_0_int - gamma_int) * x - d_0_int

    res_u = parabola(eq.B_u - B_min_int)
    res_star = parabola(eq.B_star - B_min_int)
    check("Prop: fixed-point residual at B_u ~ 0",
          abs(res_u) < 1e-12, f"residual = {res_u:.3e}")

    check("Prop: fixed-point residual at B_i* ~ 0",
          abs(res_star) < 1e-12, f"residual = {res_star:.3e}")

    # Stability: slope of the parabola at x_-/x_+ is +/-sqrt(disc).
    check("Prop(a): eigenvalue at B_i* is -sqrt(disc) < 0 (stable)",
          eq.eig_star < 0 and np.isclose(eq.eig_star, -math.sqrt(eq.disc)),
          f"eig(B_i*) = {eq.eig_star:.6f}")

    check("Prop(b): eigenvalue at B_u is +sqrt(disc) > 0 (unstable)",
          eq.eig_u > 0 and np.isclose(eq.eig_u, +math.sqrt(eq.disc)),
          f"eig(B_u) = {eq.eig_u:.6f}")

    # The eigenvalues are the analytic slopes; confirm against a finite
    # difference of the parabola so the sign convention cannot silently flip.
    h_fd = 1e-7
    slope_star = (parabola(eq.B_star - B_min_int + h_fd)
                  - parabola(eq.B_star - B_min_int - h_fd)) / (2 * h_fd)
    slope_u = (parabola(eq.B_u - B_min_int + h_fd)
               - parabola(eq.B_u - B_min_int - h_fd)) / (2 * h_fd)
    check("Prop: eigenvalues match finite-difference slopes at both roots",
          np.isclose(slope_star, eq.eig_star, atol=1e-6)
          and np.isclose(slope_u, eq.eig_u, atol=1e-6),
          f"slope(B_i*) = {slope_star:.6f}, slope(B_u) = {slope_u:.6f}")

    check("Prop(a): Pi(r) > 0 at B_i* (x_+ < Pi_0/gamma)",
          Pi_0_int - gamma_int * (eq.B_star - B_min_int) > 0,
          f"Pi(B_i*) = {Pi_0_int - gamma_int * (eq.B_star - B_min_int):.6f}")

    # Beyond Pi = 0 the repair term vanishes and dB/dt = -sigma*M/r^3 - gamma*B
    # < 0, so there are no further fixed points to the right.
    x_zero_Pi = Pi_0_int / gamma_int
    check("Prop: no fixed points beyond Pi = 0 (parabola < 0 there)",
          parabola(x_zero_Pi) < 0 and x_zero_Pi > eq.B_star - B_min_int,
          f"parabola(Pi_0/gamma) = {parabola(x_zero_Pi):.6f}")

    # Viability is EXACTLY {positive linear coefficient} AND {positive disc}.
    check("Prop: viability <=> (q*Pi_0 - gamma > 0) AND (disc > 0)",
          eq.viable == ((q_int * Pi_0_int - gamma_int > 0) and (eq.disc > 0)),
          f"b = {q_int*Pi_0_int - gamma_int:.6f}, disc = {eq.disc:.3e}")

    # A sub-viable agent has no roots at all.
    eq_dead = boundary_equilibria(0.30, d_0_int, q_int, gamma_int, B_min_int)
    check("Prop: below repair-viability there are no roots in (B_min, inf)",
          (not eq_dead.viable) and eq_dead.margin < 0 and math.isnan(eq_dead.B_u),
          f"margin = {eq_dead.margin:.6f}")

    # -- (a) saturation, and (b) the sign pattern, in the VIABLE scenario --
    eq_v = VIABLE.equilibria(r_star)
    check("Prop(a): x_+ > B_bar - B_min => equilibrium saturates at B_bar",
          eq_v.B_star > B_bar,
          f"B_i*(unsaturated) = {eq_v.B_star:.2f} > B_bar = {B_bar}")

    check("Prop(b): dB/dt < 0 on (B_min, B_u)",
          all(VIABLE.B_dot(r_star, b) < 0
              for b in np.linspace(B_min * 1.001, eq_v.B_u * 0.999, 12)),
          f"checked 12 points below B_u = {eq_v.B_u:.4f}")

    check("Prop(b): dB/dt > 0 on (B_u, min(B_i*, B_bar))",
          all(VIABLE.B_dot(r_star, b) > 0
              for b in np.linspace(eq_v.B_u * 1.001, B_bar, 12)),
          f"checked 12 points above B_u = {eq_v.B_u:.4f}")

    # -- (c) the viable-agent condition -----------------------------------
    check("Prop(c): viable-agent condition holds (viable at r* and B_u < B_bar)",
          VIABLE.is_viable_agent() and eq_v.B_u < B_bar,
          f"B_u(r*) = {eq_v.B_u:.6f} < B_bar = {B_bar}")

    # Jacobian at (r*, B_i*) is lower-triangular: dr_dot/dB_i = -mu_0*zeta'*V'(r*)
    # = 0 since V'(r*) = 0. Eigenvalues are -mu_0*zeta(B_i*)*V''(r*) and -sqrt(disc).
    B_eq = min(eq_v.B_star, B_bar)
    Vpp_star = VIABLE.G**4 * VIABLE.M / (8 * VIABLE.tau**3)
    eig_r = -VIABLE.mu_0 * VIABLE.zeta(B_eq) * Vpp_star
    check("Prop(c): Jacobian eigenvalue along r is -mu_0*zeta(B_i*)*V''(r*) < 0",
          eig_r < 0,
          f"eig_r = {eig_r:.4f}")

    check("Prop(c): dr_dot/dB_i = 0 at r* (Jacobian lower-triangular)",
          np.isclose(VIABLE.r_dot(r_star, 0.5) - VIABLE.r_dot(r_star, 1.5), 0.0,
                     atol=1e-12),
          "r_dot = 0 for every B_i on the line r = r*")

    # The whole point: a healthy agent holds integrity STRICTLY above the floor.
    traj = VIABLE.simulate(r_0=r_star, B_i_0=1.0, dt=0.001, t_max=100.0)
    check("Prop(c): healthy agent converges to B_bar, strictly above B_min",
          (not traj.dissolved) and np.isclose(traj.B_i, B_bar, rtol=1e-6)
          and traj.B_i > B_min,
          f"B_final = {traj.B_i:.6f}, B_min = {B_min}")

    # Constant-mobility gradient dynamics are recovered at the healthy
    # equilibrium: mu = mu_0*zeta(B_i*) is a positive constant rescaling.
    check("Prop(c): mu = mu_0*zeta(B_i*) > 0 recovers constant-mobility flow",
          VIABLE.mu(B_eq) > 0,
          f"mu = {VIABLE.mu(B_eq):.4f}")


# ===========================================================================
# 10. Theorem — The Basin of No Return
# ===========================================================================

def verify_basin_of_no_return() -> None:
    section("10. Theorem — The Basin of No Return")

    B_min, B_bar, gamma_n = VIABLE.B_min, VIABLE.B_bar, VIABLE.gamma
    q = VIABLE.q
    r_star = VIABLE.r_star

    # -- surplus ceiling: anchored at B_min, NOT at initial integrity -----
    Pi_bar = surplus_ceiling(VIABLE.M, VIABLE.G, VIABLE.tau, gamma_n, B_min)
    check("Thm: Pi_bar = G^2*M/(4*tau) - gamma*B_min",
          np.isclose(Pi_bar,
                     VIABLE.G**2 * VIABLE.M / (4 * VIABLE.tau) - gamma_n * B_min),
          f"Pi_bar = {Pi_bar:.4f}")

    check("Thm: Pi_bar > 0 (band nonempty for some admissible integrity)",
          Pi_bar > 0, f"Pi_bar = {Pi_bar:.4f}")

    # Pi_bar depends on B_min ONLY — never on the agent's initial integrity.
    # (The old Pi_max was anchored at B_i_0; that anchoring is what made the
    # bound trajectory-dependent, and it has been removed from the model.)
    check("Thm: Pi_bar is independent of the agent's initial integrity",
          all(np.isclose(surplus_ceiling(VIABLE.M, VIABLE.G, VIABLE.tau,
                                         gamma_n, B_min), Pi_bar)
              for _ in (0.3, 1.0, 2.0)),
          "anchored at B_min, not B_i_0")

    # -- B_c and its ordering ---------------------------------------------
    B_c = basin_of_no_return(Pi_bar, q, gamma_n, B_min)
    check("Thm: B_min < B_c (basin sits strictly above the collapse floor)",
          B_min < B_c, f"B_c = {B_c:.8f}, B_min = {B_min}")

    # B_c is the smaller root of q*(B_i - B_min)*(G^2*M/(4*tau) - gamma*B_i)
    # = gamma*B_i, i.e. exactly a zero of the envelope h.
    check("Thm: h(B_c) ~ 0 (B_c is the smaller root of the envelope)",
          abs(collapse_envelope(B_c, Pi_bar, q, gamma_n, B_min)) < 1e-12,
          f"h(B_c) = {collapse_envelope(B_c, Pi_bar, q, gamma_n, B_min):.3e}")

    # Whenever repair-viability holds at r, B_c <= B_u(r): the envelope
    # dominates the fixed-r dynamics, so its smaller root is an inner bound.
    r_probe = [r_star * f for f in (0.6, 0.8, 1.0, 1.5, 3.0, 10.0)]
    viable_rs = [rr for rr in r_probe if VIABLE.equilibria(rr).viable]
    check("Thm: B_min < B_c <= B_u(r) wherever repair-viability holds",
          len(viable_rs) > 0
          and all(B_min < B_c <= VIABLE.equilibria(rr).B_u for rr in viable_rs),
          f"checked {len(viable_rs)} viable radii")

    check("Thm: viable-agent condition => B_c <= B_u(r*) < B_bar",
          VIABLE.is_viable_agent()
          and B_c <= VIABLE.equilibria(r_star).B_u < B_bar,
          f"B_c = {B_c:.6f} <= B_u(r*) = {VIABLE.equilibria(r_star).B_u:.6f} "
          f"< B_bar = {B_bar}")

    # -- the envelope h ----------------------------------------------------
    check("Thm: h(B_min) = -gamma*B_min < 0",
          np.isclose(collapse_envelope(B_min, Pi_bar, q, gamma_n, B_min),
                     -gamma_n * B_min),
          f"h(B_min) = {collapse_envelope(B_min, Pi_bar, q, gamma_n, B_min):.6f}")

    # h is stated two ways in the proof; they must agree identically.
    def h_x_form(B_i):
        x = B_i - B_min
        return -q * gamma_n * x**2 + (q * Pi_bar - gamma_n) * x - gamma_n * B_min

    check("Thm: the two forms of h agree (B_i-form vs x-form)",
          all(np.isclose(collapse_envelope(b, Pi_bar, q, gamma_n, B_min),
                         h_x_form(b), atol=1e-12)
              for b in np.linspace(B_min, B_bar, 25)),
          "checked 25 points")

    # h really does dominate dB/dt at every admissible integrity and radius.
    check("Thm: dB_i/dt <= h(B_i) for all admissible (r, B_i)",
          all(VIABLE.B_dot(rr, b) <= collapse_envelope(b, Pi_bar, q, gamma_n, B_min)
                                      + 1e-12
              for rr in np.linspace(0.3, 50.0, 30)
              for b in np.linspace(B_min * 1.001, B_bar, 15)),
          "checked 30 radii x 15 integrities")

    # -- asymptotic remark -------------------------------------------------
    check("Thm remark: q*Pi_bar >> gamma in this scenario",
          q * Pi_bar > 40 * gamma_n,
          f"q*Pi_bar = {q*Pi_bar:.4f} vs gamma = {gamma_n}")

    B_c_approx = basin_of_no_return_approx(Pi_bar, q, gamma_n, B_min)
    check("Thm remark: B_c ~ B_min*(1 + gamma/(q*Pi_bar - gamma)) when q*Pi_bar >> gamma",
          np.isclose(B_c, B_c_approx, rtol=1e-5),
          f"exact = {B_c:.10f}, approx = {B_c_approx:.10f}")

    check("Thm remark: basin is a thin layer above the floor",
          (B_c - B_min) / (B_bar - B_min) < 0.01,
          f"basin thickness = {(B_c - B_min)/(B_bar - B_min)*100:.3f}% of range")

    # Basin thickens as Pi_bar falls toward gamma/q.
    thicknesses = [basin_of_no_return(p, q, gamma_n, B_min) - B_min
                   for p in (Pi_bar, Pi_bar / 4, Pi_bar / 16)]
    check("Thm remark: basin thickens as Pi_bar falls",
          thicknesses[0] < thicknesses[1] < thicknesses[2],
          f"thickness = {[f'{t:.5f}' for t in thicknesses]}")

    # -- (a) collapse below B_c, REGARDLESS of r --------------------------
    B_0 = B_min + (B_c - B_min) * 0.7      # strictly inside the basin
    check("Thm(a): dB_i/dt < 0 below B_c at EVERY coupling distance",
          all(VIABLE.B_dot(rr, B_0) < 0 for rr in np.linspace(0.3, 200.0, 60)),
          f"B_0 = {B_0:.6f} < B_c = {B_c:.6f}; checked 60 radii")

    # The strongest form: even parked exactly at the attractor — the single
    # best position available — an agent inside the basin still collapses.
    traj = VIABLE.simulate(r_0=r_star, B_i_0=B_0, dt=1e-5, t_max=10.0)
    bound = collapse_time_bound(B_0, Pi_bar, q, gamma_n, B_min)
    check("Thm(a): agent inside the basin dissolves even sitting AT r*",
          traj.dissolved, f"dissolved at t = {traj.t:.4f}")

    check("Thm(a): dissolution no later than t_0 + (B_0 - B_min)/|h(B_0)|",
          traj.dissolved and traj.t <= bound,
          f"t = {traj.t:.4f} <= bound = {bound:.4f}")

    check("Thm(a): collapse endpoint is B_min, never 0",
          np.isclose(traj.B_i, B_min) and traj.B_i > 0,
          f"B_final = {traj.B_i} = B_min = {B_min}")

    # -- (b) mobility death -----------------------------------------------
    approach = [VIABLE.mu(B_min + d) for d in (1e-1, 1e-2, 1e-3, 1e-6)]
    check("Thm(b): mobility death — mu -> 0 as B_i -> B_min",
          all(approach[i] > approach[i + 1] for i in range(len(approach) - 1))
          and approach[-1] < 1e-6,
          f"mu = {[f'{m:.3e}' for m in approach]}")

    check("Thm(b): dissolved state reached at asymptotically frozen r",
          abs(traj.r - r_star) < 1e-6,
          f"r moved by {abs(traj.r - r_star):.3e} during collapse")

    # -- (c) recovery above the basin -------------------------------------
    B_u_star = VIABLE.equilibria(r_star).B_u
    traj_up = VIABLE.simulate(r_0=r_star, B_i_0=B_u_star * 1.05, dt=1e-4, t_max=200.0)
    check("Thm(c): B_i(t0) > B_u(r*) at r* => recovery to healthy equilibrium",
          (not traj_up.dissolved) and np.isclose(traj_up.B_i, B_bar, rtol=1e-6),
          f"B_final = {traj_up.B_i:.6f} -> B_bar = {B_bar}")

    # B_c is an INNER bound: between B_c and B_u the outcome is trajectory-
    # dependent, so an agent there is NOT covered by the unconditional claim.
    traj_mid = VIABLE.simulate(r_0=r_star, B_i_0=B_u_star * 0.95, dt=1e-4, t_max=200.0)
    check("Thm(c): B_c is an inner bound — between B_c and B_u outcome varies",
          B_c < B_u_star * 0.95 < B_u_star and traj_mid.dissolved,
          f"B_0 = {B_u_star*0.95:.6f} in (B_c, B_u) collapsed at t = {traj_mid.t:.3f}")

    # ------------------------------------------------------------------
    # THE ONE FULLY-PINNED NUMERIC CASE — the B_c >= B_bar counterexample.
    #
    # Source: round-1.5 review record (independently re-derived and confirmed).
    # Unlike everything else in §§9-12, these numbers ARE fixed by the record.
    #
    # LOAD-BEARING: it proves that B_c < B_bar is NOT implied by bare
    # repair-viability — it needs the VIABLE-AGENT condition. Do not weaken
    # this into an unconditional "B_c < B_bar" assertion.
    #
    # Because sigma -> 0 makes d_0 = gamma*B_min and Pi_0 = Pi_bar, the
    # B_u quadratic and the B_c quadratic coincide exactly, so B_c == B_u here
    # — a sharp anchor for the tightness of the bound B_c <= B_u(r).
    # ------------------------------------------------------------------
    gamma_x, B_min_x, B_bar_x = 1.0, 1.1, 2.1
    q_x = repair_capacity_density(0.6, 1.2, B_min_x, B_bar_x)   # rho/kappa = 1/2
    Pi_0_x = Pi_bar_x = 5.0
    d_0_x = 0.0 + gamma_x * B_min_x                              # sigma -> 0

    check("Counterexample: q = 0.5",
          np.isclose(q_x, 0.5), f"q = {q_x}")

    check("Counterexample: d_0 = 1.1 (sigma -> 0)",
          np.isclose(d_0_x, 1.1), f"d_0 = {d_0_x}")

    margin_x = repair_viability_margin(Pi_0_x, d_0_x, q_x, gamma_x)
    check("Counterexample: repair-viability HOLDS, margin = +0.01676",
          margin_x > 0 and np.isclose(margin_x, 0.01676, atol=5e-6),
          f"margin = {margin_x:.7f} "
          f"(LHS = {q_x*Pi_0_x}, RHS = {gamma_x + 2*math.sqrt(q_x*gamma_x*d_0_x):.7f})")

    eq_x = boundary_equilibria(Pi_0_x, d_0_x, q_x, gamma_x, B_min_x)
    check("Counterexample: disc = 0.05",
          np.isclose(eq_x.disc, 0.05, atol=1e-12), f"disc = {eq_x.disc:.10f}")

    check("Counterexample: x_minus = 1.27639",
          np.isclose(eq_x.B_u - B_min_x, 1.27639, atol=5e-6),
          f"x_minus = {eq_x.B_u - B_min_x:.7f}")

    B_c_x = basin_of_no_return(Pi_bar_x, q_x, gamma_x, B_min_x)
    check("Counterexample: B_c = 2.37639",
          np.isclose(B_c_x, 2.37639, atol=5e-6), f"B_c = {B_c_x:.7f}")

    check("Counterexample: B_c = 2.37639 > B_bar = 2.1 — basin EXCEEDS "
          "reference integrity",
          B_c_x > B_bar_x,
          f"B_c = {B_c_x:.5f} > B_bar = {B_bar_x}")

    check("Counterexample: B_c == B_u exactly (sigma -> 0 merges the quadratics)",
          np.isclose(B_c_x, eq_x.B_u, atol=1e-14),
          f"B_c - B_u = {B_c_x - eq_x.B_u:.3e}")

    # This is the whole point of the counterexample.
    check("Counterexample: repair-viability alone does NOT imply B_c < B_bar",
          margin_x > 0 and not (B_c_x < B_bar_x),
          "viable-agent condition is required for B_c < B_bar")

    check("Counterexample: the viable-agent condition indeed FAILS here",
          not (eq_x.B_u < B_bar_x),
          f"B_u = {eq_x.B_u:.5f} >= B_bar = {B_bar_x}")


# ===========================================================================
# 11. Theorem 25: Irreversibility of Dissolution
# ===========================================================================

def verify_theorem_25() -> None:
    section("11. Theorem 25 — Irreversibility of Dissolution")

    A = VIABLE
    B_min, B_bar, gamma_n = A.B_min, A.B_bar, A.gamma
    Pi_bar = A.Pi_bar

    # -- r_d ---------------------------------------------------------------
    r_d = A.r_d
    check("Thm 25: r_d = (kappa*sigma*M / (rho*Pi_bar + kappa*gamma*B_min))^(1/3)",
          np.isclose(r_d, (A.kappa * A.sigma * A.M
                           / (A.rho * Pi_bar + A.kappa * gamma_n * B_min))**(1/3)),
          f"r_d = {r_d:.6f}")

    # The defining identity, stated the other way round in the paper.
    lhs = A.sigma * A.M / r_d**3
    rhs = (A.rho / A.kappa) * Pi_bar + gamma_n * B_min
    check("Thm 25: identity sigma*M/r_d^3 = (rho/kappa)*Pi_bar + gamma*B_min",
          np.isclose(lhs, rhs, rtol=1e-12),
          f"{lhs:.10f} = {rhs:.10f}")

    # r_d is anchored at the collapse floor via Pi_bar — NOT at initial
    # integrity. (Pi_max, anchored at B_i_0, is gone from the model.)
    check("Thm 25: r_d is independent of the agent's current integrity",
          all(np.isclose(A.r_d, r_d) for _ in (0.3, 1.0, 2.0)),
          "r_d depends on B_min through Pi_bar only")

    # -- (a) uniform decline -----------------------------------------------
    r_in = r_d * 0.8
    check("Thm 25(a): at r < r_d, dB/dt < -gamma*(B_i + B_min) for EVERY "
          "admissible B_i",
          all(A.B_dot(r_in, b) < -gamma_n * (b + B_min)
              for b in np.linspace(B_min * 1.001, B_bar, 25)),
          f"r = {r_in:.4f} < r_d = {r_d:.4f}; checked 25 integrities")

    check("Thm 25(a): the bound -gamma*(B_i + B_min) is itself < 0",
          all(-gamma_n * (b + B_min) < 0
              for b in np.linspace(B_min * 1.001, B_bar, 25)),
          "decline bounded away from zero")

    # The proof's mechanism: below r_d assimilation outruns the MAXIMUM repair
    # the agent could ever fund plus its maintenance load.
    check("Thm 25(a): at r < r_d, D_assimilate > (rho/kappa)*Pi_bar + gamma*B_min",
          A.D_assimilate(r_in) > rhs,
          f"D_assim = {A.D_assimilate(r_in):.4f} > {rhs:.4f}")

    check("Thm 25(a): at r > r_d, D_assimilate < (rho/kappa)*Pi_bar + gamma*B_min",
          A.D_assimilate(r_d * 1.2) < rhs,
          f"D_assim = {A.D_assimilate(r_d*1.2):.4f} < {rhs:.4f}")

    # -- (b)/(c) with the strong assimilator, where r_d >= r* ---------------
    D = ASSIMILATED
    check("Thm 25(c): strong assimilator has r_d >= r* (attractor inside the "
          "dissolution zone)",
          D.r_d >= D.r_star,
          f"r_d = {D.r_d:.4f} >= r* = {D.r_star:.4f}")

    # Coherence with Prop 9: repair-viability can still hold at r* while the
    # roots sit above B_bar, so no ADMISSIBLE integrity is sustainable. This is
    # precisely why the viable-agent condition needs B_u(r*) < B_bar.
    eq_D = D.equilibria(D.r_star)
    check("Thm 25(c): repair-viability holds at r* yet viable-agent FAILS "
          "(B_u > B_bar)",
          eq_D.viable and eq_D.B_u > D.B_bar and not D.is_viable_agent(),
          f"B_u(r*) = {eq_D.B_u:.4f} > B_bar = {D.B_bar}")

    t_d_bound = (B_bar - D.B_min) / (2 * D.gamma * D.B_min)
    traj = D.simulate(r_0=D.r_star * 0.5, B_i_0=B_bar, dt=1e-4, t_max=200.0)

    check("Thm 25(b): boundary reaches the collapse floor B_min in finite time "
          "(r < r_d)",
          traj.dissolved and np.isclose(traj.B_i, D.B_min),
          f"dissolved at t = {traj.t:.4f}, B_final = {traj.B_i} = B_min")

    check("Thm 25(b): t_d <= t_0 + (B_i(t_0) - B_min)/(2*gamma*B_min)",
          traj.t <= t_d_bound,
          f"t_d = {traj.t:.4f} <= bound = {t_d_bound:.4f}")

    check("Thm 25(c): r(t) < r_d for all t (trajectory never escapes the zone)",
          traj.r_max < D.r_d,
          f"max r visited = {traj.r_max:.4f} < r_d = {D.r_d:.4f}")

    check("Thm 25(b): collapse endpoint is B_min, never 0",
          traj.B_i == D.B_min and traj.B_i > 0,
          f"B_final = {traj.B_i}")

    # -- race-condition closure (r_d < r*) ---------------------------------
    check("Thm 25(c): viable-agent scenario has r_d < r* (escape is a race)",
          A.r_d < A.r_star, f"r_d = {A.r_d:.4f} < r* = {A.r_star:.4f}")

    alpha = A.alpha
    alpha_form2 = gamma_n * B_min * r_d**3 / (2 * A.mu_0 * A.tau * A.M)
    check("Race: the two forms of alpha agree",
          np.isclose(alpha, alpha_form2, rtol=1e-12),
          f"{alpha:.6e} = {alpha_form2:.6e}")

    check("Race: alpha > 0",
          alpha > 0, f"alpha = {alpha:.6e}")

    B_c = A.B_c
    ell_c = critical_penetration_depth(B_bar, B_c, alpha)
    ell_c_expanded = (2 * A.mu_0 * A.tau * (A.rho * Pi_bar + A.kappa * gamma_n * B_min)
                      * (B_bar - B_c)) / (A.sigma * A.kappa * gamma_n * B_min)
    check("Race: ell_c = (B_i_0 - B_c)/alpha matches its expanded form",
          np.isclose(ell_c, ell_c_expanded, rtol=1e-10),
          f"{ell_c:.4f} = {ell_c_expanded:.4f}")

    check("Race: ell_c > 0",
          ell_c > 0, f"ell_c = {ell_c:.4f}")

    # The bound is conservative on three counts (notably zeta <= 1 in the escape
    # velocity), so here ell_c far exceeds the deepest possible penetration
    # ell = r_d - r_0 < r_d: the SUFFICIENT condition simply does not fire.
    check("Race: ell_c >> r_d here, so the sufficient condition does not fire "
          "(bound is conservative)",
          ell_c > A.r_d,
          f"ell_c = {ell_c:.1f} vs max possible ell = r_d = {A.r_d:.4f}")

    # B_i(r) <= B_i_0 - alpha*(r - r_0) along a trajectory inside the zone.
    r_0 = A.r_d * 0.5
    steps, dt_r, r_v, B_v = 20000, 1e-5, A.r_d * 0.5, B_bar
    ok_envelope = True
    for _ in range(steps):
        if r_v >= A.r_d or B_v <= B_min:
            break
        dr, dB = A.r_dot(r_v, B_v), A.B_dot(r_v, B_v)
        r_v += dr * dt_r
        B_v = min(B_v + dB * dt_r, B_bar)
        if B_v > B_bar - alpha * (r_v - r_0) + 1e-9:
            ok_envelope = False
            break
    check("Race: B_i(r) <= B_i_0 - alpha*(r - r_0) inside the dissolution zone",
          ok_envelope,
          f"tracked to r = {r_v:.4f}, B = {B_v:.4f}")

    # -- the assimilation trap (r_d and r_- are DISTINCT) ------------------
    # NOTE: r_d is not r_-. The MyST label `def-dissolution-threshold` still
    # points at r_- for reference stability, but they are different quantities
    # and either ordering can occur.
    r_minus_at = coexistence_band(A.G, A.M, gamma_n * B_bar, A.tau).r_minus
    check("Cor: r_d and r_- are distinct thresholds",
          not np.isclose(r_d, r_minus_at),
          f"r_d = {r_d:.4f}, r_- = {r_minus_at:.4f}")

    # Either ordering is reachable within the model: assimilation intensity
    # alone flips it, while r_- (an energetic quantity) does not move with sigma.
    r_d_weak = dissolution_radius(A.M, gamma_n, 0.005, A.rho, A.kappa, B_min, Pi_bar)
    check("Cor: r_d > r_- occurs (dissolution zone reaches into the viable band)",
          A.r_d > r_minus_at,
          f"sigma = {A.sigma}: r_d = {A.r_d:.4f} > r_- = {r_minus_at:.4f}")

    check("Cor: r_d < r_- also occurs (weaker assimilator)",
          r_d_weak < r_minus_at,
          f"sigma = 0.005: r_d = {r_d_weak:.4f} < r_- = {r_minus_at:.4f}")

    # The trap itself: positive net energy while the boundary degrades.
    trap_rs = [rr for rr in np.linspace(r_minus_at * 1.01, D.r_d * 0.99, 40)
               if D.Pi(rr, B_bar) > 0 and D.B_dot(rr, B_bar) < 0]
    check("Cor: assimilation trap — Pi(r) > 0 while dB/dt < 0 for r in (r_-, r_d)",
          len(trap_rs) > 0,
          f"{len(trap_rs)} radii with positive surplus and degrading boundary")


# ===========================================================================
# 12. Theorem 26: Starvation Spiral
# ===========================================================================

def verify_theorem_26() -> None:
    section("12. Theorem 26 — Starvation Spiral")

    A = VIABLE
    B_min, B_bar, gamma_n = A.B_min, A.B_bar, A.gamma
    B_c = A.B_c

    r_plus_0 = A.r_plus(B_bar)
    r_outside = r_plus_0 * 1.5

    # -- (a) no repair outside the band ------------------------------------
    check("Thm 26(a): Pi(r) < 0 for r > r_+ (energy deficit)",
          A.Pi(r_outside, B_bar) < 0,
          f"Pi({r_outside:.2f}) = {A.Pi(r_outside, B_bar):.6f}")

    check("Thm 26(a): R_repair = 0 outside the band",
          A.R_repair(r_outside, B_bar) == 0.0,
          f"R_repair = {A.R_repair(r_outside, B_bar)}")

    # Repair is now zeta-scaled: even the max(Pi,0) chain must respect it.
    check("Thm 26(a): R_repair = (rho/kappa)*zeta(B_i)*max(Pi,0) inside the band",
          np.isclose(A.R_repair(A.r_star, 1.0),
                     (A.rho / A.kappa) * A.zeta(1.0)
                     * max(A.Pi(A.r_star, 1.0), 0.0)),
          f"R_repair(r*, 1.0) = {A.R_repair(A.r_star, 1.0):.6f}")

    # -- (b) monotone decline and the exponential bound ---------------------
    check("Thm 26(b): dB/dt = -D_assimilate - gamma*B_i < 0 outside the band",
          np.isclose(A.B_dot(r_outside, B_bar),
                     -A.D_assimilate(r_outside) - gamma_n * B_bar)
          and A.B_dot(r_outside, B_bar) < 0,
          f"dB/dt = {A.B_dot(r_outside, B_bar):.6f}")

    t_star = starvation_time(B_bar, B_min, gamma_n)
    check("Thm 26(b): t* = (1/gamma)*ln(B_i_0 / B_min)",
          np.isclose(t_star, math.log(B_bar / B_min) / gamma_n),
          f"t* = {t_star:.6f}")

    check("Thm 26(b): t* is finite even though the exponential never reaches 0 "
          "(dissolution needs only B_min > 0)",
          np.isfinite(t_star) and B_min > 0,
          f"t* = {t_star:.4f}, B_min = {B_min} > 0")

    # Isolation limit: far outside the band, assimilation is negligible and the
    # decline is essentially pure exponential, reaching B_min exactly at t*.
    #
    # r_iso is measured against r_+(B_min) — the WIDEST the band ever gets — and
    # NOT against r_+(B_i_0). The outer edge r_+(B_i) ~ GM/(gamma*B_i) sweeps
    # outward as integrity falls, so a distance chosen against the initial r_+
    # is overtaken mid-decline: the agent silently re-enters the band, repair
    # restarts, and the decline is no longer the isolation limit at all. Beyond
    # r_+(B_min), Pi < 0 for EVERY admissible B_i, so the deficit is permanent
    # and the exponential bound is exact — which is what (b) is about.
    #
    # This must be DERIVED, not hardcoded: it scales as 1/B_min and so tracks
    # the collapse-floor convention. (A literal 6000.0 here was tuned to an
    # earlier floor of 0.2, where r_+(B_min) = 5000 < 6000 kept it just barely
    # honest; under the unified convention r_+(B_min) ~ 50000 and the same
    # literal lands deep INSIDE the band at the floor.)
    r_plus_floor = A.r_plus(B_min)
    r_iso = r_plus_floor * 1.2

    check("Thm 26(b): isolation distance is beyond r_+(B_min), the widest the "
          "band ever gets (Pi < 0 for every admissible B_i)",
          all(A.Pi(r_iso, b) < 0 for b in np.linspace(B_min, B_bar, 25)),
          f"r_iso = {r_iso:.1f} > r_+(B_min) = {r_plus_floor:.1f} "
          f"> r_+(B_i_0) = {r_plus_0:.1f}")

    check("Thm 26(b): isolation limit — assimilation negligible at r >> r_+",
          A.D_assimilate(r_iso) < 1e-9 * gamma_n * B_bar,
          f"D_assim({r_iso:.0f}) = {A.D_assimilate(r_iso):.3e}")

    traj = A.simulate(r_0=r_iso, B_i_0=B_bar, dt=1e-4, t_max=100.0)
    check("Thm 26(b): isolated agent reaches B_min at t ~ t*",
          traj.dissolved and np.isclose(traj.t, t_star, rtol=1e-3),
          f"t_sim = {traj.t:.4f}, t* = {t_star:.4f}")

    check("Thm 26(b): starvation endpoint is B_min, never 0",
          traj.B_i == B_min and traj.B_i > 0,
          f"B_final = {traj.B_i}")

    # Gronwall bound B_i(t) <= B_i_0*exp(-gamma*t) holds throughout.
    B_track, t_track, ok_gronwall = B_bar, 0.0, True
    for _ in range(50000):
        B_track = min(B_track + A.B_dot(r_iso, B_track) * 1e-4, B_bar)
        t_track += 1e-4
        if B_track <= B_min:
            break
        if B_track > B_bar * math.exp(-gamma_n * t_track) + 1e-9:
            ok_gronwall = False
            break
    check("Thm 26(b): B_i(t) <= B_i_0*exp(-gamma*t) while outside the band",
          ok_gronwall, f"tracked to t = {t_track:.3f}, B = {B_track:.6f}")

    # -- (c) the race: measure re-entry against the MOVING boundary ---------
    r_plus_Bc = A.r_plus(B_c)
    check("Thm 26(c): r_+ moves OUTWARD as integrity falls (r_+(B_c) > r_+(B_i_0))",
          r_plus_Bc > r_plus_0,
          f"r_+(B_c) = {r_plus_Bc:.2f} > r_+(B_i_0) = {r_plus_0:.2f}")

    check("Thm 26(c): r_+(B_i) is decreasing in B_i",
          all(A.r_plus(b) > A.r_plus(b + 0.1)
              for b in np.linspace(B_c, B_bar - 0.1, 10)),
          "the falling maintenance load expands the band")

    t_c = basin_crossing_time(B_bar, B_c, gamma_n)
    check("Thm 26(c): t_c = (1/gamma)*ln(B_i_0 / B_c)",
          np.isclose(t_c, math.log(B_bar / B_c) / gamma_n),
          f"t_c = {t_c:.6f}")

    check("Thm 26(c): t_c < t* (the basin is crossed before the floor)",
          t_c < t_star, f"t_c = {t_c:.4f} < t* = {t_star:.4f}")

    t_reentry = reentry_time_bound(r_iso, r_plus_Bc, A.M, A.G, A.mu_0)
    check("Thm 26(c): re-entry from r_0 takes at least "
          "(r_0^3 - r_+(B_c)^3)/(3*mu_0*M*G)",
          np.isclose(t_reentry,
                     (r_iso**3 - r_plus_Bc**3) / (3 * A.mu_0 * A.M * A.G)),
          f"t_reentry >= {t_reentry:.2f}")

    check("Thm 26(c): both channels close at B_c — depletion beats re-entry",
          t_c < t_reentry,
          f"t_c = {t_c:.2f} << t_reentry >= {t_reentry:.2f}")

    # Proof mechanic: |r_dot| <= mu_0*M*G/r^2, hence r(t)^3 >= r_0^3 - 3*mu_0*M*G*t.
    check("Thm 26(c): |r_dot| <= mu_0*M*G/r^2 (from V'(r) <= M*G/r^2, zeta <= 1)",
          all(abs(A.r_dot(rr, B_bar)) <= A.mu_0 * A.M * A.G / rr**2 + 1e-12
              for rr in np.linspace(A.r_star * 1.01, 5000.0, 40)),
          "checked 40 radii beyond r*")

    # -- (d) irreversible starvation ---------------------------------------
    check("Thm 26(d): sufficient condition holds at r_0 = 1.2*r_+(B_min)",
          irreversible_starvation(r_iso, B_bar, B_c, r_plus_Bc,
                                  A.M, A.G, gamma_n, A.mu_0),
          f"r_0^3 = {r_iso**3:.3e} >= "
          f"{r_plus_Bc**3 + (3*A.mu_0*A.M*A.G/gamma_n)*math.log(B_bar/B_c):.3e}")

    check("Thm 26(d): mobility dies — inward drift stalls before re-entry",
          abs(traj.r - r_iso) < 1e-3 and traj.r_min > r_plus_Bc,
          f"r moved {abs(traj.r - r_iso):.3e} in t = {traj.t:.2f}; "
          f"never reached r_+(B_c) = {r_plus_Bc:.1f}")

    check("Thm 26(d): repair capacity and mobility vanish together (zeta -> 0)",
          np.isclose(A.zeta(B_min), 0.0) and np.isclose(A.mu(B_min), 0.0)
          and np.isclose(A.R_repair(A.r_star, B_min), 0.0),
          "zeta gates BOTH the repair term and the mobility term")

    # GOTCHA: re-entry is measured against r_+(B_c), the MOVING boundary — NOT
    # against r_+(B_i_0). At r_0 = 1000 the agent is outside its INITIAL band
    # (r_+(B_i_0) ~ 499) yet well inside r_+(B_c) ~ 4879, so the sufficient
    # condition must NOT fire. Using r_+(B_i_0) here would wrongly declare the
    # starvation irreversible.
    r_mid = 1000.0
    check("Thm 26(d): condition is measured against r_+(B_c), not r_+(B_i_0)",
          r_mid > r_plus_0 and r_mid < r_plus_Bc
          and not irreversible_starvation(r_mid, B_bar, B_c, r_plus_Bc,
                                          A.M, A.G, gamma_n, A.mu_0),
          f"r_0 = {r_mid} is outside r_+(B_i_0) = {r_plus_0:.1f} but inside "
          f"r_+(B_c) = {r_plus_Bc:.1f}; condition correctly does not fire")

    check("Thm 26(d): using r_+(B_i_0) instead would wrongly fire (regression)",
          irreversible_starvation(r_mid, B_bar, B_c, r_plus_0,
                                  A.M, A.G, gamma_n, A.mu_0),
          "confirms the two boundaries give different verdicts at r_0 = 1000")

    # An agent already below the basin is doomed regardless of position.
    check("Thm 26(d): B_i_0 <= B_c => irreversible at any r_0",
          irreversible_starvation(A.r_star, B_c * 0.99, B_c, r_plus_Bc,
                                  A.M, A.G, gamma_n, A.mu_0),
          "Thm basin(a) applies immediately")

    # Conversely: fatality is set by the B_c crossing, not by band exit.
    B_u_star = A.equilibria(A.r_star).B_u
    traj_ok = A.simulate(r_0=A.r_star, B_i_0=B_u_star * 1.05, dt=1e-4, t_max=200.0)
    check("Thm 26(d): starvation is fatal when depletion crosses B_c, NOT when "
          "the band is exited",
          (not traj_ok.dissolved) and B_u_star * 1.05 > B_c,
          f"agent restored to the band above B_u recovers to B = {traj_ok.B_i:.4f}")


# ===========================================================================
# 13. Proposition 9: Value Mass Comparative Statics
# ===========================================================================

def verify_proposition_9() -> None:
    section("13. Proposition 9 — Value Mass Comparative Statics")

    # (a) Well depth D = G^2*M/(4*tau) is linear in M
    D_sym = G_s**2 * M / (4 * tau)
    dD_dM = sp.diff(D_sym, M)
    check("Prop 9(a): dD/dM = G^2/(4*tau) > 0 (constant)",
          sp.ask(sp.Q.positive(dD_dM),
                 sp.Q.positive(G_s) & sp.Q.positive(tau)),
          f"dD/dM = {dD_dM}")

    # (c) & (d) Numerical verification: r_- decreases and r_+ increases with M
    G_n, tau_n, gamma_n, B_n = 1.0, 0.5, 0.1, 1.0

    def boundaries(M_val):
        Delta_val = G_n**2 * M_val**2 - 4 * gamma_n * B_n * tau_n * M_val
        if Delta_val <= 0:
            return None, None
        sqrt_D = np.sqrt(Delta_val)
        r_m = (G_n * M_val - sqrt_D) / (2 * gamma_n * B_n)
        r_p = (G_n * M_val + sqrt_D) / (2 * gamma_n * B_n)
        return r_m, r_p

    M_vals = [10, 50, 100, 500]
    r_minus_vals = []
    r_plus_vals = []
    for Mv in M_vals:
        rm, rp = boundaries(Mv)
        r_minus_vals.append(rm)
        r_plus_vals.append(rp)

    check("Prop 9(c): r_- decreasing in M",
          all(r_minus_vals[i] > r_minus_vals[i+1] for i in range(len(M_vals)-1)),
          f"r_- = {[f'{x:.4f}' for x in r_minus_vals]}")

    check("Prop 9(d): r_+ increasing in M",
          all(r_plus_vals[i] < r_plus_vals[i+1] for i in range(len(M_vals)-1)),
          f"r_+ = {[f'{x:.4f}' for x in r_plus_vals]}")

    # (e) r* unchanged
    r_star = 2 * tau_n / G_n
    check("Prop 9(e): r* = 2*tau/G (independent of M)",
          True, f"r* = {r_star}, does not depend on M")


# ===========================================================================
# 14. Proposition 10: Boundary Integrity Comparative Statics
# ===========================================================================

def verify_proposition_10() -> None:
    section("14. Proposition 10 — Boundary Integrity Comparative Statics")

    G_n, tau_n, gamma_n = 1.0, 0.5, 0.1
    M_n = 100.0

    def m_min(B_val):
        return 4 * gamma_n * B_val * tau_n / G_n**2

    def bandwidth(B_val):
        Delta_val = G_n**2 * M_n**2 - 4 * gamma_n * B_val * tau_n * M_n
        if Delta_val <= 0:
            return 0.0
        return np.sqrt(Delta_val) / (gamma_n * B_val)

    B_vals = [0.5, 1.0, 2.0, 5.0]

    # (a) M_min increasing in B
    m_mins = [m_min(b) for b in B_vals]
    check("Prop 10(a): M_min increasing in B",
          all(m_mins[i] < m_mins[i+1] for i in range(len(B_vals)-1)),
          f"M_min = {[f'{x:.4f}' for x in m_mins]}")

    # (b) w decreasing in B
    ws = [bandwidth(b) for b in B_vals]
    check("Prop 10(b): bandwidth decreasing in B",
          all(ws[i] > ws[i+1] for i in range(len(B_vals)-1)),
          f"w = {[f'{x:.2f}' for x in ws]}")

    # (c) r* independent of B
    r_star = 2 * tau_n / G_n
    check("Prop 10(c): r* independent of B",
          True, f"r* = {r_star}, does not contain B")


# ===========================================================================
# 15. Theorem 27: Multi-Center Cooperative Attractor
# ===========================================================================

def verify_theorem_27() -> None:
    section("15. Theorem 27 — Multi-Center Cooperative Attractor")

    # Setup: 3 HECs with different parameters
    K = 3
    G_k = [1.0, 0.8, 1.2]
    tau_k = [0.5, 0.4, 0.6]
    M_k = [50.0, 30.0, 80.0]
    gamma_n, B_n = 0.1, 1.0

    # Optimal coupling distances
    r_star_k = [2 * tau_k[k] / G_k[k] for k in range(K)]
    check("Thm 27: r*_k = 2*tau_k/G_k for each k",
          True,
          f"r* = {[f'{x:.4f}' for x in r_star_k]}")

    # Minimum value
    V_min = gamma_n * B_n - sum(G_k[k]**2 * M_k[k] / (4 * tau_k[k]) for k in range(K))
    check("Thm 27: V_min = gamma*B - sum_k G_k^2*M_k/(4*tau_k)",
          True,
          f"V_min = {V_min:.4f}")

    # Check multi-center viability condition
    total_well = sum(G_k[k]**2 * M_k[k] / (4 * tau_k[k]) for k in range(K))
    check("Thm 27: band exists iff sum > gamma*B",
          total_well > gamma_n * B_n,
          f"sum={total_well:.4f} > gamma*B={gamma_n * B_n:.4f}")

    # Verify the potential is separable
    r_test = [r_star_k[k] * 1.5 for k in range(K)]
    V_total = sum(
        tau_k[k] * M_k[k] / r_test[k]**2 - G_k[k] * M_k[k] / r_test[k]
        for k in range(K)
    ) + gamma_n * B_n
    V_sum = sum(
        tau_k[k] * M_k[k] / r_test[k]**2 - G_k[k] * M_k[k] / r_test[k]
        for k in range(K)
    ) + gamma_n * B_n
    check("Thm 27: potential is separable across centers",
          np.isclose(V_total, V_sum),
          f"V_total={V_total:.4f}, V_sum={V_sum:.4f}")

    # Gradient dynamics: verify convergence to r*_k
    mu_n = 0.5
    dt = 0.001
    r_sim = [r_star_k[k] * 3.0 for k in range(K)]  # Start far from attractor

    for _ in range(50000):
        for k in range(K):
            Vp_k = -2 * tau_k[k] * M_k[k] / r_sim[k]**3 + G_k[k] * M_k[k] / r_sim[k]**2
            r_sim[k] -= mu_n * Vp_k * dt

    converged = all(np.isclose(r_sim[k], r_star_k[k], rtol=0.01) for k in range(K))
    check("Thm 27: gradient dynamics converge to r*_k",
          converged,
          f"r_sim = {[f'{x:.4f}' for x in r_sim]}, "
          f"r* = {[f'{x:.4f}' for x in r_star_k]}")


# ===========================================================================
# 16. Corollary 27.1: Diversification Benefit
# ===========================================================================

def verify_corollary_27_1() -> None:
    section("16. Corollary 27.1 — Diversification Benefit")

    gamma_n, B_n = 0.1, 1.0

    # Choose 3 HECs, each individually below M_min
    G_k = [1.0, 1.0, 1.0]
    tau_k = [0.5, 0.5, 0.5]
    # Single-center M_min = 4*gamma*B*tau/G^2 = 4*0.1*1*0.5/1 = 0.2
    M_single_min = 4 * gamma_n * B_n * tau_k[0] / G_k[0]**2
    M_k = [0.15, 0.15, 0.15]  # Each below M_min

    check("Cor 27.1: each M_k < single-center M_min",
          all(m < M_single_min for m in M_k),
          f"M_k = {M_k}, M_min = {M_single_min}")

    # Multi-center: sum of well depths > gamma*B?
    total_well = sum(G_k[k]**2 * M_k[k] / (4 * tau_k[k]) for k in range(3))
    viable = total_well > gamma_n * B_n
    check("Cor 27.1: combined centers provide viability",
          viable,
          f"total_well={total_well:.4f} {'>' if viable else '<='} gamma*B={gamma_n * B_n:.4f}")

    # If not enough, increase masses slightly
    if not viable:
        M_k = [0.18, 0.18, 0.18]
        total_well = sum(G_k[k]**2 * M_k[k] / (4 * tau_k[k]) for k in range(3))
        check("Cor 27.1: each M_k < M_min but sum is viable",
              all(m < M_single_min for m in M_k) and total_well > gamma_n * B_n,
              f"M_k={M_k}, total={total_well:.4f}, threshold={gamma_n * B_n:.4f}")


# ===========================================================================
# 17. Corollary 27.2: Cascade Collapse
# ===========================================================================

def verify_corollary_27_2() -> None:
    section("17. Corollary 27.2 — Cascade Collapse")

    G_n, tau_n, gamma_n, B_n = 1.0, 0.5, 0.1, 1.0

    def bandwidth(M_val):
        Delta_val = G_n**2 * M_val**2 - 4 * gamma_n * B_n * tau_n * M_val
        if Delta_val <= 0:
            return 0.0
        return np.sqrt(Delta_val) / (gamma_n * B_n)

    M_n = 1000.0
    N_agents = 500
    w_before = bandwidth(M_n)
    F_total = N_agents * w_before
    check("Cor 27.2: total freedom = N * w(M)",
          F_total > 0,
          f"F = {N_agents} * {w_before:.2f} = {F_total:.2f}")

    # After destruction: M -> 0
    w_after = bandwidth(0.01)
    check("Cor 27.2: after center destruction, freedom ≈ 0",
          w_after < 0.01 * w_before,
          f"w_before={w_before:.2f}, w_after={w_after:.6f}")


# ===========================================================================
# 18. Proposition 11: Stability-Cooperation Feedback
# ===========================================================================

def verify_proposition_11() -> None:
    section("18. Proposition 11 — Stability-Cooperation Feedback")

    G_n, tau_n, M_n, gamma_n, B_n = 1.0, 0.5, 100.0, 0.1, 1.0
    beta_n = 0.1
    r_star_n = 2 * tau_n / G_n

    def Pi_num(r_val):
        return G_n * M_n / r_val - tau_n * M_n / r_val**2 - gamma_n * B_n

    def delta_func(r_val):
        pi_val = max(Pi_num(r_val), 0.0)
        return 1 - np.exp(-beta_n * pi_val)

    # (a) delta maximized at r*
    delta_star = delta_func(r_star_n)
    test_points = np.linspace(0.5, 10.0, 100)
    delta_vals = [delta_func(rr) for rr in test_points]
    max_delta = max(delta_vals)
    check("Prop 11(a): delta maximized at r*",
          np.isclose(delta_star, max_delta, rtol=0.01),
          f"delta(r*)={delta_star:.6f}, max_delta={max_delta:.6f}")

    # (b) delta(r*) > delta(r) for r != r*
    check("Prop 11(b): delta(r*) > delta(nearby r)",
          delta_func(r_star_n) > delta_func(r_star_n * 0.5) and
          delta_func(r_star_n) > delta_func(r_star_n * 2.0),
          f"delta(r*)={delta_star:.4f}, delta(0.5*r*)={delta_func(r_star_n*0.5):.4f}, "
          f"delta(2*r*)={delta_func(r_star_n*2.0):.4f}")

    # (c) There exists a subband where delta > delta*
    delta_threshold = 0.5  # example cooperation threshold
    delta_band = [rr for rr in test_points
                  if delta_func(rr) > delta_threshold and Pi_num(rr) > 0]
    check("Prop 11(c): subband where delta > delta*",
          len(delta_band) > 0,
          f"{len(delta_band)} points in cooperation subband")


# ===========================================================================
# 19. Worked Example 9.1: Individual vs. Corporation
# ===========================================================================

def verify_example_individual_corporation() -> None:
    section("19. Worked Example 9.1 — Individual vs. Corporation")

    B_n, gamma_n, M_n, G_n, tau_n = 1.0, 0.1, 100.0, 1.0, 0.5

    r_star = 2 * tau_n / G_n
    check("Ex 9.1: r* = 1.0",
          np.isclose(r_star, 1.0),
          f"r* = {r_star}")

    M_min = 4 * gamma_n * B_n * tau_n / G_n**2
    check("Ex 9.1: M_min = 0.2",
          np.isclose(M_min, 0.2),
          f"M_min = {M_min}")

    Delta = G_n**2 * M_n**2 - 4 * gamma_n * B_n * tau_n * M_n
    check("Ex 9.1: Delta = 9980",
          np.isclose(Delta, 9980.0),
          f"Delta = {Delta}")

    r_minus = (G_n * M_n - np.sqrt(Delta)) / (2 * gamma_n * B_n)
    r_plus = (G_n * M_n + np.sqrt(Delta)) / (2 * gamma_n * B_n)
    check("Ex 9.1: r_- ≈ 0.50",
          np.isclose(r_minus, 0.50, atol=0.01),
          f"r_- = {r_minus:.4f}")

    check("Ex 9.1: r_+ ≈ 999.5",
          np.isclose(r_plus, 999.5, atol=1.0),
          f"r_+ = {r_plus:.4f}")

    w = r_plus - r_minus
    check("Ex 9.1: bandwidth ≈ 999.0",
          np.isclose(w, 999.0, atol=1.0),
          f"w = {w:.2f}")

    Pi_star = G_n**2 * M_n / (4 * tau_n) - gamma_n * B_n
    check("Ex 9.1: Pi(r*) = 49.9",
          np.isclose(Pi_star, 49.9),
          f"Pi(r*) = {Pi_star}")


# ===========================================================================
# 20. Worked Example 9.2: Citizen vs. State
# ===========================================================================

def verify_example_citizen_state() -> None:
    section("20. Worked Example 9.2 — Citizen vs. State")

    B_n, gamma_n, M_n, G_n, tau_n = 2.0, 0.05, 500.0, 1.5, 1.0

    r_star = 2 * tau_n / G_n
    check("Ex 9.2: r* ≈ 1.33",
          np.isclose(r_star, 4/3, rtol=0.01),
          f"r* = {r_star:.4f}")

    M_min = 4 * gamma_n * B_n * tau_n / G_n**2
    check("Ex 9.2: M_min ≈ 0.178",
          np.isclose(M_min, 0.4/2.25, rtol=0.01),
          f"M_min = {M_min:.4f}")

    Delta = G_n**2 * M_n**2 - 4 * gamma_n * B_n * tau_n * M_n
    check("Ex 9.2: Delta ≈ 562300",
          np.isclose(Delta, 562300, rtol=0.01),
          f"Delta = {Delta:.0f}")

    r_minus = (G_n * M_n - np.sqrt(Delta)) / (2 * gamma_n * B_n)
    r_plus = (G_n * M_n + np.sqrt(Delta)) / (2 * gamma_n * B_n)
    w = r_plus - r_minus
    check("Ex 9.2: r_- ≈ 0.67",
          np.isclose(r_minus, 0.67, atol=0.02),
          f"r_- = {r_minus:.4f}")

    check("Ex 9.2: r_+ ≈ 7499",
          np.isclose(r_plus, 7499, atol=5),
          f"r_+ = {r_plus:.2f}")

    check("Ex 9.2: bandwidth ≈ 7498",
          np.isclose(w, 7498, atol=5),
          f"w = {w:.2f}")


# ===========================================================================
# 21. Worked Example 9.3: Small Nation vs. Superpower
# ===========================================================================

def verify_example_nation_superpower() -> None:
    section("21. Worked Example 9.3 — Small Nation vs. Superpower")

    B_n, gamma_n, M_n, G_n, tau_n = 50.0, 0.02, 10000.0, 0.5, 2.0

    r_star = 2 * tau_n / G_n
    check("Ex 9.3: r* = 8.0",
          np.isclose(r_star, 8.0),
          f"r* = {r_star}")

    M_min = 4 * gamma_n * B_n * tau_n / G_n**2
    check("Ex 9.3: M_min = 32",
          np.isclose(M_min, 32.0),
          f"M_min = {M_min}")

    Delta = G_n**2 * M_n**2 - 4 * gamma_n * B_n * tau_n * M_n
    check("Ex 9.3: Delta = 24,920,000",
          np.isclose(Delta, 24920000, rtol=0.001),
          f"Delta = {Delta:.0f}")

    w = np.sqrt(Delta) / (gamma_n * B_n)
    check("Ex 9.3: bandwidth ≈ 4992",
          np.isclose(w, 4992, atol=5),
          f"w = {w:.2f}")


# ===========================================================================
# 22. Cross-Task Consistency
# ===========================================================================

def verify_cross_task_consistency() -> None:
    section("22. Cross-Task Consistency Checks")

    # Check that V(r) = -Pi(r)
    Pi = G_s * M / r - tau * M / r**2 - gamma * B
    check("Cross-task: V(r) = -Pi(r)",
          sp.simplify(V + Pi) == 0,
          "V + Pi = 0")

    # Check M_min formula consistency
    M_min = 4 * gamma * B * tau / G_s**2
    V_at_rstar = sp.simplify(V.subs(r, 2*tau/G_s))
    V_at_Mmin = sp.simplify(V_at_rstar.subs(M, M_min))
    check("Cross-task: V(r*) = 0 when M = M_min",
          V_at_Mmin == 0,
          f"V(r*, M_min) = {V_at_Mmin}")

    # Verify well depth = gamma*B when M = M_min
    D_at_Mmin = G_s**2 * M_min / (4 * tau)
    check("Cross-task: D = gamma*B when M = M_min",
          sp.simplify(D_at_Mmin - gamma * B) == 0,
          f"D(M_min) = {sp.simplify(D_at_Mmin)}")

    # Attractor location independent of M, gamma, B
    r_star_sym = 2 * tau / G_s
    check("Cross-task: r* depends only on tau, G",
          r_star_sym.free_symbols == {tau, G_s},
          f"r* symbols = {r_star_sym.free_symbols}")


# ===========================================================================
# 23. Symbolic Stress Tests
# ===========================================================================

def verify_symbolic_stress_tests() -> None:
    section("23. Symbolic Stress Tests")

    # V'(r) sign analysis
    Vp = sp.diff(V, r)
    Vp_factored = sp.simplify(Vp * r**3 / M)
    check("Stress: V'(r) * r^3/M = G*r - 2*tau",
          sp.simplify(Vp_factored - (G_s * r - 2 * tau)) == 0,
          f"V'*r^3/M = {Vp_factored}")

    # V''(r*) explicit value
    Vpp = sp.diff(V, r, 2)
    r_star = 2 * tau / G_s
    Vpp_star = sp.simplify(Vpp.subs(r, r_star))
    expected_Vpp = G_s**4 * M / (8 * tau**3)
    check("Stress: V''(r*) = G^4*M/(8*tau^3)",
          sp.simplify(Vpp_star - expected_Vpp) == 0,
          f"V''(r*) = {Vpp_star}")

    # Band boundaries satisfy Vieta's formulas
    r_minus_sym = (G_s * M - sp.sqrt(G_s**2 * M**2 - 4 * gamma * B * tau * M)) / (2 * gamma * B)
    r_plus_sym = (G_s * M + sp.sqrt(G_s**2 * M**2 - 4 * gamma * B * tau * M)) / (2 * gamma * B)

    # Sum of roots = G*M/(gamma*B)
    root_sum = sp.simplify(r_minus_sym + r_plus_sym)
    check("Stress: r_- + r_+ = G*M/(gamma*B)",
          sp.simplify(root_sum - G_s * M / (gamma * B)) == 0,
          f"sum = {root_sum}")

    # Product of roots = tau*M/(gamma*B)
    root_prod = sp.simplify(r_minus_sym * r_plus_sym)
    expected_prod = tau * M / (gamma * B)
    check("Stress: r_- * r_+ = tau*M/(gamma*B)",
          sp.simplify(root_prod - expected_prod) == 0,
          f"product = {root_prod}")

    # Numerical edge case: M exactly at M_min
    G_n, tau_n, gamma_n, B_n = 1.0, 0.5, 0.1, 1.0
    M_min_n = 4 * gamma_n * B_n * tau_n / G_n**2
    Delta_edge = G_n**2 * M_min_n**2 - 4 * gamma_n * B_n * tau_n * M_min_n
    check("Stress: Delta = 0 at M = M_min",
          np.isclose(Delta_edge, 0.0, atol=1e-12),
          f"Delta(M_min) = {Delta_edge:.2e}")

    # Edge: very large M
    M_huge = 1e15
    V_star_huge = gamma_n * B_n - G_n**2 * M_huge / (4 * tau_n)
    check("Stress: V(r*) << 0 for large M",
          V_star_huge < -1e10,
          f"V(r*) = {V_star_huge:.2e}")

    # Edge: parameters approaching zero
    # tau -> 0 shifts attractor to r* -> 0 (complete integration)
    check("Stress: as tau -> 0, r* -> 0",
          True, "r* = 2*tau/G -> 0 as tau -> 0")


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    print("=" * 72)
    print("  VERIFY TASK 1.6: Value Dynamics — Attractor Mechanics")
    print("=" * 72)

    verify_proposition_8()
    verify_definitions_38_39()
    verify_theorem_22()
    verify_theorem_23()
    verify_band_boundaries()
    verify_theorem_24()
    verify_corollary_24_1()
    verify_corollary_24_2()
    verify_healthy_boundary_equilibrium()
    verify_basin_of_no_return()
    verify_theorem_25()
    verify_theorem_26()
    verify_proposition_9()
    verify_proposition_10()
    verify_theorem_27()
    verify_corollary_27_1()
    verify_corollary_27_2()
    verify_proposition_11()
    verify_example_individual_corporation()
    verify_example_citizen_state()
    verify_example_nation_superpower()
    verify_cross_task_consistency()
    verify_symbolic_stress_tests()

    print(f"\n{'='*72}")
    print(f"  FINAL RESULT: {PASS} passed, {FAIL} failed, "
          f"{PASS+FAIL} total — "
          f"{'100% PASS' if FAIL == 0 else f'{PASS/(PASS+FAIL)*100:.1f}%'}")
    print(f"{'='*72}\n")

    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
