"""
Figure: Tipping Threshold Sensitivity (§7.5)
==============================================

Two-panel figure:
  (a) Tipping threshold λ* vs. generative surplus ratio R for different β
      values. The Lovejoy-Nobre 20-25% Amazon threshold is marked.
  (b) Maximum sustainable extraction rate h*/δN_0 vs. N_0/N_c for different β,
      showing how the safe extraction margin depends on stock surplus.

Output: output/figures/fig_tipping_threshold.png
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.plotting import paper_style
from modules.figure_data import save_figure_data

import matplotlib.pyplot as plt

# markdown figure description:
""" 
![Figure 7: Tipping Threshold Sensitivity. (a) Maximum destruction fraction $\lambda^*$ vs. generative surplus ratio $R$ for different rate-stock coupling exponents $\beta$. The shaded band marks the Lovejoy and Nobre [-@LovejoyNobre2018] estimate of 20-25% for the Amazon deforestation threshold; the diamond marks the calibration point ($R \approx 1.3$, $\beta \approx 2$). Low-$\beta$ systems (grasslands) tolerate far greater destruction at any given surplus ratio. (b) Normalized maximum sustainable extraction rate $h^*/(\delta\mathcal{N}_0)$ vs. stock level $\mathcal{N}_0/\mathcal{N}_c$. High-$\beta$ systems benefit disproportionately from operating above their tipping threshold, but are correspondingly more fragile when stock is reduced.](output/figures/fig_tipping_threshold.png)
"""

paper_style()

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
betas = [1.1, 1.2, 1.5, 2.0, 2.5, 3.0]
colors = ['#bcbd22', '#2ca02c', '#1f77b4', '#d62728', '#9467bd', '#8c564b']
labels_eco = {
    1.1: 'Microbial mat',
    1.2: 'Grassland',
    1.5: 'Temperate forest',
    2.0: 'Tropical rainforest',
    2.5: 'Coral reef',
    3.0: 'Neural tissue',
}

# Surplus ratio R = alpha * N_0^(beta-1) / delta
# lambda* = 1 - R^{-1/(beta-1)}
R_vals = np.linspace(1.01, 10.0, 500)

# ---------------------------------------------------------------------------
# Compute λ* vs R for each β
# ---------------------------------------------------------------------------
lam_star_data = {}
for beta in betas:
    lam_star = 1.0 - R_vals ** (-1.0 / (beta - 1.0))
    lam_star_data[beta] = lam_star

# ---------------------------------------------------------------------------
# Compute h*/δN_0 vs N_0/N_c for each β
# h* = alpha*N_0^beta - delta*N_0
# h*/delta*N_0 = alpha*N_0^(beta-1)/delta - 1 = R - 1
# So for β=anything, h*/(δN_0) = R - 1  (it's always just R-1!)
# But the *shape* of h*(N)/δN at varying N/N_c is more interesting:
# h*(N)/delta/N = alpha*N^(beta-1)/delta - 1
# With N/N_c = x, and N_c = (delta/alpha)^{1/(beta-1)}:
#   alpha*N^(beta-1)/delta = alpha*(x*N_c)^(beta-1)/delta = x^(beta-1)
# So h*/(delta*N) = x^(beta-1) - 1
# ---------------------------------------------------------------------------
x_vals = np.linspace(1.01, 5.0, 300)  # N/N_c

h_star_data = {}
for beta in betas:
    h_star = x_vals ** (beta - 1.0) - 1.0
    h_star_data[beta] = h_star

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ===== Panel (a): λ* vs R =====
ax = axes[0]

for beta, color in zip(betas, colors):
    eco_label = labels_eco.get(beta, '')
    label_str = f'$\\beta={beta}$'
    if eco_label:
        label_str += f' ({eco_label})'
    ax.plot(R_vals, lam_star_data[beta] * 100, color=color, linewidth=2.5,
            label=label_str)

# Lovejoy-Nobre band
ax.axhspan(20, 25, alpha=0.15, color='#d62728', zorder=0)
ax.text(6.5, 21.5, 'Lovejoy & Nobre (2018): 20–25%',
        fontsize=9, color='#d62728', ha='center', fontstyle='italic')

# Mark the calibration point: R ≈ 1.3, λ* ≈ 23% for β=2
ax.plot(1.3, 23, 'D', color='#d62728', markersize=8, zorder=5,
        markeredgecolor='black', markeredgewidth=0.8)
ax.annotate('Amazon\n($R \\approx 1.3$, $\\beta \\approx 2$)',
            xy=(1.3, 23), xytext=(2.5, 12),
            fontsize=9, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.2))

ax.set_xlabel('Generative Surplus Ratio $R = \\alpha\\mathcal{N}_0^{\\beta-1}/\\delta$',
              fontsize=13)
ax.set_ylabel('Tipping Threshold $\\lambda^*$ (%)', fontsize=13)
ax.set_title('(a) Tipping Threshold vs.\nGenerative Surplus', fontsize=14)
ax.legend(fontsize=8.5, loc='center right', bbox_to_anchor=(1.0, 0.45))
ax.set_xlim(1, 10)
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3)

# ===== Panel (b): Normalized MSY vs N/N_c =====
ax = axes[1]

for beta, color in zip(betas, colors):
    ax.plot(x_vals, h_star_data[beta], color=color, linewidth=2.5,
            label=f'$\\beta={beta}$')

ax.axhline(y=0, color='black', ls='-', alpha=0.3, linewidth=1)
ax.text(1.5, -0.15, 'Below: system in decline', fontsize=8, alpha=0.5)

ax.set_xlabel('Stock Ratio $\\mathcal{N}_0 / \\mathcal{N}_c$', fontsize=13)
ax.set_ylabel('Normalized Extraction $h^* / (\\delta\\mathcal{N}_0)$', fontsize=13)
ax.set_title('(b) Maximum Sustainable Extraction\nvs. Stock Level', fontsize=14)
ax.legend(fontsize=8.5, loc='upper left', bbox_to_anchor=(1.0, 1.0))
ax.set_xlim(1, 5)
ax.set_ylim(-0.2, 20)
ax.grid(True, alpha=0.3)

# Annotate: high β grows fast
ax.annotate('High $\\beta$: steep extraction growth',
            xy=(3.5, h_star_data[3.0][np.argmin(np.abs(x_vals - 3.5))]),
            xytext=(2.0, 14), fontsize=9,
            arrowprops=dict(arrowstyle='->', color='#8c564b', lw=1.2))

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
plt.tight_layout()
out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'figures')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'fig_tipping_threshold.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Saved: {out_path}")
plt.close()

# Save data for reproducibility
save_figure_data(
    "tipping_threshold",
    betas=betas,
    R_vals=R_vals,
    x_vals=x_vals,
    **{f"lam_star_beta_{b}": lam_star_data[b] for b in betas},
    **{f"h_star_beta_{b}": h_star_data[b] for b in betas},
)
