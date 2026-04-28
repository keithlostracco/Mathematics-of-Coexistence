"""
Figure: Superlinear Recovery Time (§7.9)
=========================================

Two-panel figure:
  (a) Recovery time T_recover(λ) vs. destruction fraction λ for different β
      values, showing the transition from approximately linear (low β) to
      threshold-dominated (high β). Ecological system labels annotated.
  (b) Recovery time ratio T(λ) / T_linear(λ) vs. λ, highlighting the
      superlinear penalty. A ratio of 1 means linear recovery; higher
      means superlinear.

Output: output/figures/fig_recovery_time.png
"""


from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.plotting import paper_style
from modules.negentropy import recovery_time, recovery_time_lower_bound, tipping_threshold
from modules.figure_data import save_figure_data

import matplotlib.pyplot as plt

# markdown figure description:
""" 

"""

paper_style()

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
alpha = 1e-30
delta = 1e-10

# Ecosystem types with estimated β and surplus ratio R
ecosystems = [
    {"label": "Grassland",         "beta": 1.2, "R": 3.0,  "color": "#2ca02c", "ls": "-"},
    {"label": "Temperate forest",  "beta": 1.5, "R": 2.0,  "color": "#1f77b4", "ls": "-"},
    {"label": "Tropical rainforest","beta": 2.0, "R": 1.3, "color": "#d62728", "ls": "-"},
    {"label": "Coral reef",        "beta": 2.5, "R": 1.25, "color": "#9467bd", "ls": "-"},
]

n_lambda = 200  # points along λ axis

# ---------------------------------------------------------------------------
# Compute recovery times for each ecosystem type
# ---------------------------------------------------------------------------
results = {}

for eco in ecosystems:
    beta = eco["beta"]
    R = eco["R"]

    N_c = tipping_threshold(alpha, beta, delta)
    # R = alpha * N_0^(beta-1) / delta, so N_0 = N_c * R^(1/(beta-1))
    N_0 = N_c * R ** (1.0 / (beta - 1.0))
    lam_star = 1.0 - N_c / N_0

    # λ values from 0.01 to 0.98*λ*
    lam_max = 0.98 * lam_star
    lam_vals = np.linspace(0.01, lam_max, n_lambda)

    T_vals = np.array([recovery_time(N_0, l, alpha, beta, delta, n_steps=5000)
                       for l in lam_vals])

    # Linear baseline: T_linear(λ) = λ * N_0 / F(N_0)
    T_linear = np.array([recovery_time_lower_bound(N_0, l, alpha, beta, delta)
                         for l in lam_vals])

    # Normalize to T(0.01) for visual comparison across ecosystems
    T_norm = T_vals / T_vals[0] if T_vals[0] > 0 else T_vals

    results[eco["label"]] = {
        "lam_vals": lam_vals,
        "lam_star": lam_star,
        "T_vals": T_vals,
        "T_linear": T_linear,
        "T_ratio": T_vals / np.maximum(T_linear, 1e-300),
        "T_norm": T_norm,
        "beta": beta,
        "R": R,
        "N_0": N_0,
        "N_c": N_c,
    }

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ===== Panel (a): Normalized recovery time vs. λ =====
ax = axes[0]

for eco in ecosystems:
    r = results[eco["label"]]
    ax.semilogy(r["lam_vals"] * 100, r["T_norm"],
                color=eco["color"], ls=eco["ls"], linewidth=2.5,
                label=f'{eco["label"]} ($\\beta={eco["beta"]}$, '
                      f'$\\lambda^*={r["lam_star"]*100:.0f}\\%$)')

    # Mark tipping point
    ax.axvline(x=r["lam_star"] * 100, color=eco["color"],
               ls=':', alpha=0.5, linewidth=1)

# Lovejoy-Nobre range
ax.axvspan(20, 25, alpha=0.12, color='#d62728', zorder=0)
ax.text(22.5, ax.get_ylim()[0] * 3, 'Lovejoy &\nNobre\n(2018)',
        ha='center', fontsize=8, color='#d62728', fontstyle='italic')

# Linear reference
lam_ref = np.linspace(0.01, 80, 100)
ax.semilogy(lam_ref, lam_ref / lam_ref[0], 'k--', alpha=0.3, linewidth=1,
            label='Linear reference')

ax.set_xlabel('Destruction Fraction $\\lambda$ (%)', fontsize=13)
ax.set_ylabel('Normalized Recovery Time $T(\\lambda) / T(1\\%)$', fontsize=13)
ax.set_title('(a) Recovery Time vs. Destruction Fraction', fontsize=14)
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(0, 85)
ax.set_ylim(0.8, 1e5)
ax.grid(True, alpha=0.3)

# ===== Panel (b): Superlinear penalty ratio =====
ax = axes[1]

for eco in ecosystems:
    r = results[eco["label"]]
    ax.plot(r["lam_vals"] * 100, r["T_ratio"],
            color=eco["color"], ls=eco["ls"], linewidth=2.5,
            label=f'{eco["label"]} ($\\beta={eco["beta"]}$)')

ax.axhline(y=1.0, color='black', ls='--', alpha=0.3, linewidth=1)
ax.text(40, 1.12, 'Linear recovery (ratio = 1)', fontsize=9, alpha=0.6, ha='left')

# Lovejoy-Nobre range
ax.axvspan(20, 25, alpha=0.12, color='#d62728', zorder=0)

ax.set_xlabel('Destruction Fraction $\\lambda$ (%)', fontsize=13)
ax.set_ylabel('Superlinear Penalty $T(\\lambda) / T_{\\mathrm{linear}}(\\lambda)$',
              fontsize=13)
ax.set_title('(b) Superlinear Recovery Penalty', fontsize=14)
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(0, 85)
ax.grid(True, alpha=0.3)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
plt.tight_layout()
out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'figures')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'fig_recovery_time.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

# Save data for reproducibility
save_figure_data(
    "recovery_time",
    ecosystems=[e["label"] for e in ecosystems],
    betas=[e["beta"] for e in ecosystems],
    surplus_ratios=[e["R"] for e in ecosystems],
    tipping_fractions=[results[e["label"]]["lam_star"] for e in ecosystems],
)
