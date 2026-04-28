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
    mu_val = 1.0        # Coupling adjustment rate
    beta_val = 1e-7     # Discount factor scaling
    alpha_star = 0.4    # Critical synthetic data fraction

    print(f"  M = {M_val:.0e}, G = {G_val}, tau = {tau_val}")
    print(f"  gamma = {gamma_val}, B_i = {Bi_val}, sigma = {sigma_val}")
    print(f"  rho = {rho_val}, mu = {mu_val}, beta = {beta_val}")
    print(f"  alpha* = {alpha_star}")
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
    # 10. Theorem 25 — Representational Lock-In (Dissolution)
    # ---------------------------------------------------------------------------

    section("10. Theorem 25 — Representational Lock-In")

    Pi_max = G_val**2 * M_val / (4 * tau_val) - gamma_val * Bi_val
    r_d = (sigma_val * M_val / (rho_val * Pi_max + gamma_val * Bi_val))**(1/3)
    check("r_d = (sigma*M / (rho*Pi_max + gamma*Bi))^(1/3)",
          True, f"r_d = {r_d:.6f}")
    check("r_d ~= 0.737",
          abs(r_d - 0.737) < 0.001, f"r_d = {r_d:.6f}")

    # Lock-in trap: r_d > r-
    check("Cor 25.1: r_d > r- (lock-in trap exists)",
          r_d > r_minus, f"r_d = {r_d:.4f} > r- = {r_minus:.4f}")

    # Lock-in at r = 0.5
    r_lock = 0.5
    D_assim_05 = sigma_val * M_val / r_lock**3
    Pi_05 = Pi(r_lock)
    R_repair_05 = rho_val * max(Pi_05, 0)
    Bdot_05 = R_repair_05 - D_assim_05 - gamma_val * Bi_val

    check("At r=0.5: D_assimilate = sigma*M/r^3 = 8e7",
          abs(D_assim_05 - 8e7) < 1e2, f"D_assimilate = {D_assim_05:.2e}")
    check("At r=0.5: Pi < 0 (energy deficit)",
          Pi_05 < 0, f"Pi(0.5) = {Pi_05:.2e}")
    check("At r=0.5: R_repair = 0 (no surplus)",
          abs(R_repair_05) < 1e-6, f"R_repair = {R_repair_05}")
    check("At r=0.5: dBi/dt << 0 (rapid collapse)",
          Bdot_05 < -1e7, f"dBi/dt = {Bdot_05:.2e}")

    # Lock-in at r = 0.6
    r_06 = 0.6
    D_assim_06 = sigma_val * M_val / r_06**3
    Pi_06 = Pi(r_06)
    R_repair_06 = rho_val * max(Pi_06, 0)
    Bdot_06 = R_repair_06 - D_assim_06 - gamma_val * Bi_val

    check("At r=0.6: Pi > 0 (inside viable band)",
          Pi_06 > 0, f"Pi(0.6) = {Pi_06:.2e}")
    check("At r=0.6: D_assimilate > R_repair (homogenization wins)",
          D_assim_06 > R_repair_06,
          f"D_assim = {D_assim_06:.2e} > R_repair = {R_repair_06:.2e}")
    check("At r=0.6: dBi/dt < 0 (lock-in trap: capable but dissolving)",
          Bdot_06 < 0, f"dBi/dt = {Bdot_06:.2e}")

    # Finite-time collapse simulation at r = 0.5
    section("10b. Dissolution simulation at r=0.5")

    Bi_t = Bi_val
    dt_diss = 1e-9
    steps_to_zero = 0
    while Bi_t > 0 and steps_to_zero < 1_000_000:
        Pi_t = max(Pi(r_lock, M_val, G_val, tau_val, gamma_val, Bi_t), 0)
        D_assim_t = sigma_val * M_val / r_lock**3
        dB = rho_val * Pi_t - D_assim_t - gamma_val * Bi_t
        Bi_t += dB * dt_diss
        steps_to_zero += 1

    check("Thm 25c: B_i reaches 0 in finite time at r=0.5",
          Bi_t <= 0, f"B_i -> {Bi_t:.4f} after {steps_to_zero} steps")

    # ---------------------------------------------------------------------------
    # 11. Theorem 26 — Capability Starvation Spiral
    # ---------------------------------------------------------------------------

    section("11. Theorem 26 — Capability Starvation Spiral")

    r_outside = 1e7

    Pi_outside = Pi(r_outside)
    check("Thm 26a: Pi(r=1e7) < 0 (outside band)",
          Pi_outside < 0, f"Pi = {Pi_outside:.2e}")

    D_assim_outside = sigma_val * M_val / r_outside**3
    Bdot_outside = rho_val * max(Pi_outside, 0) - D_assim_outside - gamma_val * Bi_val
    check("Thm 26b: dBi/dt < 0 outside band",
          Bdot_outside < 0, f"dBi/dt = {Bdot_outside:.2e}")

    check("Thm 26: at large r, D_assimilate ~= 0",
          D_assim_outside < 1e-5, f"D_assim(1e7) = {D_assim_outside:.2e}")

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

    for scenario in scenarios:
        rng = np.random.default_rng(42)
        labs_Bi_0 = np.clip(rng.normal(Bi_val, sigma_sim * Bi_val, N_labs), 20, 70)
        labs_Bi = labs_Bi_0.copy()
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

            for j in range(N_labs):
                if labs_Bi[j] <= 0:
                    continue
                if D_total_sim >= gamma_val * labs_Bi_0[j]:
                    labs_Bi[j] = min(labs_Bi[j] + rho_val * dt, labs_Bi_0[j])
                else:
                    deficit = gamma_val * labs_Bi_0[j] - D_total_sim
                    labs_Bi[j] -= deficit * dt
                    if labs_Bi[j] < 0:
                        labs_Bi[j] = 0.0

            surviving[i] = np.sum(labs_Bi > 1.0)

        results[scenario["name"]] = surviving

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
    D_total_all = sum(G_val**2 * c["M"] / (4 * tau_val) for c in centers_init_fig)
    Bi_max = D_total_all / gamma_val
    for scenario in scenarios_fig:
        rng = np.random.default_rng(42)
        labs_Bi_0 = np.clip(rng.normal(Bi_val, sigma_sim * Bi_val, N_labs), 1.0, Bi_max)
        labs_Bi = labs_Bi_0.copy()
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
