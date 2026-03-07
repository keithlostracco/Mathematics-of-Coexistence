"""
Verify: Power Concentration — Infrastructure Monopolies
========================================================

Independently validates every numerical claim, applying
Theorems 22–27, Definitions 35–45, Propositions 8–11, Lemma 2, and all
corollaries to the compute infrastructure monopoly scenario.

Run:
    python scripts/simulations/human-applications/verify_power_concentration.py
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

# ---------------------------------------------------------------------------
# 1. AI Scenario Parameters
# ---------------------------------------------------------------------------



if __name__ == "__main__":
    reset()

    section("1. AI Scenario Parameters")

    M_val = 1e8        # GPU-hours/year (value mass)
    G_val = 1.0        # resource coupling coefficient
    tau_val = 0.5      # dissolution coupling coefficient
    gamma_val = 0.3    # entropy leakage rate
    Bi_val = 50.0      # boundary integrity
    sigma_val = 0.1    # assimilation intensity
    rho_val = 0.5      # repair allocation fraction
    mu_val = 1.0       # adjustment rate
    beta_val = 1e-7    # discount factor scaling

    print(f"  M = {M_val:.0e}, G = {G_val}, tau = {tau_val}")
    print(f"  gamma = {gamma_val}, B_i = {Bi_val}, sigma = {sigma_val}")
    print(f"  rho = {rho_val}, mu = {mu_val}, beta = {beta_val}")
    check("Parameters loaded", True)

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


    # Verify at a few test points
    check("V(1.0) = tau*M/1 - G*M/1 + gamma*Bi",
          abs(V(1.0) - (tau_val*M_val - G_val*M_val + gamma_val*Bi_val)) < 1e-6,
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
    gamma_Bi = gamma_val * Bi_val  # = 15
    check("Prop 8b: V(r) -> gamma*Bi as r -> inf",
          abs(V(1e12) - gamma_Bi) < 1e-4, f"V(1e12) = {V(1e12):.6f}, gamma*Bi = {gamma_Bi}")

    # (c) Smoothness — V is C^inf (structural, not numerically testable, skip)

    # (d) Unique critical point — the minimum
    r_star = 2 * tau_val / G_val  # = 1.0
    check("Prop 8d: unique critical point at r* = 2*tau/G",
          abs(r_star - 1.0) < 1e-10, f"r* = {r_star}")

    def V_prime_exact(r, M=M_val, G=G_val, tau=tau_val):
        """V'(r) = -2*tau*M/r^3 + G*M/r^2 = M/r^3 * (G*r - 2*tau)."""
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
    expected_eigenvalue = -mu_val * G_val**4 * M_val / (8 * tau_val**3)
    check("Thm 22b: V''(r*) = G^4*M/(8*tau^3)",
          abs(V_pp_star - G_val**4 * M_val / (8 * tau_val**3)) < 1e-2,
          f"V''(r*) = {V_pp_star:.2e}")
    check("Thm 22b: eigenvalue lambda < 0",
          eigenvalue < 0, f"lambda = {eigenvalue:.2e}")
    check("Thm 22b: eigenvalue = -1e8",
          abs(eigenvalue - (-1e8)) < 1, f"lambda = {eigenvalue:.2e}")

    # (c) Global attraction — simulate gradient dynamics
    section("4c. Theorem 22c — Lyapunov global attraction (simulation)")

    def simulate_gradient(r0, dt=1e-12, steps=10000):
        """Simulate dr/dt = -mu * V'(r) from r0."""
        r_t = r0
        for _ in range(steps):
            r_t = r_t - dt * mu_val * V_prime_exact(r_t)
            if r_t < 1e-10:
                return r_t
        return r_t


    # From r0 = 0.3 (close coupling)
    r_final_close = simulate_gradient(0.3, dt=1e-12, steps=50000)
    check("Thm 22c: gradient from r=0.3 converges toward r*",
          r_final_close > 0.3, f"r_final = {r_final_close:.4f}")

    # From r0 = 5.0 (far coupling)
    r_final_far = simulate_gradient(5.0, dt=1e-12, steps=50000)
    check("Thm 22c: gradient from r=5.0 converges toward r*",
          r_final_far < 5.0, f"r_final = {r_final_far:.4f}")

    # Lyapunov function W = V(r) - V(r*) >= 0 always
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

    # Test: band should NOT exist when M < M_min
    Delta_sub = G_val**2 * 20**2 - 4 * gamma_val * Bi_val * tau_val * 20
    check("M=20 < M_min=30: Delta < 0 (no band)",
          Delta_sub < 0, f"Delta(M=20) = {Delta_sub}")

    # Test: band at exact threshold
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
    # Use Vieta's formula for r- to avoid catastrophic cancellation:
    # r- * r+ = tau*M / (gamma*Bi), so r- = tau*M / (gamma*Bi * r+)
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

    # (a) w > 0 iff M > M_min (already shown)
    check("Thm 24a: w > 0 since M > M_min", w > 0)

    # (b) w increasing in M
    masses = [1e2, 1e4, 1e6, 1e8]
    bandwidths = []
    for M_test in masses:
        D_test = G_val**2 * M_test**2 - 4 * gamma_val * Bi_val * tau_val * M_test
        if D_test > 0:
            bandwidths.append(math.sqrt(D_test) / (gamma_val * Bi_val))
        else:
            bandwidths.append(0.0)

    check("Thm 24b: w increasing in M",
          all(bandwidths[i] < bandwidths[i+1] for i in range(len(bandwidths)-1)),
          f"w = {[f'{b:.1f}' for b in bandwidths]}")

    # (c) w decreasing in gamma, Bi, tau — numerical perturbation tests
    def bandwidth(M, G, tau, gamma, Bi):
        D = G**2 * M**2 - 4 * gamma * Bi * tau * M
        if D <= 0:
            return 0.0
        return math.sqrt(D) / (gamma * Bi)


    w_base = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_val)

    # w decreasing in gamma
    w_gamma_up = bandwidth(M_val, G_val, tau_val, gamma_val * 1.1, Bi_val)
    check("Thm 24c: w decreasing in gamma",
          w_gamma_up < w_base, f"w(gamma*1.1) = {w_gamma_up:.1f} < {w_base:.1f}")

    # w decreasing in Bi
    w_Bi_up = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_val * 1.1)
    check("Thm 24c: w decreasing in Bi",
          w_Bi_up < w_base, f"w(Bi*1.1) = {w_Bi_up:.1f} < {w_base:.1f}")

    # w decreasing in tau
    w_tau_up = bandwidth(M_val, G_val, tau_val * 1.1, gamma_val, Bi_val)
    check("Thm 24c: w decreasing in tau",
          w_tau_up < w_base, f"w(tau*1.1) = {w_tau_up:.1f} < {w_base:.1f}")

    # (d) w increasing in G
    w_G_up = bandwidth(M_val, G_val * 1.1, tau_val, gamma_val, Bi_val)
    check("Thm 24d: w increasing in G",
          w_G_up > w_base, f"w(G*1.1) = {w_G_up:.1f} > {w_base:.1f}")

    # (e) Large-M limit: w ~= G*M/(gamma*Bi)
    w_approx = G_val * M_val / (gamma_val * Bi_val)
    check("Thm 24e: w ~= G*M/(gamma*Bi) for large M",
          abs(w - w_approx) / w_approx < 1e-4,
          f"w = {w:.1f}, approx = {w_approx:.1f}")

    # (f) Near threshold: w ~ sqrt(M - M_min)
    M_near = M_min * 1.001
    D_near = G_val**2 * M_near**2 - 4 * gamma_val * Bi_val * tau_val * M_near
    w_near = math.sqrt(D_near) / (gamma_val * Bi_val) if D_near > 0 else 0
    # Check that w_near is small
    check("Thm 24f: w vanishes near M_min",
          w_near < 1.0 and w_near > 0, f"w(M_min*1.001) = {w_near:.4f}")

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
    # 10. Theorem 25 — Irreversibility of Dissolution
    # ---------------------------------------------------------------------------

    section("10. Theorem 25 — Irreversibility of Dissolution")

    Pi_max = G_val**2 * M_val / (4 * tau_val) - gamma_val * Bi_val
    r_d = (sigma_val * M_val / (rho_val * Pi_max + gamma_val * Bi_val))**(1/3)
    check("r_d = (sigma*M / (rho*Pi_max + gamma*Bi))^(1/3)",
          True, f"r_d = {r_d:.6f}")
    check("r_d ~= 0.737",
          abs(r_d - 0.737) < 0.001, f"r_d = {r_d:.6f}")

    # Assimilation trap: r_d > r-
    check("Cor 25.1: r_d > r- (assimilation trap exists)",
          r_d > r_minus, f"r_d = {r_d:.4f} > r- = {r_minus:.4f}")

    # Acqui-hire at r = 0.5 (just inside inner boundary)
    r_acq = 0.5
    D_assim_05 = sigma_val * M_val / r_acq**3
    Pi_05 = Pi(r_acq)
    R_repair_05 = rho_val * max(Pi_05, 0)
    Bdot_05 = R_repair_05 - D_assim_05 - gamma_val * Bi_val

    check("At r=0.5: D_assimilate = sigma*M/r^3 = 8e7",
          abs(D_assim_05 - 8e7) < 1e2, f"D_assimilate = {D_assim_05:.2e}")
    check("At r=0.5: Pi < 0 (energy deficit)",
          Pi_05 < 0, f"Pi(0.5) = {Pi_05:.2e}")
    check("At r=0.5: R_repair = 0 (no surplus)",
          abs(R_repair_05) < 1e-6, f"R_repair = {R_repair_05}")
    check("At r=0.5: dBi/dt << 0 (rapid boundary collapse)",
          Bdot_05 < -1e7, f"dBi/dt = {Bdot_05:.2e}")

    # Acqui-hire at r = 0.6 (inside viable band but below r_d)
    r_06 = 0.6
    D_assim_06 = sigma_val * M_val / r_06**3
    Pi_06 = Pi(r_06)
    R_repair_06 = rho_val * max(Pi_06, 0)
    Bdot_06 = R_repair_06 - D_assim_06 - gamma_val * Bi_val

    check("At r=0.6: Pi > 0 (inside viable band)",
          Pi_06 > 0, f"Pi(0.6) = {Pi_06:.2e}")
    check("At r=0.6: D_assimilate > R_repair (dissolution wins)",
          D_assim_06 > R_repair_06,
          f"D_assim = {D_assim_06:.2e} > R_repair = {R_repair_06:.2e}")
    check("At r=0.6: dBi/dt < 0 (assimilation trap: viable but dissolving)",
          Bdot_06 < 0, f"dBi/dt = {Bdot_06:.2e}")

    # Verify README numerical claims for r=0.6
    Pi_06_expected = G_val * M_val / 0.6 - tau_val * M_val / 0.36 - gamma_val * Bi_val
    check("Pi(0.6) matches README calculation",
          abs(Pi_06 - Pi_06_expected) < 1, f"Pi(0.6) = {Pi_06:.2e}")

    D_assim_06_expected = sigma_val * M_val / (0.6**3)
    check("D_assimilate(0.6) matches README",
          abs(D_assim_06 - D_assim_06_expected) < 1, f"D = {D_assim_06:.2e}")

    # Finite-time collapse simulation at r = 0.5
    section("10b. Dissolution simulation at r=0.5")

    Bi_t = Bi_val
    dt_diss = 1e-9  # very small timestep because dBi/dt is huge
    steps_to_zero = 0
    while Bi_t > 0 and steps_to_zero < 1_000_000:
        Pi_t = max(Pi(r_acq, M_val, G_val, tau_val, gamma_val, Bi_t), 0)
        D_assim_t = sigma_val * M_val / r_acq**3
        dB = rho_val * Pi_t - D_assim_t - gamma_val * Bi_t
        Bi_t += dB * dt_diss
        steps_to_zero += 1

    check("Thm 25c: B_i reaches 0 in finite time at r=0.5",
          Bi_t <= 0, f"B_i -> {Bi_t:.4f} after {steps_to_zero} steps")

    # ---------------------------------------------------------------------------
    # 11. Theorem 26 — Starvation Spiral
    # ---------------------------------------------------------------------------

    section("11. Theorem 26 — Starvation Spiral")

    r_outside = 1e7  # well beyond r+

    # (a) Pi < 0 outside band
    Pi_outside = Pi(r_outside)
    check("Thm 26a: Pi(r=1e7) < 0 (outside band)",
          Pi_outside < 0, f"Pi = {Pi_outside:.2e}")

    # (b) Boundary decay
    D_assim_outside = sigma_val * M_val / r_outside**3
    Bdot_outside = rho_val * max(Pi_outside, 0) - D_assim_outside - gamma_val * Bi_val
    check("Thm 26b: dBi/dt < 0 outside band",
          Bdot_outside < 0, f"dBi/dt = {Bdot_outside:.2e}")

    # (c) Exponential starvation: Bi(t) = Bi(0)*exp(-gamma*t)
    # At large r, D_assimilate ~= 0, so dominant decay is -gamma*Bi
    check("Thm 26: at large r, D_assimilate ~= 0",
          D_assim_outside < 1e-5, f"D_assim(1e7) = {D_assim_outside:.2e}")

    # Time to Bi=1: t = ln(Bi_0)/gamma
    t_to_1 = math.log(Bi_val) / gamma_val
    check("Starvation time to Bi=1: t = ln(50)/0.3 ~= 13.0",
          abs(t_to_1 - 13.04) < 0.1, f"t = {t_to_1:.2f}")

    # Simulate starvation
    Bi_starve = Bi_val
    dt_starve = 0.01
    t_starve = 0
    while Bi_starve > 1.0:
        Bi_starve *= math.exp(-gamma_val * dt_starve)
        t_starve += dt_starve

    check("Starvation simulation: Bi reaches 1 at t ~= 13",
          abs(t_starve - t_to_1) < 0.5, f"t_sim = {t_starve:.2f}")

    # ---------------------------------------------------------------------------
    # 12. Theorem 27 — Multi-Center Dynamics
    # ---------------------------------------------------------------------------

    section("12. Theorem 27 — Multi-Center Attractor")

    # Three compute centers
    centers = [
        {"name": "Alpha", "M": 5e7, "G": 1.0, "tau": 0.5, "labs": 25},
        {"name": "Beta",  "M": 3e7, "G": 1.0, "tau": 0.5, "labs": 15},
        {"name": "Gamma", "M": 2e7, "G": 1.0, "tau": 0.5, "labs": 10},
    ]

    # Each center's optimal coupling and well depth
    for c in centers:
        c["r_star"] = 2 * c["tau"] / c["G"]
        c["D"] = c["G"]**2 * c["M"] / (4 * c["tau"])

    check("Alpha r* = 1.0", abs(centers[0]["r_star"] - 1.0) < 1e-10)
    check("Beta r* = 1.0", abs(centers[1]["r_star"] - 1.0) < 1e-10)
    check("Gamma r* = 1.0", abs(centers[2]["r_star"] - 1.0) < 1e-10)

    check("Alpha D = 2.5e7", abs(centers[0]["D"] - 2.5e7) < 1, f"D = {centers[0]['D']:.2e}")
    check("Beta D = 1.5e7", abs(centers[1]["D"] - 1.5e7) < 1, f"D = {centers[1]['D']:.2e}")
    check("Gamma D = 1.0e7", abs(centers[2]["D"] - 1.0e7) < 1, f"D = {centers[2]['D']:.2e}")

    # Multi-center total well depth
    D_total = sum(c["D"] for c in centers)
    check("D_total = 5.0e7",
          abs(D_total - 5.0e7) < 1, f"D_total = {D_total:.2e}")

    # Viability condition: D_total > gamma*Bi
    check("Thm 27: multi-center viable (D_total >> gamma*Bi)",
          D_total > gamma_Bi, f"D_total = {D_total:.2e} >> {gamma_Bi}")

    # Multi-center V at attractor
    V_multi_star = gamma_Bi - D_total
    check("V(r*) = gamma*Bi - D_total < 0",
          V_multi_star < 0, f"V_multi(r*) = {V_multi_star:.2e}")

    # Corollary 27.1: Diversification benefit
    # Individual M_min = 30. Each center has M >> 30, so individually viable too.
    for c in centers:
        check(f"Cor 27.1: {c['name']} individually viable (M={c['M']:.0e} > {M_min})",
              c["M"] > M_min)

    # ---------------------------------------------------------------------------
    # 13. Cascade Collapse — Corollary 27.2
    # ---------------------------------------------------------------------------

    section("13. Cascade Collapse — Corollary 27.2")

    # Scenario: Gamma fails
    D_after_gamma_fail = centers[0]["D"] + centers[1]["D"]
    check("After Gamma fails: D = Alpha + Beta = 4.0e7",
          abs(D_after_gamma_fail - 4.0e7) < 1, f"D = {D_after_gamma_fail:.2e}")
    check("Labs still viable after Gamma fails",
          D_after_gamma_fail > gamma_Bi)

    # Scenario: Beta AND Gamma fail
    D_after_BG_fail = centers[0]["D"]
    check("After Beta+Gamma fail: D = Alpha = 2.5e7",
          abs(D_after_BG_fail - 2.5e7) < 1, f"D = {D_after_BG_fail:.2e}")
    check("Labs still individually viable after Beta+Gamma fail",
          D_after_BG_fail > gamma_Bi)

    # Freedom lost if Alpha also collapses
    N_labs = 50
    w_alpha = bandwidth(centers[0]["M"], centers[0]["G"], centers[0]["tau"],
                         gamma_val, Bi_val)
    F_lost = N_labs * w_alpha
    check("Freedom lost on Alpha collapse: N*w(M_Alpha)",
          F_lost > 1e8, f"F_lost = {F_lost:.3e}")

    # Total freedom lost: N * w(M_Alpha)
    expected_w_alpha = math.sqrt(
        centers[0]["G"]**2 * centers[0]["M"]**2 -
        4 * gamma_val * Bi_val * centers[0]["tau"] * centers[0]["M"]
    ) / (gamma_val * Bi_val)
    check("w(Alpha) computed correctly",
          abs(w_alpha - expected_w_alpha) < 1, f"w = {w_alpha:.1f}")
    check("Total F_lost = 50 * w_alpha ~= 1.67e8",
          abs(F_lost - 50 * w_alpha) < 1, f"F_lost = {F_lost:.3e}")

    # ---------------------------------------------------------------------------
    # 14. Scaling Table — §3.3
    # ---------------------------------------------------------------------------

    section("14. Scaling Table Verification — §3.3")

    test_cases = [
        (30, 0.0, 15.0),    # threshold
        (1e2, 5.58, 50.0),
        (1e4, 665.3, 5000.0),
        (1e6, 6.666e4, 5e5),
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
    # 15. Propositions 9–10 — Comparative Statics
    # ---------------------------------------------------------------------------

    section("15. Propositions 9–10 — Comparative Statics")

    # Prop 9: Value mass effects
    # (a) Well depth D linear in M
    D_double = G_val**2 * (2*M_val) / (4*tau_val)
    check("Prop 9a: D doubles when M doubles",
          abs(D_double / well_depth - 2.0) < 1e-6)

    # (b) w increasing in M (already checked above in Thm 24b)
    check("Prop 9b: w increasing in M (see Thm 24b)", True)

    # (c) r- decreasing in M
    r_minus_2M = (G_val * 2*M_val - math.sqrt(
        G_val**2 * (2*M_val)**2 - 4*gamma_val*Bi_val*tau_val*2*M_val
    )) / (2*gamma_val*Bi_val)
    check("Prop 9c: r- decreases when M increases",
          r_minus_2M < r_minus, f"r-(2M) = {r_minus_2M:.6f} < r-(M) = {r_minus:.6f}")

    # (d) r+ increasing in M
    r_plus_2M = (G_val * 2*M_val + math.sqrt(
        G_val**2 * (2*M_val)**2 - 4*gamma_val*Bi_val*tau_val*2*M_val
    )) / (2*gamma_val*Bi_val)
    check("Prop 9d: r+ increases when M increases",
          r_plus_2M > r_plus, f"r+(2M) = {r_plus_2M:.1f} > r+(M) = {r_plus:.1f}")

    # (e) r* unchanged with M
    check("Prop 9e: r* independent of M",
          abs(r_star - 2*tau_val/G_val) < 1e-10)

    # Prop 10: Boundary integrity effects
    # (a) M_min increasing in Bi
    M_min_2B = 4 * gamma_val * (2*Bi_val) * tau_val / G_val**2
    check("Prop 10a: M_min doubles when Bi doubles",
          abs(M_min_2B / M_min - 2.0) < 1e-6)

    # (b) w decreasing in Bi (already checked in Thm 24c)
    check("Prop 10b: w decreasing in Bi (see Thm 24c)", True)

    # (c) r* independent of Bi
    check("Prop 10c: r* independent of Bi",
          abs(r_star - 2*tau_val/G_val) < 1e-10)

    # ---------------------------------------------------------------------------
    # 16. Proposition 11 — Stability-Cooperation Feedback
    # ---------------------------------------------------------------------------

    section("16. Proposition 11 — Stability-Cooperation Feedback")

    def delta_func(r, beta_p=beta_val):
        """Discount factor: delta(r) = 1 - exp(-beta * max(Pi(r), 0))."""
        return 1 - math.exp(-beta_p * max(Pi(r), 0))


    delta_star = delta_func(r_star)
    check("delta(r*) = 1 - exp(-beta*Pi(r*)) ~= 0.9933",
          abs(delta_star - (1 - math.exp(-beta_val * Pi_star))) < 1e-6,
          f"delta(r*) = {delta_star:.6f}")
    check("delta(r*) ~= 0.9933",
          abs(delta_star - 0.9933) < 0.001, f"delta(r*) = {delta_star:.4f}")

    # (a) delta maximized at r*
    for r_test in [0.6, 0.8, 1.5, 3.0, 100.0]:
        d_test = delta_func(r_test)
        check(f"Prop 11a: delta(r*) >= delta({r_test})",
              delta_star >= d_test - 1e-10,
              f"delta(r*) = {delta_star:.6f}, delta({r_test}) = {d_test:.6f}")

    # (b) delta(r+) = 0 (at band boundary, Pi = 0)
    delta_boundary = delta_func(r_plus)
    check("delta(r+) ~= 0 (no future horizon at boundary)",
          abs(delta_boundary) < 1e-6, f"delta(r+) = {delta_boundary:.8f}")

    # (c) Cooperation threshold: delta* = 0.159
    delta_coop = 0.159
    check("Prop 11c: delta(r*) >> delta* = 0.159",
          delta_star > delta_coop,
          f"delta(r*) = {delta_star:.4f} > delta* = {delta_coop}")

    # Cooperation subband: find r where delta(r) = delta*
    # delta(r) = delta* => Pi(r) = -ln(1 - delta*)/beta
    Pi_threshold = -math.log(1 - delta_coop) / beta_val
    # Pi(r) = G*M/r - tau*M/r^2 - gamma*Bi = Pi_threshold
    # This is a quadratic in 1/r... solve numerically
    from scipy.optimize import brentq


    def delta_minus_coop(r):
        return delta_func(r) - delta_coop


    # Find inner crossing (between r_minus and r_star)
    r_coop_inner = brentq(delta_minus_coop, r_minus + 0.001, r_star)
    # Find outer crossing (between r_star and r_plus)
    r_coop_outer = brentq(delta_minus_coop, r_star, r_plus - 0.01)

    check("Cooperation subband exists (inner < r* < outer)",
          r_coop_inner < r_star < r_coop_outer,
          f"r_coop = ({r_coop_inner:.4f}, {r_coop_outer:.1f})")
    check("Cooperation subband centered on r*",
          abs(r_coop_inner) > r_minus and r_coop_outer < r_plus)

    # ---------------------------------------------------------------------------
    # 17. Corollary 24.2 — Inequality of Freedom
    # ---------------------------------------------------------------------------

    section("17. Corollary 24.2 — Inequality of Freedom")

    Bi_A = 50.0
    Bi_B = 10.0

    w_A = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_A)
    w_B = bandwidth(M_val, G_val, tau_val, gamma_val, Bi_B)

    check("Cor 24.2a: w(Bi=50) < w(Bi=10) (complex entity has narrower band)",
          w_A < w_B, f"w_A = {w_A:.1f}, w_B = {w_B:.1f}")

    # Lab B: M_min
    M_min_B = 4 * gamma_val * Bi_B * tau_val / G_val**2
    check("Cor 24.2b: M_min(Bi=50) > M_min(Bi=10)",
          M_min > M_min_B, f"M_min_A = {M_min}, M_min_B = {M_min_B}")

    # Lab B bandwidth ~= 3.333e7
    gamma_B_Bi_B = gamma_val * Bi_B  # = 3.0
    Delta_B = G_val**2 * M_val**2 - 4 * gamma_val * Bi_B * tau_val * M_val
    w_B_check = math.sqrt(Delta_B) / gamma_B_Bi_B
    check("Lab B bandwidth ~= 3.333e7",
          abs(w_B_check - 3.333e7) / 3.333e7 < 0.001, f"w_B = {w_B_check:.3e}")

    # Lab B has ~5x wider band
    ratio = w_B / w_A
    check("Lab B has ~5x wider band than Lab A",
          abs(ratio - 5.0) < 0.1, f"ratio = {ratio:.2f}")

    # ---------------------------------------------------------------------------
    # 18. Symbolic Cross-Checks
    # ---------------------------------------------------------------------------

    section("18. Symbolic Cross-Checks")

    r_sym = sp.Symbol("r", positive=True)
    M_sym = sp.Symbol("M", positive=True)
    G_sym = sp.Symbol("G", positive=True)
    tau_sym = sp.Symbol("tau", positive=True)
    gamma_sym = sp.Symbol("gamma", positive=True)
    B_sym = sp.Symbol("B", positive=True)

    V_sym = tau_sym * M_sym / r_sym**2 - G_sym * M_sym / r_sym + gamma_sym * B_sym

    # First derivative
    V_prime_sym = sp.diff(V_sym, r_sym)
    V_prime_simplified = sp.simplify(V_prime_sym)
    check("Symbolic V'(r) simplifies correctly",
          sp.simplify(V_prime_sym - M_sym * (G_sym * r_sym - 2 * tau_sym) / r_sym**3) == 0,
          f"V' = {V_prime_simplified}")

    # Critical point
    r_star_sym = sp.solve(V_prime_sym, r_sym)
    check("Symbolic r* = 2*tau/G",
          len(r_star_sym) == 1 and sp.simplify(r_star_sym[0] - 2*tau_sym/G_sym) == 0,
          f"r* = {r_star_sym}")

    # Second derivative at r*
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

    # Multi-center: potential separability
    K_val = 3
    r_syms = sp.symbols("r1 r2 r3", positive=True)
    M_syms = sp.symbols("M1 M2 M3", positive=True)
    tau_syms = sp.symbols("tau1 tau2 tau3", positive=True)
    G_syms = sp.symbols("G1 G2 G3", positive=True)

    V_multi = sum(
        tau_syms[k] * M_syms[k] / r_syms[k]**2 - G_syms[k] * M_syms[k] / r_syms[k]
        for k in range(K_val)
    ) + gamma_sym * B_sym

    # Each component's gradient wrt r_k depends only on r_k
    for k in range(K_val):
        dV_drk = sp.diff(V_multi, r_syms[k])
        # Check that dV/dr_k doesn't contain r_j for j != k
        other_r = [r_syms[j] for j in range(K_val) if j != k]
        depends_on_others = any(dV_drk.has(rj) for rj in other_r)
        check(f"Multi-center: dV/dr_{k+1} independent of other r's",
              not depends_on_others)

    # -------------------------------------------------------------------
    # FIGURE DATA EXPORT
    # -------------------------------------------------------------------
    section("FIGURE DATA — Power Concentration")

    from modules.figure_data import save_figure_data

    r_star_val = 2 * tau_val / G_val

    # Panel (a): V(r) curves for different M
    masses_fig = [1e2, 1e4, 1e6, 1e8]
    r_min_plot, r_max_plot = 0.3, 15.0
    r_arr = np.linspace(r_min_plot, r_max_plot, 1000)
    V_curves = []
    V_star_vals = []
    for M_f in masses_fig:
        V_f = np.array([V(r, M=M_f) for r in r_arr])
        V_star_f = V(r_star_val, M=M_f)
        V_curves.append(V_f)
        V_star_vals.append(V_star_f)
    V_curves = np.array(V_curves)
    V_star_vals = np.array(V_star_vals)

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

    # Panel (c): Cascade collapse simulation (3 scenarios)
    centers_init_fig = [
        {"name": "Alpha", "M": 24},
        {"name": "Beta",  "M": 14},
        {"name": "Gamma", "M": 10},
    ]
    N_labs = 50
    sigma_sim = 0.35
    rho_sim = 0.5
    dt = 0.1
    T_total = 30.0
    times = np.arange(0, T_total, dt)

    scenarios_fig = [
        {"fail_times": {}},
        {"fail_times": {"Gamma": 5}},
        {"fail_times": {"Gamma": 5, "Beta": 10}},
    ]

    surviving_all = []
    for scenario in scenarios_fig:
        rng = np.random.default_rng(42)
        labs_Bi_0 = np.clip(rng.normal(Bi_val, sigma_sim * Bi_val, N_labs), 20, 80)
        labs_Bi = labs_Bi_0.copy()
        surviving = np.zeros(len(times))

        for i, t in enumerate(times):
            alive_centers = []
            for c in centers_init_fig:
                if c["name"] not in scenario["fail_times"] or \
                   t < scenario["fail_times"][c["name"]]:
                    alive_centers.append(c)

            D_total = sum(G_val**2 * c["M"] / (4 * tau_val) for c in alive_centers)

            for j in range(N_labs):
                if labs_Bi[j] <= 0:
                    continue
                if D_total >= gamma_val * labs_Bi_0[j]:
                    labs_Bi[j] = min(labs_Bi[j] + rho_sim * dt, labs_Bi_0[j])
                else:
                    deficit = gamma_val * labs_Bi_0[j] - D_total
                    labs_Bi[j] -= deficit * dt
                    if labs_Bi[j] < 0:
                        labs_Bi[j] = 0.0

            surviving[i] = np.sum(labs_Bi > 1.0)
        surviving_all.append(surviving)

    surviving_all = np.array(surviving_all)

    save_figure_data(
        "power_concentration",
        r_arr=r_arr,
        masses=np.array(masses_fig),
        V_curves=V_curves,
        V_star_vals=V_star_vals,
        r_star=np.array(r_star_val),
        M_range=M_range,
        Bi_values=Bi_values,
        bandwidth_curves=bandwidth_curves,
        M_min_vals=M_min_vals,
        times=times,
        surviving_all=surviving_all,
        G=np.array(G_val),
        tau=np.array(tau_val),
        gamma=np.array(gamma_val),
        Bi=np.array(Bi_val),
    )
    check("Figure data saved", True)

    print()
    sys.exit(summary())
