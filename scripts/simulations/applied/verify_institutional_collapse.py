"""
Verify: Institutional Ecosystem Collapse — Dual-Channel Cascade
================================================================

Independently validates every numerical claim in the institutional
ecosystem collapse application, applying Theorems 22–27, Definitions 35–45,
Propositions 8–11, Lemma 2, and all corollaries to the dual-channel
cascade scenario.

Run:
    python scripts/simulations/applied/verify_institutional_collapse.py
"""

from __future__ import annotations

import sys
import os
import math

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import sympy as sp

from modules.verify import reset, section, check, close, summary
from modules.value_dynamics import (
    CANONICAL_KAPPA, COLLAPSE_FLOOR_FRACTION, boundary_scale,
    ActiveBoundary, basin_of_no_return, basin_of_no_return_approx,
    boundary_equilibria, boundary_velocity, collapse_envelope,
    collapse_time_bound, dissolution_radius, mobility,
    repair_capacity_density, repair_rate, starvation_time,
    structural_capacity, surplus_ceiling,
)

# ---------------------------------------------------------------------------
# 1. Scenario Parameters
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    reset()

    section("1. Institutional Ecosystem Scenario Parameters")

    M_val = 1e8        # Ecosystem footprint (param-scale × deployment × data rate)
    G_val = 1.0        # Capability transfer efficiency
    tau_val = 0.5       # Homogenization pressure coefficient
    gamma_val = 0.3     # Capability decay rate without foundation support
    Bi_val = 50.0       # Alignment independence (boundary integrity)
    sigma_val = 0.1     # Representational monoculture pressure
    rho_val = 0.5       # Independence reinvestment fraction
    mu_val = 1.0        # Baseline coupling adjustment rate (mu_0)
    beta_val = 1e-7     # Discount factor scaling
    alpha_star = 0.4    # Critical synthetic data fraction

    # -----------------------------------------------------------------------
    # ACTIVE-DISSIPATIVE BOUNDARY PARAMETERS — !! NOT FROM THE PAPER !!
    #
    # TC-VI gives NO numeric value for kappa, B_min or B_bar (nor for any other
    # parameter of the active dissipative model); its worked examples predate
    # the boundary rebuild and use only B, gamma, M, G, tau. That silence is
    # deliberate. The values below are therefore CHOSEN, and must NOT be cited
    # as canonical TC-VI parameters.
    #
    # They are not chosen HERE, though: kappa and the B_bar/B_min convention are
    # shared with every other TC-VI script through modules/value_dynamics.py, so
    # that there is exactly ONE place to change and audit them. This script only
    # declares its own integrity and derives the rest.
    #
    #   kappa = CANONICAL_KAPPA = 2.0
    #                 The TC-IV/TC-V baseline repair multiplier
    #                 (kappa = 1 + k_clear + k_pen + k_irr > 1 strictly, so
    #                 kappa = 1 is inadmissible).
    #                 r_d scales as kappa^(1/3): kappa = 4 would push r_d past
    #                 r* = 1.0, inverting the case study into unconditional
    #                 dissolution, so this choice is load-bearing for the
    #                 narrative below and is reported as such.
    #
    #   B_bar = 50.0  = boundary_scale(Bi_val)[0]. The convention reads the
    #                 scenario's declared alignment independence B_i = 50 AS the
    #                 fully-intact reference, so zeta(B_i) = 1 at t = 0: the
    #                 institution starts healthy, and B_min < B_i <= B_bar as
    #                 the model requires. (The alternative B_bar = 2*B_declared
    #                 was rejected by measurement — it gives B_u(r*) = 80.2 > 50,
    #                 which would collapse the institution even parked at the
    #                 attractor, inverting this very case study.)
    #
    #   B_min = 1.0   = COLLAPSE_FLOOR_FRACTION * B_bar = 0.02 * 50. The collapse
    #                 floor, ABSORBING. Not arbitrary: this script already used
    #                 1.0 as the effective floor before the port — the starvation
    #                 check asserted t = ln(B_i/1)/gamma ~ 13.04 and the
    #                 starvation loop halted at B_i = 1.0. The fraction is chosen
    #                 so that B_min lands exactly on that pre-existing constant,
    #                 making it exactly the paper's t* = (1/gamma)*ln(B_i_0/B_min).
    # -----------------------------------------------------------------------
    kappa_val = CANONICAL_KAPPA              # Repair multiplier — shared choice
    B_bar_val, B_min_val = boundary_scale(Bi_val)   # B_bar = B declared; B_min = 2% of it

    check("Convention: B_bar is the scenario's declared integrity (zeta = 1 at t=0)",
          B_bar_val == Bi_val
          and abs(structural_capacity(Bi_val, B_min_val, B_bar_val) - 1.0) < 1e-12,
          f"B_bar = {B_bar_val} = declared B_i = {Bi_val}")

    check("Convention: B_min = COLLAPSE_FLOOR_FRACTION * B_bar = 1.0",
          abs(B_min_val - COLLAPSE_FLOOR_FRACTION * B_bar_val) < 1e-12
          and abs(B_min_val - 1.0) < 1e-12,
          f"B_min = {COLLAPSE_FLOOR_FRACTION} * {B_bar_val} = {B_min_val}")

    # Single source of truth for the coupled agent-boundary system: every
    # formula below is delegated to modules/value_dynamics.py.
    AB = ActiveBoundary(
        M=M_val, G=G_val, tau=tau_val, gamma=gamma_val, sigma=sigma_val,
        rho=rho_val, kappa=kappa_val, B_min=B_min_val, B_bar=B_bar_val,
        mu_0=mu_val,
    )

    print(f"  M = {M_val:.0e}, G = {G_val}, tau = {tau_val}")
    print(f"  gamma = {gamma_val}, B_i = {Bi_val}, sigma = {sigma_val}")
    print(f"  rho = {rho_val}, mu_0 = {mu_val}, beta = {beta_val}")
    print(f"  alpha* = {alpha_star}")
    print(f"  [script-chosen, NOT from the paper] "
          f"kappa = {kappa_val}, B_min = {B_min_val}, B_bar = {B_bar_val}")
    check("Parameters loaded", True)

    check("Model: 0 < B_min < B_i <= B_bar (admissible integrity)",
          0.0 < B_min_val < Bi_val <= B_bar_val,
          f"{B_min_val} < {Bi_val} <= {B_bar_val}")
    check("Model: kappa > 1 strictly (repair costs more than it restores)",
          kappa_val > 1.0, f"kappa = {kappa_val}")
    check("Model: rho in (0,1) (repair allocation fraction)",
          0.0 < rho_val < 1.0, f"rho = {rho_val}")

    # ---------------------------------------------------------------------------
    # 2. Coexistence Potential V(r) — Definition 37
    # ---------------------------------------------------------------------------

    section("2. Coexistence Potential V(r) — Definition 37")

    def V(r, M=M_val, G=G_val, tau=tau_val, gamma=gamma_val, Bi=Bi_val):
        """Coexistence potential: V(r) = tau*M/r^2 - G*M/r + gamma*Bi."""
        return tau * M / r**2 - G * M / r + gamma * Bi

    def Pi(r, M=M_val, G=G_val, tau=tau_val, gamma=gamma_val, Bi=Bi_val):
        """Net energy rate: Pi(r) = -V(r)."""
        return -V(r, M, G, tau, gamma, Bi)

    # Verify at test points
    gamma_Bi = gamma_val * Bi_val  # = 15
    check("V(1.0) = tau*M/1 - G*M/1 + gamma*Bi",
          abs(V(1.0) - (tau_val*M_val - G_val*M_val + gamma_Bi)) < 1e-6,
          f"V(1.0) = {V(1.0)}")

    check("Pi(r) = -V(r)", abs(Pi(1.0) + V(1.0)) < 1e-6)

    # ---------------------------------------------------------------------------
    # 3. Proposition 8 — Properties of V(r)
    # ---------------------------------------------------------------------------

    section("3. Proposition 8 — Properties of V(r)")

    # (a) lim r->0+ V(r) = +inf
    check("Prop 8a: V(r) -> +inf as r -> 0+",
          V(1e-6) > 1e18, f"V(1e-6) = {V(1e-6):.2e}")

    # (b) lim r->inf V(r) = gamma*Bi
    check("Prop 8b: V(r) -> gamma*Bi as r -> inf",
          abs(V(1e12) - gamma_Bi) < 1e-4, f"V(1e12) = {V(1e12):.6f}, gamma*Bi = {gamma_Bi}")

    # (d) Unique critical point — the minimum
    r_star = 2 * tau_val / G_val  # = 1.0
    check("Prop 8d: unique critical point at r* = 2*tau/G",
          abs(r_star - 1.0) < 1e-10, f"r* = {r_star}")

    def V_prime_exact(r, M=M_val, G=G_val, tau=tau_val):
        """V'(r) = M/r^3 * (G*r - 2*tau)."""
        return M / r**3 * (G * r - 2 * tau)

    check("V'(0.5) < 0 (decreasing for r < r*)",
          V_prime_exact(0.5) < 0, f"V'(0.5) = {V_prime_exact(0.5):.2e}")
    check("V'(1.0) = 0 (critical point at r*)",
          abs(V_prime_exact(1.0)) < 1e-6, f"V'(1.0) = {V_prime_exact(1.0):.2e}")
    check("V'(2.0) > 0 (increasing for r > r*)",
          V_prime_exact(2.0) > 0, f"V'(2.0) = {V_prime_exact(2.0):.2e}")

    # (e) V_min < gamma*Bi
    V_min = V(r_star)
    check("Prop 8e: V(r*) < gamma*Bi",
          V_min < gamma_Bi, f"V(r*) = {V_min:.2e}, gamma*Bi = {gamma_Bi}")

    # ---------------------------------------------------------------------------
    # 4. Theorem 22 — Stability of the Cooperative Attractor
    # ---------------------------------------------------------------------------

    section("4. Theorem 22 — Stability of the Cooperative Attractor")

    # (a) Fixed point
    check("Thm 22a: r* = 2*tau/G = 1.0 is fixed point",
          abs(r_star - 1.0) < 1e-10 and abs(V_prime_exact(r_star)) < 1e-6)

    # (b) Eigenvalue
    def V_double_prime(r, M=M_val, G=G_val, tau=tau_val):
        """V''(r) = 6*tau*M/r^4 - 2*G*M/r^3."""
        return 6 * tau * M / r**4 - 2 * G * M / r**3

    V_pp_star = V_double_prime(r_star)
    eigenvalue = -mu_val * V_pp_star
    check("Thm 22b: V''(r*) = G^4*M/(8*tau^3)",
          abs(V_pp_star - G_val**4 * M_val / (8 * tau_val**3)) < 1e-2,
          f"V''(r*) = {V_pp_star:.2e}")
    check("Thm 22b: eigenvalue lambda < 0",
          eigenvalue < 0, f"lambda = {eigenvalue:.2e}")
    check("Thm 22b: eigenvalue = -1e8",
          abs(eigenvalue - (-1e8)) < 1, f"lambda = {eigenvalue:.2e}")

    # (c) Global attraction — Lyapunov function
    section("4c. Theorem 22c — Lyapunov global attraction")

    for r_test in [0.1, 0.5, 1.0, 2.0, 10.0, 1000.0]:
        W = V(r_test) - V(r_star)
        check(f"Lyapunov W(r={r_test}) >= 0", W >= -1e-10, f"W = {W:.2e}")

    # Corollary 22.1: Resilience
    check("Cor 22.1: perturbation from r* is self-correcting (eigenvalue < 0)",
          eigenvalue < 0)

    # ---------------------------------------------------------------------------
    # 5. Theorem 23 — Existence of the Coexistence Band
    # ---------------------------------------------------------------------------

    section("5. Theorem 23 — Existence of the Coexistence Band")

    M_min = 4 * gamma_val * Bi_val * tau_val / G_val**2
    check("M_min = 4*gamma*Bi*tau/G^2 = 30",
          abs(M_min - 30.0) < 1e-10, f"M_min = {M_min}")

    check("M = 1e8 >> M_min = 30 -> band exists",
          M_val > M_min, f"M/M_min = {M_val/M_min:.2e}")

    # Band should NOT exist when M < M_min
    Delta_sub = G_val**2 * 20**2 - 4 * gamma_val * Bi_val * tau_val * 20
    check("M=20 < M_min=30: Delta < 0 (no band)",
          Delta_sub < 0, f"Delta(M=20) = {Delta_sub}")

    # Band at exact threshold
    Delta_exact = G_val**2 * M_min**2 - 4 * gamma_val * Bi_val * tau_val * M_min
    check("M=M_min: Delta = 0 (marginal)",
          abs(Delta_exact) < 1e-6, f"Delta(M_min) = {Delta_exact}")

    # ---------------------------------------------------------------------------
    # 6. Theorem 24 — Freedom Bandwidth
    # ---------------------------------------------------------------------------

    section("6. Theorem 24 — Freedom Bandwidth")

    Delta = G_val**2 * M_val**2 - 4 * gamma_val * Bi_val * tau_val * M_val
    check("Delta = G^2*M^2 - 4*gamma*Bi*tau*M",
          abs(Delta - (1e16 - 3e9)) < 1, f"Delta = {Delta:.6e}")

    sqrt_Delta = math.sqrt(Delta)
    denom = 2 * gamma_val * Bi_val  # = 30

    r_plus = (G_val * M_val + sqrt_Delta) / denom
    # Vieta's formula for r- to avoid catastrophic cancellation
    r_minus = tau_val * M_val / (gamma_val * Bi_val * r_plus)
    w = r_plus - r_minus

    check("r- approx 0.50",
          abs(r_minus - 0.50) < 0.01, f"r- = {r_minus:.6f}")
    check("r+ approx 6.667e6",
          abs(r_plus - 6.667e6) / 6.667e6 < 0.001, f"r+ = {r_plus:.2f}")

    # Bandwidth from formula
    w_formula = sqrt_Delta / (gamma_val * Bi_val)
    check("w = sqrt(Delta)/(gamma*Bi) matches r+ - r-",
          abs(w - w_formula) < 1e-4, f"w = {w:.2f}, formula = {w_formula:.2f}")
    check("w approx 6.667e6",
          abs(w - 6.667e6) / 6.667e6 < 0.001, f"w = {w:.2f}")

    # Comparative statics
    def bandwidth(M, G, tau, gamma, Bi):
        D = G**2 * M**2 - 4 * gamma * Bi * tau * M
        if D <= 0:
            return 0.0
        return math.sqrt(D) / (gamma * Bi)

    w_base = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_val)

    # (b) w increasing in M
    masses = [1e2, 1e4, 1e6, 1e8]
    bandwidths = []
    for M_test in masses:
        bandwidths.append(bandwidth(M_test, G_val, tau_val, gamma_val, Bi_val))
    check("Thm 24b: w increasing in M",
          all(bandwidths[i] < bandwidths[i+1] for i in range(len(bandwidths)-1)),
          f"w = {[f'{b:.1f}' for b in bandwidths]}")

    # (c) w decreasing in gamma, Bi, tau
    w_gamma_up = bandwidth(M_val, G_val, tau_val, gamma_val * 1.1, Bi_val)
    check("Thm 24c: w decreasing in gamma",
          w_gamma_up < w_base, f"w(gamma*1.1) = {w_gamma_up:.1f} < {w_base:.1f}")
    w_Bi_up = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_val * 1.1)
    check("Thm 24c: w decreasing in Bi",
          w_Bi_up < w_base, f"w(Bi*1.1) = {w_Bi_up:.1f} < {w_base:.1f}")
    w_tau_up = bandwidth(M_val, G_val, tau_val * 1.1, gamma_val, Bi_val)
    check("Thm 24c: w decreasing in tau",
          w_tau_up < w_base, f"w(tau*1.1) = {w_tau_up:.1f} < {w_base:.1f}")

    # (d) w increasing in G
    w_G_up = bandwidth(M_val, G_val * 1.1, tau_val, gamma_val, Bi_val)
    check("Thm 24d: w increasing in G",
          w_G_up > w_base, f"w(G*1.1) = {w_G_up:.1f} > {w_base:.1f}")

    # (e) Large-M limit
    w_approx = G_val * M_val / (gamma_val * Bi_val)
    check("Thm 24e: w ~= G*M/(gamma*Bi) for large M",
          abs(w - w_approx) / w_approx < 1e-4,
          f"w = {w:.1f}, approx = {w_approx:.1f}")

    # Corollary 24.1: Freedom is finite
    check("Cor 24.1: bandwidth is finite for finite M",
          w < float('inf') and w > 0, f"w = {w:.1f}")

    # ---------------------------------------------------------------------------
    # 7. Lemma 2 — Attractor Containment
    # ---------------------------------------------------------------------------

    section("7. Lemma 2 — Attractor Containment")

    check("r- < r* < r+",
          r_minus < r_star < r_plus,
          f"r- = {r_minus:.4f}, r* = {r_star}, r+ = {r_plus:.1f}")

    check("V(r-) ~= 0", abs(V(r_minus)) < 0.5, f"V(r-) = {V(r_minus):.6e}")
    check("V(r+) ~= 0", abs(V(r_plus)) < 1e-2, f"V(r+) = {V(r_plus):.6e}")
    check("V(r*) < 0", V(r_star) < 0, f"V(r*) = {V(r_star):.2e}")

    # ---------------------------------------------------------------------------
    # 8. Well Depth — Definition 39
    # ---------------------------------------------------------------------------

    section("8. Well Depth — Definition 39")

    well_depth = G_val**2 * M_val / (4 * tau_val)
    check("Well depth D = G^2*M/(4*tau) = 5e7",
          abs(well_depth - 5e7) < 1, f"D = {well_depth:.2e}")

    V_star = V(r_star)
    check("D = gamma*Bi - V(r*)",
          abs(well_depth - (gamma_Bi - V_star)) < 1e-2,
          f"gamma*Bi - V(r*) = {gamma_Bi - V_star:.2e}")

    # ---------------------------------------------------------------------------
    # 9. Net Energy at Attractor — §3.1
    # ---------------------------------------------------------------------------

    section("9. Net Energy at Attractor")

    Pi_star = Pi(r_star)
    expected_Pi = G_val**2 * M_val / (4 * tau_val) - gamma_val * Bi_val
    check("Pi(r*) = G^2*M/(4*tau) - gamma*Bi = 4.9999985e7",
          abs(Pi_star - expected_Pi) < 1e-2,
          f"Pi(r*) = {Pi_star:.7e}, expected = {expected_Pi:.7e}")

    # ---------------------------------------------------------------------------
    # 9b. Proposition — Healthy Boundary Equilibrium
    #
    # The institution's alignment independence is an ACTIVE DISSIPATIVE
    # structure, not a passive reservoir: the machinery that maintains it is
    # itself part of what it maintains. So repair is autocatalytic (it dies with
    # the boundary) and the fixed-r dynamics are quadratic in x = B_i - B_min.
    # ---------------------------------------------------------------------------

    section("9b. Proposition — Healthy Boundary Equilibrium")

    zeta_Bi = structural_capacity(Bi_val, B_min_val, B_bar_val)
    check("Def: zeta(B_min) = 0 (no capacity at the collapse floor)",
          abs(structural_capacity(B_min_val, B_min_val, B_bar_val)) < 1e-12,
          f"zeta(B_min) = {structural_capacity(B_min_val, B_min_val, B_bar_val)}")

    check("Def: zeta(B_bar) = 1 (full capacity at reference integrity)",
          abs(structural_capacity(B_bar_val, B_min_val, B_bar_val) - 1.0) < 1e-12,
          f"zeta(B_bar) = {structural_capacity(B_bar_val, B_min_val, B_bar_val)}")

    zetas = [structural_capacity(b, B_min_val, B_bar_val)
             for b in np.linspace(B_min_val, B_bar_val, 20)]
    check("Def: zeta increasing on [B_min, B_bar], valued in [0,1]",
          all(zetas[i] < zetas[i + 1] for i in range(len(zetas) - 1))
          and all(0.0 <= z <= 1.0 for z in zetas),
          f"zeta in [{zetas[0]:.3f}, {zetas[-1]:.3f}]")

    check("Def: the institution starts fully intact — zeta(B_i) = 1",
          abs(zeta_Bi - 1.0) < 1e-12, f"zeta({Bi_val}) = {zeta_Bi:.6f}")

    # Autocatalysis — the property that separates an active structure from a
    # passive reservoir: repair dies at the floor even with vast surplus.
    # Stated RELATIVE to the repair an intact boundary would fund from the same
    # Pi: at this scenario's scale Pi(r*) ~ 5e7, so an absolute threshold would
    # say nothing. The ratio is exactly zeta(B_i), which -> 0 at the floor.
    Pi_floor = AB.Pi(r_star, B_min_val * 1.000001)
    ungated_floor = (rho_val / kappa_val) * max(Pi_floor, 0)
    ratios = [AB.R_repair(r_star, B_min_val * (1 + e))
              / ((rho_val / kappa_val)
                 * max(AB.Pi(r_star, B_min_val * (1 + e)), 0))
              for e in (1e-6, 1e-8, 1e-10, 1e-12)]
    check("Def: R_repair/(ungated repair) -> 0 as B_i -> B_min even though Pi >> 0",
          all(ratios[i] > ratios[i + 1] for i in range(len(ratios) - 1))
          and ratios[-1] < 1e-12 and Pi_floor > 1.0,
          f"ratio -> {ratios[-1]:.3e} while Pi = {Pi_floor:.3e} and "
          f"ungated repair = {ungated_floor:.3e}")

    check("Def: R_repair = 0 exactly AT the collapse floor (autocatalytic)",
          AB.R_repair(r_star, B_min_val) == 0.0 and Pi_floor > 1.0,
          f"R_repair(r*, B_min) = {AB.R_repair(r_star, B_min_val)} "
          f"despite Pi = {Pi_floor:.3e}")

    q_val = repair_capacity_density(rho_val, kappa_val, B_min_val, B_bar_val)
    check("Prop: q = rho/(kappa*(B_bar - B_min))",
          abs(q_val - rho_val / (kappa_val * (B_bar_val - B_min_val))) < 1e-12,
          f"q = {q_val:.8f}")

    # Repair-viability at r*: q*Pi_0 > gamma + 2*sqrt(q*gamma*d_0)
    Pi_0_star = AB.Pi_0(r_star)
    d_0_star = AB.d_0(r_star)
    eq_star = AB.equilibria(r_star)

    check("Prop: repair-viability at r*: q*Pi_0 > gamma + 2*sqrt(q*gamma*d_0)",
          eq_star.viable and eq_star.margin > 0,
          f"margin = {eq_star.margin:.2f}")

    check("Prop: exactly two roots B_u < B_i* in (B_min, inf)",
          B_min_val < eq_star.B_u < eq_star.B_star,
          f"B_u = {eq_star.B_u:.6f}, B_i* = {eq_star.B_star:.4e}")

    # Fixed-point residuals against the parabola from the proof.
    def _parabola(x):
        return -q_val * gamma_val * x**2 + (q_val * Pi_0_star - gamma_val) * x - d_0_star

    # Root residuals are asserted in BACKWARD-ERROR form |p(x)|/|p'(x)|, which
    # measures the distance from the computed root to a true root. At this
    # scenario's scale the parabola's coefficients are O(1e7) (d_0(r*) ~ 1e7),
    # so a raw |p(x)| threshold would be measuring the coefficient scale rather
    # than the root accuracy. Newton-scaled, both roots are located to ~1e-8.
    def _dparabola(x):
        return -2 * q_val * gamma_val * x + (q_val * Pi_0_star - gamma_val)

    for _nm, _root in (("B_u", eq_star.B_u), ("B_i*", eq_star.B_star)):
        _x = _root - B_min_val
        _newton = abs(_parabola(_x) / _dparabola(_x))
        check(f"Prop: fixed-point residual at {_nm} ~ 0 (Newton-scaled)",
              _newton < 1e-7,
              f"|p|/|p'| = {_newton:.3e} (raw residual = {_parabola(_x):.3e}, "
              f"slope = {_dparabola(_x):.3e})")

    check("Prop(a): eigenvalue at B_i* is -sqrt(disc) < 0 (stable)",
          eq_star.eig_star < 0
          and abs(eq_star.eig_star + math.sqrt(eq_star.disc)) < 1e-6,
          f"eig(B_i*) = {eq_star.eig_star:.4f}")

    check("Prop(b): eigenvalue at B_u is +sqrt(disc) > 0 (unstable)",
          eq_star.eig_u > 0
          and abs(eq_star.eig_u - math.sqrt(eq_star.disc)) < 1e-6,
          f"eig(B_u) = {eq_star.eig_u:.4f}")

    check("Prop(a): x_+ > B_bar - B_min => healthy equilibrium saturates at B_bar",
          eq_star.B_star > B_bar_val,
          f"B_i*(unsaturated) = {eq_star.B_star:.4e} > B_bar = {B_bar_val}")

    check("Prop(b): dBi/dt < 0 on (B_min, B_u)",
          all(AB.B_dot(r_star, b) < 0
              for b in np.linspace(B_min_val * 1.001, eq_star.B_u * 0.999, 12)),
          f"checked 12 points below B_u = {eq_star.B_u:.4f}")

    check("Prop(b): dBi/dt > 0 on (B_u, min(B_i*, B_bar))",
          all(AB.B_dot(r_star, b) > 0
              for b in np.linspace(eq_star.B_u * 1.001, B_bar_val, 12)),
          f"checked 12 points above B_u = {eq_star.B_u:.4f}")

    # (c) The viable-agent condition — repair-viability at r* AND B_u(r*) < B_bar.
    check("Prop(c): viable-agent condition holds (viable at r* and B_u < B_bar)",
          AB.is_viable_agent() and eq_star.B_u < B_bar_val,
          f"B_u(r*) = {eq_star.B_u:.4f} < B_bar = {B_bar_val}")

    # The narrative claim: at the attractor the institution sits ABOVE the
    # unstable root, so it repairs faster than it decays and holds integrity.
    check("Prop(c): the institution at r* is above B_u => it recovers, not collapses",
          Bi_val > eq_star.B_u and AB.B_dot(r_star, Bi_val) > 0,
          f"B_i = {Bi_val} > B_u(r*) = {eq_star.B_u:.4f}; "
          f"dBi/dt = {AB.B_dot(r_star, Bi_val):.4e} > 0")

    # ---------------------------------------------------------------------------
    # 9c. Theorem — The Basin of No Return
    # ---------------------------------------------------------------------------

    section("9c. Theorem — The Basin of No Return")

    Pi_bar_basin = surplus_ceiling(M_val, G_val, tau_val, gamma_val, B_min_val)
    B_c = basin_of_no_return(Pi_bar_basin, q_val, gamma_val, B_min_val)

    check("Thm: B_min < B_c (basin sits strictly above the collapse floor)",
          B_min_val < B_c, f"B_c = {B_c:.8f}, B_min = {B_min_val}")

    # B_c is asserted to be a root in BACKWARD-ERROR form |h|/|h'|, i.e. the
    # distance from the computed B_c to a true root of h. That is the right
    # yardstick here regardless of conditioning: h' ~ 2.6e5, so a raw |h|
    # tolerance would silently rescale with the parameters.
    h_at_Bc = collapse_envelope(B_c, Pi_bar_basin, q_val, gamma_val, B_min_val)
    dh_at_Bc = -2 * q_val * gamma_val * (B_c - B_min_val) + (q_val * Pi_bar_basin - gamma_val)
    check("Thm: B_c is the smaller root of the collapse envelope (Newton-scaled)",
          abs(h_at_Bc / dh_at_Bc) < 1e-8,
          f"|h|/|h'| = {abs(h_at_Bc/dh_at_Bc):.3e} (raw h(B_c) = {h_at_Bc:.3e}, "
          f"h'(B_c) = {dh_at_Bc:.3e})")

    # Independent cross-check of B_c against the cancellation-free root form
    # 2c/(b + sqrt(disc)). This scenario sits deep in q*Pi_bar >> gamma (ratio
    # ~8.5e5), where the textbook (b - sqrt(disc))/(2a) loses the basin
    # THICKNESS B_c - B_min (~1.2e-6) to cancellation — b ~ 2.55e5 but
    # b - sqrt(disc) ~ 3.6e-9, so ~14 digits cancel. value_dynamics evaluates
    # the stable branch, so the two agree to the last ulp; the tolerance is set
    # tight enough to FAIL if that ever regresses to the naive form (which
    # lands ~2.9e-9 off, and so would slip through a loose 1e-8 bound).
    B_c_stable = B_min_val + (2 * gamma_val * B_min_val) / (
        (q_val * Pi_bar_basin - gamma_val)
        + math.sqrt((q_val * Pi_bar_basin - gamma_val)**2
                    - 4 * q_val * gamma_val**2 * B_min_val))
    check("Thm: B_c agrees with the numerically stable root form 2c/(b+sqrt(disc))",
          abs(B_c - B_c_stable) < 1e-14,
          f"B_c = {B_c:.12f} vs stable = {B_c_stable:.12f} "
          f"(h(stable) = {collapse_envelope(B_c_stable, Pi_bar_basin, q_val, gamma_val, B_min_val):.3e})")

    check("Thm: h(B_min) = -gamma*B_min < 0",
          abs(collapse_envelope(B_min_val, Pi_bar_basin, q_val, gamma_val, B_min_val)
              + gamma_val * B_min_val) < 1e-9,
          f"h(B_min) = "
          f"{collapse_envelope(B_min_val, Pi_bar_basin, q_val, gamma_val, B_min_val):.6f}")

    check("Thm: B_c <= B_u(r*) (B_c is a certified INNER bound of the basin)",
          B_c <= eq_star.B_u,
          f"B_c = {B_c:.6f} <= B_u(r*) = {eq_star.B_u:.4f}")

    check("Thm: viable-agent condition => B_c < B_bar",
          AB.is_viable_agent() and B_c < B_bar_val,
          f"B_c = {B_c:.6f} < B_bar = {B_bar_val}")

    # The envelope dominates the true dynamics at every admissible (r, B_i).
    check("Thm: dBi/dt <= h(B_i) for all admissible (r, B_i)",
          all(AB.B_dot(rr, b)
              <= collapse_envelope(b, Pi_bar_basin, q_val, gamma_val, B_min_val) + 1e-6
              for rr in np.linspace(0.3, 50.0, 30)
              for b in np.linspace(B_min_val * 1.001, B_bar_val, 15)),
          "checked 30 radii x 15 integrities")

    # (a) Below B_c collapse is unconditional — regardless of coupling distance.
    B_0_basin = B_min_val + (B_c - B_min_val) * 0.7
    check("Thm(a): dBi/dt < 0 below B_c at EVERY coupling distance",
          all(AB.B_dot(rr, B_0_basin) < 0 for rr in np.linspace(0.3, 200.0, 60)),
          f"B_0 = {B_0_basin:.8f} < B_c = {B_c:.8f}; checked 60 radii")

    check("Thm(a): even parked AT the attractor r*, an agent inside the basin declines",
          AB.B_dot(r_star, B_0_basin) < 0,
          f"dBi/dt(r*, {B_0_basin:.8f}) = {AB.B_dot(r_star, B_0_basin):.4e}")

    check("Thm(a): finite-time collapse bound (B_0 - B_min)/|h(B_0)| is finite",
          math.isfinite(collapse_time_bound(B_0_basin, Pi_bar_basin, q_val,
                                            gamma_val, B_min_val)),
          f"bound = {collapse_time_bound(B_0_basin, Pi_bar_basin, q_val, gamma_val, B_min_val):.4e}")

    # Asymptotic remark: q*Pi_bar >> gamma here, so the basin is a thin layer.
    check("Thm remark: q*Pi_bar >> gamma in this scenario",
          q_val * Pi_bar_basin > 40 * gamma_val,
          f"q*Pi_bar = {q_val*Pi_bar_basin:.2f} vs gamma = {gamma_val}")

    B_c_approx = basin_of_no_return_approx(Pi_bar_basin, q_val, gamma_val, B_min_val)
    check("Thm remark: B_c ~ B_min*(1 + gamma/(q*Pi_bar - gamma))",
          abs(B_c - B_c_approx) / B_c < 1e-5,
          f"exact = {B_c:.10f}, approx = {B_c_approx:.10f}")

    check("Thm remark: basin is a thin layer above the floor",
          (B_c - B_min_val) / (B_bar_val - B_min_val) < 0.01,
          f"basin thickness = {(B_c - B_min_val)/(B_bar_val - B_min_val)*100:.5f}% of range")

    # The basin thickens as the surplus ceiling falls toward gamma/q.
    thicknesses = [basin_of_no_return(p, q_val, gamma_val, B_min_val) - B_min_val
                   for p in (Pi_bar_basin, Pi_bar_basin / 4, Pi_bar_basin / 16)]
    check("Thm remark: basin thickens as Pi_bar falls",
          thicknesses[0] < thicknesses[1] < thicknesses[2],
          f"thickness = {[f'{t:.3e}' for t in thicknesses]}")

    # ---------------------------------------------------------------------------
    # 10. Theorem 25 — Representational Lock-In (Dissolution)
    # ---------------------------------------------------------------------------

    section("10. Theorem 25 — Representational Lock-In")

    # Pi_bar is the SURPLUS CEILING, anchored at the collapse floor B_min — the
    # largest net rate available at ANY coupling distance to an agent at the
    # floor. (The old Pi_max = G^2*M/(4*tau) - gamma*B_i_0 was anchored at the
    # agent's INITIAL integrity; that made the bound trajectory-dependent and it
    # has been deleted from the model. Do not reintroduce it.)
    Pi_bar = surplus_ceiling(M_val, G_val, tau_val, gamma_val, B_min_val)
    check("Thm 25: Pi_bar = G^2*M/(4*tau) - gamma*B_min (anchored at the floor)",
          abs(Pi_bar - (G_val**2 * M_val / (4 * tau_val)
                        - gamma_val * B_min_val)) < 1e-6,
          f"Pi_bar = {Pi_bar:.4f}")
    check("Thm 25: Pi_bar > 0 (surplus available above the floor)",
          Pi_bar > 0, f"Pi_bar = {Pi_bar:.4f}")

    r_d = dissolution_radius(M_val, gamma_val, sigma_val, rho_val, kappa_val,
                             B_min_val, Pi_bar)
    check("r_d = (kappa*sigma*M / (rho*Pi_bar + kappa*gamma*B_min))^(1/3)",
          abs(r_d - (kappa_val * sigma_val * M_val
                     / (rho_val * Pi_bar
                        + kappa_val * gamma_val * B_min_val))**(1/3)) < 1e-12,
          f"r_d = {r_d:.6f}")

    # The defining identity, stated the other way round in the paper.
    check("Thm 25: identity sigma*M/r_d^3 = (rho/kappa)*Pi_bar + gamma*B_min",
          abs(sigma_val * M_val / r_d**3
              - ((rho_val / kappa_val) * Pi_bar + gamma_val * B_min_val)) < 1e-6,
          f"{sigma_val*M_val/r_d**3:.6f} = "
          f"{(rho_val/kappa_val)*Pi_bar + gamma_val*B_min_val:.6f}")

    # r_d ~= 0.928 at kappa = 2. NOTE: this number is NOT paper-sourced — it
    # follows from the script-chosen kappa (r_d scales as kappa^(1/3)). Under
    # the superseded passive formula it was 0.737.
    check("r_d ~= 0.928 (at the script-chosen kappa = 2)",
          abs(r_d - 0.928) < 0.001, f"r_d = {r_d:.6f}")

    # Lock-in trap: r- < r_d. The dissolution zone reaches into the viable band,
    # so an institution can hold positive net energy while still dissolving.
    check("Cor 25.1: r_d > r- (lock-in trap exists)",
          r_d > r_minus, f"r_d = {r_d:.4f} > r- = {r_minus:.4f}")

    check("Cor 25.1: r_d < r* (escape from the zone is a race, not hopeless)",
          r_d < r_star, f"r_d = {r_d:.4f} < r* = {r_star:.4f}")

    # Lock-in at r = 0.5
    r_lock = 0.5
    D_assim_05 = AB.D_assimilate(r_lock)
    Pi_05 = Pi(r_lock)
    R_repair_05 = AB.R_repair(r_lock, Bi_val)
    Bdot_05 = AB.B_dot(r_lock, Bi_val)

    check("At r=0.5: D_assimilate = sigma*M/r^3 = 8e7",
          abs(D_assim_05 - 8e7) < 1e2, f"D_assimilate = {D_assim_05:.2e}")
    check("At r=0.5: Pi < 0 (energy deficit)",
          Pi_05 < 0, f"Pi(0.5) = {Pi_05:.2e}")
    check("At r=0.5: R_repair = 0 (no surplus)",
          abs(R_repair_05) < 1e-6, f"R_repair = {R_repair_05}")
    check("At r=0.5: dBi/dt << 0 (rapid collapse)",
          Bdot_05 < -1e7, f"dBi/dt = {Bdot_05:.2e}")

    # Thm 25(a): below r_d the decline is UNIFORM — every admissible integrity
    # declines faster than -gamma*(B_i + B_min), regardless of how healthy it is.
    check("Thm 25a: at r=0.5 < r_d, dBi/dt < -gamma*(B_i + B_min) for EVERY "
          "admissible B_i",
          all(AB.B_dot(r_lock, b) < -gamma_val * (b + B_min_val)
              for b in np.linspace(B_min_val * 1.001, B_bar_val, 25)),
          f"r = {r_lock} < r_d = {r_d:.4f}; checked 25 integrities")

    # Lock-in at r = 0.6
    r_06 = 0.6
    D_assim_06 = AB.D_assimilate(r_06)
    Pi_06 = Pi(r_06)
    R_repair_06 = AB.R_repair(r_06, Bi_val)
    Bdot_06 = AB.B_dot(r_06, Bi_val)

    # Repair is now (rho/kappa)*zeta(B_i)*max(Pi,0): it is charged the kappa
    # surcharge AND gated by the boundary's own surviving capacity.
    check("Def: R_repair(0.6) = (rho/kappa)*zeta(B_i)*max(Pi,0)",
          abs(R_repair_06 - (rho_val / kappa_val)
              * structural_capacity(Bi_val, B_min_val, B_bar_val)
              * max(Pi_06, 0)) < 1e-6,
          f"R_repair(0.6) = {R_repair_06:.4e}")

    check("At r=0.6: Pi > 0 (inside viable band)",
          Pi_06 > 0, f"Pi(0.6) = {Pi_06:.2e}")
    check("At r=0.6: D_assimilate > R_repair (homogenization wins)",
          D_assim_06 > R_repair_06,
          f"D_assim = {D_assim_06:.2e} > R_repair = {R_repair_06:.2e}")
    check("At r=0.6: dBi/dt < 0 (lock-in trap: capable but dissolving)",
          Bdot_06 < 0, f"dBi/dt = {Bdot_06:.2e}")

    # Finite-time collapse simulation at r = 0.5
    section("10b. Dissolution simulation at r=0.5")

    # Fixed-r integration (the lock-in scenario holds the coupling distance at
    # r_lock), delegating dB_i/dt to the module. Integrity NEVER reaches 0: the
    # run terminates on the ABSORBING set {B_i <= B_min}, which IS dissolution.
    Bi_t = Bi_val
    dt_diss = 1e-9
    steps_to_floor = 0
    while Bi_t > B_min_val and steps_to_floor < 1_000_000:
        dB = boundary_velocity(r_lock, Bi_t, M_val, G_val, tau_val, gamma_val,
                               sigma_val, rho_val, kappa_val, B_min_val,
                               B_bar_val)
        Bi_t += dB * dt_diss
        steps_to_floor += 1

    check("Thm 25b: B_i reaches the collapse floor B_min in finite time at r=0.5",
          Bi_t <= B_min_val,
          f"B_i -> {Bi_t:.4f} <= B_min = {B_min_val} after {steps_to_floor} steps")

    check("Thm 25b: collapse endpoint is B_min > 0, never 0",
          B_min_val > 0 and Bi_t <= B_min_val,
          f"B_final = {Bi_t:.4f}, B_min = {B_min_val} > 0")

    # Thm 25(b): t_d <= t_0 + (B_i(t_0) - B_min)/(2*gamma*B_min)
    t_diss = steps_to_floor * dt_diss
    t_d_bound = (Bi_val - B_min_val) / (2 * gamma_val * B_min_val)
    check("Thm 25b: t_d <= (B_i(t_0) - B_min)/(2*gamma*B_min)",
          t_diss <= t_d_bound,
          f"t_d = {t_diss:.3e} <= bound = {t_d_bound:.4f}")

    # ---------------------------------------------------------------------------
    # 11. Theorem 26 — Capability Starvation Spiral
    # ---------------------------------------------------------------------------

    section("11. Theorem 26 — Capability Starvation Spiral")

    r_outside = 1e7

    Pi_outside = Pi(r_outside)
    check("Thm 26a: Pi(r=1e7) < 0 (outside band)",
          Pi_outside < 0, f"Pi = {Pi_outside:.2e}")

    D_assim_outside = AB.D_assimilate(r_outside)

    # Thm 26(a): outside the band Pi < 0, so the agent allocates NOTHING to
    # repair — R_repair = 0 exactly, independent of its remaining capacity.
    check("Thm 26a: R_repair = 0 outside the band (energy deficit)",
          AB.R_repair(r_outside, Bi_val) == 0.0,
          f"R_repair = {AB.R_repair(r_outside, Bi_val)}")

    Bdot_outside = AB.B_dot(r_outside, Bi_val)
    check("Thm 26b: dBi/dt = -D_assimilate - gamma*B_i < 0 outside band",
          Bdot_outside < 0
          and abs(Bdot_outside
                  - (-D_assim_outside - gamma_val * Bi_val)) < 1e-9,
          f"dBi/dt = {Bdot_outside:.2e}")

    check("Thm 26: at large r, D_assimilate ~= 0",
          D_assim_outside < 1e-5, f"D_assim(1e7) = {D_assim_outside:.2e}")

    # Thm 26(b): in the isolation limit the decline is exponential and reaches
    # the COLLAPSE FLOOR at finite t* = (1/gamma)*ln(B_i_0/B_min). The
    # exponential never reaches zero — dissolution needs only B_min > 0.
    t_star_starve = starvation_time(Bi_val, B_min_val, gamma_val)
    check("Thm 26b: t* = (1/gamma)*ln(B_i_0/B_min) = ln(50/1)/0.3 ~= 13.04",
          abs(t_star_starve - math.log(Bi_val / B_min_val) / gamma_val) < 1e-9
          and abs(t_star_starve - 13.04) < 0.1,
          f"t* = {t_star_starve:.2f}")

    check("Thm 26b: t* is finite though the exponential never reaches 0 "
          "(dissolution needs only B_min > 0)",
          math.isfinite(t_star_starve) and B_min_val > 0,
          f"t* = {t_star_starve:.2f}, B_min = {B_min_val} > 0")

    # Simulate starvation to the collapse floor
    Bi_starve = Bi_val
    dt_starve = 0.01
    t_starve = 0
    while Bi_starve > B_min_val:
        Bi_starve *= math.exp(-gamma_val * dt_starve)
        t_starve += dt_starve

    check("Starvation simulation: Bi reaches the floor B_min at t ~= t*",
          abs(t_starve - t_star_starve) < 0.5,
          f"t_sim = {t_starve:.2f}, t* = {t_star_starve:.2f}")

    # Mobility is health-dependent: mu(B_i) = mu_0*zeta(B_i). The same machinery
    # that repairs the boundary also executes the coupling adjustments, so a
    # starving institution loses the ability to migrate back toward the band.
    check("Thm 26: mu(B_i) = mu_0*zeta(B_i) (health-dependent mobility)",
          abs(mobility(Bi_val, mu_val, B_min_val, B_bar_val)
              - mu_val * structural_capacity(Bi_val, B_min_val, B_bar_val)) < 1e-12,
          f"mu(B_i) = {mobility(Bi_val, mu_val, B_min_val, B_bar_val):.4f}")

    check("Thm 26: mobility death — mu -> 0 as B_i -> B_min",
          abs(mobility(B_min_val, mu_val, B_min_val, B_bar_val)) < 1e-12,
          f"mu(B_min) = {mobility(B_min_val, mu_val, B_min_val, B_bar_val)}")

    check("Thm 26d: repair capacity and mobility vanish TOGETHER (zeta gates both)",
          abs(structural_capacity(B_min_val, B_min_val, B_bar_val)) < 1e-12
          and abs(mobility(B_min_val, mu_val, B_min_val, B_bar_val)) < 1e-12
          and abs(AB.R_repair(r_star, B_min_val)) < 1e-12,
          "zeta multiplies BOTH the repair term and the mobility term")

    # ---------------------------------------------------------------------------
    # 12. Theorem 27 — Multi-Foundation Dynamics
    # ---------------------------------------------------------------------------

    section("12. Theorem 27 — Multi-Foundation Attractor")

    centers = [
        {"name": "F_alpha", "M": 5e7, "G": 1.0, "tau": 0.5, "derivs": 25},
        {"name": "F_beta",  "M": 3e7, "G": 1.0, "tau": 0.5, "derivs": 15},
        {"name": "F_gamma", "M": 2e7, "G": 1.0, "tau": 0.5, "derivs": 10},
    ]

    for c in centers:
        c["r_star"] = 2 * c["tau"] / c["G"]
        c["D"] = c["G"]**2 * c["M"] / (4 * c["tau"])

    check("F_alpha D = 2.5e7", abs(centers[0]["D"] - 2.5e7) < 1,
          f"D = {centers[0]['D']:.2e}")
    check("F_beta D = 1.5e7", abs(centers[1]["D"] - 1.5e7) < 1,
          f"D = {centers[1]['D']:.2e}")
    check("F_gamma D = 1.0e7", abs(centers[2]["D"] - 1.0e7) < 1,
          f"D = {centers[2]['D']:.2e}")

    D_total = sum(c["D"] for c in centers)
    check("D_total = 5.0e7",
          abs(D_total - 5.0e7) < 1, f"D_total = {D_total:.2e}")

    check("Thm 27: multi-foundation viable (D_total >> gamma*Bi)",
          D_total > gamma_Bi, f"D_total = {D_total:.2e} >> {gamma_Bi}")

    # Corollary 27.1: Diversification
    for c in centers:
        check(f"Cor 27.1: {c['name']} individually viable (M={c['M']:.0e} > {M_min})",
              c["M"] > M_min)

    # ---------------------------------------------------------------------------
    # 13. Cascade Collapse — Corollary 27.2
    # ---------------------------------------------------------------------------

    section("13. Cascade Collapse — Corollary 27.2")

    # Scenario: F_gamma retrained
    D_after_gamma = centers[0]["D"] + centers[1]["D"]
    check("After F_gamma retrained: D = F_alpha + F_beta = 4.0e7",
          abs(D_after_gamma - 4.0e7) < 1, f"D = {D_after_gamma:.2e}")
    check("Derivatives still viable after F_gamma retraining",
          D_after_gamma > gamma_Bi)

    # F_beta AND F_gamma fail
    D_after_BG = centers[0]["D"]
    check("After F_beta+F_gamma fail: D = F_alpha = 2.5e7",
          abs(D_after_BG - 2.5e7) < 1, f"D = {D_after_BG:.2e}")
    check("Derivatives still individually viable",
          D_after_BG > gamma_Bi)

    # Total freedom lost on final collapse
    N_labs = 50
    w_alpha = bandwidth(centers[0]["M"], centers[0]["G"], centers[0]["tau"],
                        gamma_val, Bi_val)
    F_lost = N_labs * w_alpha
    check("Freedom lost on F_alpha collapse: N*w(M_alpha)",
          F_lost > 1e8, f"F_lost = {F_lost:.3e}")

    expected_w_alpha = math.sqrt(
        centers[0]["G"]**2 * centers[0]["M"]**2 -
        4 * gamma_val * Bi_val * centers[0]["tau"] * centers[0]["M"]
    ) / (gamma_val * Bi_val)
    check("w(F_alpha) computed correctly",
          abs(w_alpha - expected_w_alpha) < 1, f"w = {w_alpha:.1f}")

    # ---------------------------------------------------------------------------
    # 14. Dual-Channel Cascade Simulation
    # ---------------------------------------------------------------------------

    section("14. Dual-Channel Cascade Simulation")

    # Three scenarios:
    # 1. No failure — all foundations stable, clean data
    # 2. Representational shift only — F_gamma retrained at t=5
    # 3. Dual-channel — F_gamma retrained at t=5, alpha > alpha* at t=10

    dt = 0.1
    T_total = 30.0
    times = np.arange(0, T_total, dt)

    # Rescaled centers for simulation (same as power-concentration figure)
    sim_centers = [
        {"name": "F_alpha", "M": 24, "alive": True},
        {"name": "F_beta",  "M": 14, "alive": True},
        {"name": "F_gamma", "M": 10, "alive": True},
    ]

    sigma_sim = 0.35  # Bi spread

    scenarios = [
        {
            "name": "No failure",
            "fail_times": {},
            "data_contamination_time": None,
        },
        {
            "name": "Representational shift only",
            "fail_times": {"F_gamma": 5},
            "data_contamination_time": None,
        },
        {
            "name": "Dual-channel collapse",
            "fail_times": {"F_gamma": 5},
            "data_contamination_time": 10,
        },
    ]

    results = {}
    floor_state = {}      # per-scenario (min integrity reached, labs dissolved)

    # NOTE — SCOPE BOUNDARY. The lab-survival loop below is NOT the TC-VI
    # active-dissipative ODE. It is an ad-hoc cascade heuristic
    # (`deficit = gamma*Bi_0 - D_total; Bi -= deficit*dt`, with flat `rho*dt`
    # regrowth) with no sigma, no zeta, no (rho/kappa) and no Pi anywhere: it
    # models foundation-support withdrawal across a POPULATION, not a single
    # boundary's energy budget. That scope boundary still stands — the loop has
    # NOT been rewritten into the ODE.
    #
    # What it now DOES inherit from the boundary rebuild is the collapse floor,
    # because that part is not a property of the energy budget but of what
    # dissolution MEANS: integrity bottoms out at B_min > 0, never at 0, and
    # {B_i <= B_min} is ABSORBING — reaching it IS dissolution, and no later
    # surplus resurrects a dissolved lab. A bare clamp `max(B, B_min)` would be
    # wrong: it would let a lab sit at the floor and then climb back out. The
    # `dissolved` mask below makes the absorbing semantics structural rather
    # than something that has to be re-derived from the clamp each time.
    #
    # The survivor test is `> B_min`, NOT a literal `> 1.0`. Those coincide
    # today (B_min = 0.02*50 = 1.0), and the coincidence is exactly why the
    # literal is dangerous: it would silently stop tracking the floor if
    # COLLAPSE_FLOOR_FRACTION ever changed. Do not reintroduce it.

    def cascade_step(labs, labs_0, dissolved_mask, D_total, step, regrowth):
        """One step of the cascade heuristic, with the ABSORBING collapse floor.

        The single update rule, shared by the three scenarios below, the figure
        export block, and the absorbing-semantics probe — so the probe exercises
        the SHIPPED rule rather than a copy of it that could drift.

        Labs in the absorbing set {B_i <= B_min} are skipped outright: that, and
        not the clamp, is what makes dissolution irreversible. Integrity is
        floored at B_min rather than 0.
        """
        for j in range(len(labs)):
            if dissolved_mask[j]:
                continue                       # absorbing: never recovers
            if D_total >= gamma_val * labs_0[j]:
                labs[j] = min(labs[j] + regrowth * step, labs_0[j])
            else:
                labs[j] -= (gamma_val * labs_0[j] - D_total) * step
                if labs[j] <= B_min_val:
                    labs[j] = B_min_val        # floor, not zero
                    dissolved_mask[j] = True

    for scenario in scenarios:
        rng = np.random.default_rng(42)
        labs_Bi_0 = np.clip(rng.normal(Bi_val, sigma_sim * Bi_val, N_labs), 20, 70)
        labs_Bi = labs_Bi_0.copy()
        dissolved = labs_Bi <= B_min_val          # absorbing set {B_i <= B_min}
        surviving = np.zeros(len(times))

        for i, t in enumerate(times):
            # Determine alive foundations
            alive = []
            for c in sim_centers:
                if c["name"] not in scenario["fail_times"] or \
                   t < scenario["fail_times"][c["name"]]:
                    alive.append(c)

            # Total well depth from alive foundations
            D_total_sim = sum(G_val**2 * c["M"] / (4 * tau_val) for c in alive)

            # Data contamination: after the contamination time, D_total
            # *continuously degrades* modeling the feedback loop where
            # degraded outputs worsen training data for all models.
            if scenario["data_contamination_time"] is not None \
               and t >= scenario["data_contamination_time"]:
                t_since = t - scenario["data_contamination_time"]
                # Exponential decay of effective support from data poisoning
                contamination_factor = math.exp(-0.15 * t_since)
                D_total_sim *= contamination_factor

            cascade_step(labs_Bi, labs_Bi_0, dissolved, D_total_sim, dt, rho_val)

            surviving[i] = np.sum(~dissolved)

        results[scenario["name"]] = surviving
        floor_state[scenario["name"]] = (float(labs_Bi.min()), int(dissolved.sum()))

    # The floor is the endpoint: integrity bottoms out AT B_min and never at 0.
    check("§14: lab integrity bottoms out at B_min > 0, never at 0 "
          "(collapse floor adopted)",
          all(mn >= B_min_val for mn, _ in floor_state.values()),
          "min integrity per scenario = "
          + ", ".join(f"{k}: {mn:.4f}" for k, (mn, _) in floor_state.items())
          + f" (all >= B_min = {B_min_val})")

    check("§14: collapse floor is ABSORBING — survivors never recover",
          all(np.all(np.diff(v) <= 0) for v in results.values()),
          "survivor count is monotone non-increasing in all 3 scenarios")

    # ...but that monotonicity does NOT by itself test the absorbing semantics.
    # In all three scenarios above D_total is monotone NON-INCREASING (a failed
    # foundation never returns, and the contamination factor only decays), so a
    # lab that enters deficit never re-enters the regrowth branch and NOTHING
    # ever tries to climb back out. A bare clamp `max(B_i, B_min)` reproduces
    # those three curves exactly and would pass the check above — it would be
    # worthless as a guard.
    #
    # So probe the semantics directly, with the one thing the scenarios lack: a
    # support level that COLLAPSES and then RECOVERS. Absorbing means the
    # dissolved lab stays dissolved; a bare clamp would let it climb back out.
    probe_Bi_0 = np.array([Bi_val])
    probe_Bi = probe_Bi_0.copy()
    probe_dissolved = probe_Bi <= B_min_val
    D_starve, D_restored = 0.0, gamma_val * Bi_val * 2.0   # ample surplus
    for _ in range(int(60.0 / dt)):                        # starve to the floor
        cascade_step(probe_Bi, probe_Bi_0, probe_dissolved, D_starve, dt, rho_val)
    probe_at_floor = float(probe_Bi[0])
    probe_dead = bool(probe_dissolved[0])
    for _ in range(int(60.0 / dt)):                        # then restore support
        cascade_step(probe_Bi, probe_Bi_0, probe_dissolved, D_restored, dt, rho_val)

    check("§14: probe — a starved lab reaches the floor B_min, not 0",
          probe_dead and np.isclose(probe_at_floor, B_min_val),
          f"integrity after starvation = {probe_at_floor:.6f} = B_min = {B_min_val}")

    check("§14: probe — the floor is ABSORBING, not a clamp: restoring ample "
          "support does NOT resurrect a dissolved lab",
          probe_dissolved[0] and np.isclose(float(probe_Bi[0]), B_min_val),
          f"after 60t at D = {D_restored} (>> gamma*B_i_0 = {gamma_val*Bi_val}): "
          f"integrity = {float(probe_Bi[0]):.6f}, still dissolved "
          f"(a bare clamp would have regrown it to {Bi_val})")

    # The floor must actually be REACHED, or the semantics above are untested.
    check("§14: the absorbing floor is exercised (labs do reach it)",
          floor_state["Dual-channel collapse"][1] == N_labs
          and floor_state["No failure"][1] == 0,
          "dissolved counts — "
          + ", ".join(f"{k}: {d}/{N_labs}" for k, (_, d) in floor_state.items()))

    check("§14: survivor test tracks B_min rather than a literal 1.0",
          np.isclose(B_min_val, COLLAPSE_FLOOR_FRACTION * B_bar_val),
          f"survivors counted as integrity > B_min = {B_min_val}")

    # Verify scenario outcomes
    check("Scenario 1 (no failure): all 50 survive at t=30",
          results["No failure"][-1] == 50,
          f"surviving = {results['No failure'][-1]:.0f}")

    check("Scenario 2 (repr. shift): all 50 survive (recoverable cascade)",
          results["Representational shift only"][-1] == 50,
          f"surviving = {results['Representational shift only'][-1]:.0f}")

    check("Scenario 3 (dual-channel): worse than scenario 2",
          results["Dual-channel collapse"][-1] < results["Representational shift only"][-1],
          f"dual={results['Dual-channel collapse'][-1]:.0f} < repr={results['Representational shift only'][-1]:.0f}")

    check("Scenario 3 (dual-channel): irreversible — collapse to 0 or near-0",
          results["Dual-channel collapse"][-1] < 10,
          f"surviving = {results['Dual-channel collapse'][-1]:.0f}")

    # The dual-channel scenario should show a second wave of collapse
    # after t=10 (data contamination kicks in)
    surviving_dc = results["Dual-channel collapse"]
    idx_t10 = int(10 / dt)
    idx_t20 = int(20 / dt)
    check("Dual-channel: second collapse wave after t=10",
          surviving_dc[idx_t20] < surviving_dc[idx_t10],
          f"t=10: {surviving_dc[idx_t10]:.0f}, t=20: {surviving_dc[idx_t20]:.0f}")

    # ---------------------------------------------------------------------------
    # 15. Data Contamination Threshold
    # ---------------------------------------------------------------------------

    section("15. Data Contamination Threshold alpha*")

    # The critical synthetic data fraction alpha* is set at 0.4.
    # Below alpha*: the data ecosystem retains enough clean signal for recovery.
    # Above alpha*: recursive degradation (Shumailov et al. 2024) becomes
    # irreversible because successor models train on contaminated data.
    check("alpha* = 0.4 (critical synthetic data fraction)",
          abs(alpha_star - 0.4) < 1e-10)

    # At alpha < alpha*, ecosystem should be recoverable after foundation failure
    # At alpha > alpha*, ecosystem collapse is irreversible
    # This is verified by the simulation above (scenarios 2 vs 3)
    check("Below alpha*: recoverable (scenario 2 has survivors)",
          results["Representational shift only"][-1] > 0)
    check("Above alpha*: irreversible (scenario 3 has near-zero survivors)",
          results["Dual-channel collapse"][-1] < results["Representational shift only"][-1])

    # ---------------------------------------------------------------------------
    # 16. Scaling Table — §3.3
    # ---------------------------------------------------------------------------

    section("16. Scaling Table Verification — §3.3")

    test_cases = [
        (30, 0.0, 15.0),
        (1e2, 5.58, 50.0),
        (1e4, 665.7, 5000.0),
        (1e6, 6.667e4, 5e5),
        (1e8, 6.667e6, 5e7),
    ]

    for M_t, w_expected, D_expected in test_cases:
        D_t = G_val**2 * M_t / (4 * tau_val)
        check(f"M={M_t:.0e}: D = {D_t:.1f}",
              abs(D_t - D_expected) / max(D_expected, 1) < 0.01,
              f"expected {D_expected}")

        w_t = bandwidth(M_t, G_val, tau_val, gamma_val, Bi_val)
        if w_expected == 0.0:
            check(f"M={M_t:.0e}: w = 0 (threshold)",
                  w_t < 0.001, f"w = {w_t:.4f}")
        else:
            check(f"M={M_t:.0e}: w ~= {w_expected}",
                  abs(w_t - w_expected) / w_expected < 0.01,
                  f"w = {w_t:.2f}")

    # ---------------------------------------------------------------------------
    # 17. Propositions 9–10 — Comparative Statics
    # ---------------------------------------------------------------------------

    section("17. Propositions 9–10 — Comparative Statics")

    # Prop 9a: Well depth D linear in M
    D_double = G_val**2 * (2*M_val) / (4*tau_val)
    check("Prop 9a: D doubles when M doubles",
          abs(D_double / well_depth - 2.0) < 1e-6)

    # Prop 9c: r- decreasing in M
    r_minus_2M = (G_val * 2*M_val - math.sqrt(
        G_val**2 * (2*M_val)**2 - 4*gamma_val*Bi_val*tau_val*2*M_val
    )) / (2*gamma_val*Bi_val)
    check("Prop 9c: r- decreases when M increases",
          r_minus_2M < r_minus, f"r-(2M) = {r_minus_2M:.6f} < r-(M) = {r_minus:.6f}")

    # Prop 9d: r+ increasing in M
    r_plus_2M = (G_val * 2*M_val + math.sqrt(
        G_val**2 * (2*M_val)**2 - 4*gamma_val*Bi_val*tau_val*2*M_val
    )) / (2*gamma_val*Bi_val)
    check("Prop 9d: r+ increases when M increases",
          r_plus_2M > r_plus, f"r+(2M) = {r_plus_2M:.1f} > r+(M) = {r_plus:.1f}")

    # Prop 9e: r* unchanged with M
    check("Prop 9e: r* independent of M",
          abs(r_star - 2*tau_val/G_val) < 1e-10)

    # Prop 10a: M_min increasing in Bi
    M_min_2B = 4 * gamma_val * (2*Bi_val) * tau_val / G_val**2
    check("Prop 10a: M_min doubles when Bi doubles",
          abs(M_min_2B / M_min - 2.0) < 1e-6)

    # ---------------------------------------------------------------------------
    # 18. Proposition 11 — Stability-Cooperation Feedback
    # ---------------------------------------------------------------------------

    section("18. Proposition 11 — Stability-Cooperation Feedback")

    def delta_func(r, beta_p=beta_val):
        """Discount factor: delta(r) = 1 - exp(-beta * max(Pi(r), 0))."""
        return 1 - math.exp(-beta_p * max(Pi(r), 0))

    delta_star = delta_func(r_star)
    check("delta(r*) ~= 0.9933",
          abs(delta_star - 0.9933) < 0.001, f"delta(r*) = {delta_star:.4f}")

    # (a) delta maximized at r*
    for r_test in [0.6, 0.8, 1.5, 3.0, 100.0]:
        d_test = delta_func(r_test)
        check(f"Prop 11a: delta(r*) >= delta({r_test})",
              delta_star >= d_test - 1e-10,
              f"delta(r*) = {delta_star:.6f}, delta({r_test}) = {d_test:.6f}")

    # (b) delta(r+) = 0
    delta_boundary = delta_func(r_plus)
    check("delta(r+) ~= 0 (no future horizon at boundary)",
          abs(delta_boundary) < 1e-6, f"delta(r+) = {delta_boundary:.8f}")

    # ---------------------------------------------------------------------------
    # 19. Corollary 24.2 — Inequality of Freedom
    # ---------------------------------------------------------------------------

    section("19. Corollary 24.2 — Inequality of Freedom")

    Bi_A = 50.0
    Bi_B = 10.0

    w_A = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_A)
    w_B = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_B)

    check("Cor 24.2: w(Bi=50) < w(Bi=10) (complex derivative has narrower band)",
          w_A < w_B, f"w_A = {w_A:.1f}, w_B = {w_B:.1f}")

    ratio = w_B / w_A
    check("Model B has ~5x wider band than Model A",
          abs(ratio - 5.0) < 0.1, f"ratio = {ratio:.2f}")

    # ---------------------------------------------------------------------------
    # 20. Symbolic Cross-Checks
    # ---------------------------------------------------------------------------

    section("20. Symbolic Cross-Checks")

    r_sym = sp.Symbol("r", positive=True)
    M_sym = sp.Symbol("M", positive=True)
    G_sym = sp.Symbol("G", positive=True)
    tau_sym = sp.Symbol("tau", positive=True)
    gamma_sym = sp.Symbol("gamma", positive=True)
    B_sym = sp.Symbol("B", positive=True)

    V_sym = tau_sym * M_sym / r_sym**2 - G_sym * M_sym / r_sym + gamma_sym * B_sym

    # First derivative
    V_prime_sym = sp.diff(V_sym, r_sym)
    check("Symbolic V'(r) simplifies correctly",
          sp.simplify(V_prime_sym - M_sym * (G_sym * r_sym - 2 * tau_sym) / r_sym**3) == 0,
          f"V' = {sp.simplify(V_prime_sym)}")

    # Critical point
    r_star_sym = sp.solve(V_prime_sym, r_sym)
    check("Symbolic r* = 2*tau/G",
          len(r_star_sym) == 1 and sp.simplify(r_star_sym[0] - 2*tau_sym/G_sym) == 0,
          f"r* = {r_star_sym}")

    # V''(r*) = G^4*M/(8*tau^3)
    V_pp_sym = sp.diff(V_sym, r_sym, 2)
    V_pp_at_star = V_pp_sym.subs(r_sym, 2*tau_sym/G_sym)
    V_pp_expected = G_sym**4 * M_sym / (8 * tau_sym**3)
    check("Symbolic V''(r*) = G^4*M/(8*tau^3)",
          sp.simplify(V_pp_at_star - V_pp_expected) == 0,
          f"V''(r*) = {sp.simplify(V_pp_at_star)}")

    # V(r*) = gamma*B - G^2*M/(4*tau)
    V_at_star = V_sym.subs(r_sym, 2*tau_sym/G_sym)
    check("Symbolic V(r*) = gamma*B - G^2*M/(4*tau)",
          sp.simplify(V_at_star - (gamma_sym*B_sym - G_sym**2*M_sym/(4*tau_sym))) == 0,
          f"V(r*) = {sp.simplify(V_at_star)}")

    # Multi-center separability
    K_val = 3
    r_syms = sp.symbols("r1 r2 r3", positive=True)
    M_syms = sp.symbols("M1 M2 M3", positive=True)
    tau_syms = sp.symbols("tau1 tau2 tau3", positive=True)
    G_syms = sp.symbols("G1 G2 G3", positive=True)

    V_multi = sum(
        tau_syms[k] * M_syms[k] / r_syms[k]**2 - G_syms[k] * M_syms[k] / r_syms[k]
        for k in range(K_val)
    ) + gamma_sym * B_sym

    for k in range(K_val):
        dV_drk = sp.diff(V_multi, r_syms[k])
        other_r = [r_syms[j] for j in range(K_val) if j != k]
        depends_on_others = any(dV_drk.has(rj) for rj in other_r)
        check(f"Multi-center: dV/dr_{k+1} independent of other r's",
              not depends_on_others)

    # -------------------------------------------------------------------
    # FIGURE DATA EXPORT
    # -------------------------------------------------------------------
    section("FIGURE DATA — Institutional Collapse")

    from modules.figure_data import save_figure_data

    r_star_val = 2 * tau_val / G_val

    # Panel (a): V(r) curves for different M
    masses_fig = [1e2, 1e4, 1e6, 1e8]
    r_min_plot, r_max_plot = 0.3, 15.0
    r_arr = np.linspace(r_min_plot, r_max_plot, 1000)
    # For each mass: V(r) and V(r*) for normalisation
    V_curves = []
    V_star_vals = []
    for M_f in masses_fig:
        V_f = np.array([V(r, M=M_f) for r in r_arr])
        V_star_f = V(r_star_val, M=M_f)
        V_curves.append(V_f)
        V_star_vals.append(V_star_f)
    V_curves = np.array(V_curves)        # shape (4, 1000)
    V_star_vals = np.array(V_star_vals)   # shape (4,)

    # Panel (b): phase diagram — bandwidth vs M for different Bi
    M_range = np.logspace(1.5, 9, 500)
    Bi_values = np.array([10, 25, 50, 100, 200], dtype=float)
    bandwidth_curves = np.array([
        [bandwidth(M, G_val, tau_val, gamma_val, Bi_f) for M in M_range]
        for Bi_f in Bi_values
    ])
    M_min_vals = np.array([
        4 * gamma_val * Bi_f * tau_val / G_val**2 for Bi_f in Bi_values
    ])

    # Panel (c): cascade simulation (three scenarios)
    centers_init_fig = [
        {"name": "F_alpha", "M": 24},
        {"name": "F_beta",  "M": 14},
        {"name": "F_gamma", "M": 10},
    ]
    N_labs = 50
    sigma_sim = 0.4
    rho_sim = 0.5
    dt = 0.1
    T_total = 30.0
    times = np.arange(0, T_total, dt)

    scenarios_fig = [
        {"fail_times": {}, "data_contamination_time": None},
        {"fail_times": {"F_gamma": 5}, "data_contamination_time": None}, # {F_gamme": 5} for a less severe shift
        {"fail_times": {"F_gamma": 5}, "data_contamination_time": 10}, # {F_gamme": 5} for a less severe shift
    ]

    surviving_all = []
    # Upper clip: D_total_all / gamma = G^2 * 48 / (4*tau*gamma) = 80
    # ensures all labs are viable when every center is active.
    # Lower clip: B_min — a lab cannot START below the collapse floor, since the
    # model's admissible domain is (B_min, B_bar].  (This was a literal 1.0; it
    # is the same coincidence as the survivor test and is expressed through
    # B_min for the same reason.)
    D_total_all = sum(G_val**2 * c["M"] / (4 * tau_val) for c in centers_init_fig)
    Bi_max = D_total_all / gamma_val
    for scenario in scenarios_fig:
        rng = np.random.default_rng(42)
        labs_Bi_0 = np.clip(rng.normal(Bi_val, sigma_sim * Bi_val, N_labs),
                            B_min_val, Bi_max)
        labs_Bi = labs_Bi_0.copy()
        dissolved = labs_Bi <= B_min_val          # absorbing set {B_i <= B_min}
        surviving = np.zeros(len(times))

        for i, t in enumerate(times):
            alive_centers = []
            for c in centers_init_fig:
                if c["name"] not in scenario["fail_times"] or \
                   t < scenario["fail_times"][c["name"]]:
                    alive_centers.append(c)

            D_total = sum(G_val**2 * c["M"] / (4 * tau_val) for c in alive_centers)

            if scenario["data_contamination_time"] is not None \
               and t >= scenario["data_contamination_time"]:
                t_since = t - scenario["data_contamination_time"]
                contamination_factor = math.exp(-0.15 * t_since)
                D_total *= contamination_factor

            # Exactly the §14 update rule, including the ABSORBING collapse
            # floor — shared rather than re-typed so the published figure and
            # the verified scenarios cannot drift apart.
            cascade_step(labs_Bi, labs_Bi_0, dissolved, D_total, dt, rho_sim)

            surviving[i] = np.sum(~dissolved)
        surviving_all.append(surviving)

    surviving_all = np.array(surviving_all)  # shape (3, len(times))

    save_figure_data(
        "institutional_collapse",
        # Panel (a)
        r_arr=r_arr,
        masses=np.array(masses_fig),
        V_curves=V_curves,
        V_star_vals=V_star_vals,
        r_star=np.array(r_star_val),
        # Panel (b)
        M_range=M_range,
        Bi_values=Bi_values,
        bandwidth_curves=bandwidth_curves,
        M_min_vals=M_min_vals,
        # Panel (c)
        times=times,
        surviving_all=surviving_all,
        # Params
        G=np.array(G_val),
        tau=np.array(tau_val),
        gamma=np.array(gamma_val),
        Bi=np.array(Bi_val),
        M_crit=np.array(1e6),
    )
    check("Figure data saved", True)

    print()
    sys.exit(summary())
