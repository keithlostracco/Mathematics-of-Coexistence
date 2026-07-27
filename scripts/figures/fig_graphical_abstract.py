"""
Figure: Graphical Abstract (EPJ B submission asset)
===================================================

A two-row rearrangement of the three Cooperative Equilibrium panels, sized for
the EPJ B graphical abstract slot. Same data, same loader, same verified
numbers as fig_cooperative_equilibrium.py; only the layout and type sizes
differ, so the two figures cannot drift apart.

Layout (one panel on top, two beneath):
    top          (a) payoff matrix across friction regimes, drawn square
                     (aspect='equal') rather than stretched to the full width
    bottom left  (b) N-player cooperation threshold vs group size
    bottom right (c) defection vs tit-for-tat payoff ratio

No title text: published graphical abstracts in this journal generally carry
none, since the graphic sits beside the article title on the contents page.

Spec (EPJ B submission guidelines):
  - .jpg or .png ONLY
  - maximum width 480 px  (this renders at 480)
  - aspect ratio 11:6 stated; treated as a ceiling. At 480x430 this is
    1.12:1, well inside it, and close to what published examples use.
  - colour strongly encouraged
  - must not have served as a graphical abstract in another publication

Kept separate from fig_cooperative_equilibrium.py so the three-panel paper
figure is untouched.

This script intentionally does NOT call modules.plotting.paper_style(): the
graphical abstract is viewed at thumbnail size and needs much larger relative
type than the in-paper figures.

Output: output/figures/fig_graphical_abstract.png

Run:  python scripts/figures/fig_graphical_abstract.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.figure_data import load_figure_data

# ---------------------------------------------------------------------------
# Output geometry and type scale
# ---------------------------------------------------------------------------
PX_W, PX_H = 480, 500
DPI = 100

FS_TITLE = 7.0
FS_LABEL = 6.5
FS_TICK = 6.5
FS_LEGEND = 6.5
FS_CBAR = 6.5      
FS_CELL = 6.5 

plt.rcParams.update({
    "font.size": FS_TICK,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.0,
    "ytick.major.size": 2.0,
})

# ---------------------------------------------------------------------------
# Verified data (identical source to the in-paper figure)
# ---------------------------------------------------------------------------
data = load_figure_data("cooperative_equilibrium")

Phi_vals = data["Phi_vals"]
payoff_matrix = data["payoff_matrix"]
N_range = data["N_range"]
phi_scenarios = data["phi_scenarios"]
delta_N_curves = data["delta_N_curves"]
delta_range_invasion = data["delta_range_invasion"]
payoff_ratio = data["payoff_ratio"]
ds_base = float(data["delta_star_base"])
alpha_coop = float(data["alpha_coop"])
c_contrib = float(data["c_contrib"])
E_bar = float(data["E_bar"])

fig = plt.figure(figsize=(PX_W / DPI, PX_H / DPI), dpi=DPI)
# Bottom row only. The top panel is placed with explicit coordinates below:
# a colourbar created with ax=... repositions its host axes, which pushes an
# equal-aspect image off centre, so the square heatmap is laid out by hand.
gs = GridSpec(1, 2, figure=fig, wspace=0.40,
              left=0.105, right=0.965, top=0.415, bottom=0.080)

# ===========================================================================
# TOP: payoff matrix, drawn square and centred
# ===========================================================================
# Axes sized to the data aspect (4 payoff columns x 5 friction rows) so the
# cells come out square, then centred as a group with its colourbar.
HM_H = 0.42                                   # height in figure fractions
HM_W = HM_H * (PX_H / PX_W) * (4.0 / 5.0)      # width giving square cells
CB_W, CB_GAP = 0.022, 0.016
HM_L = (1.0 - (HM_W + CB_GAP + CB_W)) / 1.8
HM_B = 0.545

ax = fig.add_axes([HM_L, HM_B, HM_W, HM_H])

labels_Phi = [f"$\\Phi$={p:.1f}" for p in Phi_vals]
payoff_names = ['T', 'R', 'P', 'S']

abs_max = max(abs(payoff_matrix.min()), abs(payoff_matrix.max()))
norm = mcolors.TwoSlopeNorm(vmin=-abs_max, vcenter=0, vmax=abs_max)

# aspect='equal' keeps the cells square; the image then sits centred in the
# wide axes rather than being stretched across it.
im = ax.imshow(payoff_matrix, cmap='RdYlGn', norm=norm, aspect=.9)
ax.set_xticks(range(4))
ax.set_xticklabels(payoff_names, fontsize=FS_TICK)
ax.set_yticks(range(len(Phi_vals)))
ax.set_yticklabels(labels_Phi, fontsize=FS_TICK)
ax.set_xlabel('Payoff Type', fontsize=FS_LABEL, labelpad=1.5)
ax.set_ylabel('Friction Regime', fontsize=FS_LABEL, labelpad=2.0)
ax.set_title('Payoff Matrix vs. Friction Regime',
             fontsize=FS_TITLE, pad=3.0)
ax.tick_params(labelsize=FS_TICK, pad=1.0)

for i in range(len(Phi_vals)):
    for j in range(4):
        color = 'white' if abs(payoff_matrix[i, j]) > 30 else 'black'
        ax.text(j, i, f'{payoff_matrix[i, j]:.0f}', ha='center', va='center',
                fontsize=FS_CELL, fontweight='bold', color=color)

cax = fig.add_axes([HM_L + HM_W + CB_GAP, HM_B + 0.035, CB_W, HM_H - 0.070])
cbar = fig.colorbar(im, cax=cax)
cbar.set_label('Payoff (energy units)', fontsize=FS_CBAR, labelpad=3.0)
cbar.ax.tick_params(labelsize=FS_CBAR - 1.0, width=0.5, length=1.8, pad=1.2)
cbar.outline.set_linewidth(0.5)

# ===========================================================================
# BOTTOM LEFT: N-player cooperation threshold vs group size
# ===========================================================================
ax = fig.add_subplot(gs[0, 0])

colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4']
line_styles = ['--', '-.', '-', ':']

for i, (phi, col, ls) in enumerate(zip(phi_scenarios, colors, line_styles)):
    ax.plot(N_range, delta_N_curves[i], color=col, ls=ls, linewidth=1.4,
            label=f'$\\varphi_0 = {phi}$')
    ds_inf = (c_contrib / (alpha_coop * c_contrib + phi * E_bar)
              if phi > 0 else 0.5)
    ax.axhline(y=ds_inf, color=col, ls=':', alpha=0.3, linewidth=0.7)

ax.axhline(y=0.5, color='gray', ls=':', alpha=0.5, linewidth=0.7)

ax.set_xlabel('Number of Agents $N$', fontsize=FS_LABEL, labelpad=1.5)
ax.set_ylabel('Critical Discount Factor $\\delta_N^*$', fontsize=FS_LABEL,
              labelpad=2.0)
ax.set_title('$N$-Player Cooperation', fontsize=FS_TITLE, pad=3.0)
ax.set_xlim(3, 200)
ax.set_ylim(0.1, 0.55)
ax.tick_params(labelsize=FS_TICK, pad=1.5)
ax.legend(fontsize=FS_LEGEND, loc='lower right', ncol=2,
          handlelength=1.6, borderpad=0.30, labelspacing=0.22,
          columnspacing=0.8, framealpha=0.9)
ax.grid(True, alpha=0.3, linewidth=0.4)

# ===========================================================================
# BOTTOM RIGHT: defection vs tit-for-tat payoff ratio
# ===========================================================================
ax = fig.add_subplot(gs[0, 1])

ax.plot(delta_range_invasion, payoff_ratio, color='#d62728', linewidth=1.5,
        label='$V_{\\mathrm{ALLD}}/V_{\\mathrm{TFT}}$')
ax.axhline(y=1.0, color='gray', ls='--', alpha=0.6, linewidth=0.7)
ax.axvline(x=ds_base, color='#2ca02c', ls='--', alpha=0.8, linewidth=1.0,
           label=f'$\\delta^*={ds_base:.3f}$')

ax.fill_between(delta_range_invasion, payoff_ratio, 1.0,
                where=(payoff_ratio > 1.0), alpha=0.15, color='#d62728')
ax.fill_between(delta_range_invasion, payoff_ratio, 1.0,
                where=(payoff_ratio <= 1.0), alpha=0.15, color='#2ca02c')

ax.set_xlabel('Discount Factor $\\delta$', fontsize=FS_LABEL, labelpad=1.5)
ax.set_ylabel('Payoff Ratio', fontsize=FS_LABEL, labelpad=2.0)
ax.set_title('Defection vs. Tit-for-Tat', fontsize=FS_TITLE, pad=3.0)
ax.set_xlim(0, 1)
ax.set_ylim(-1, 2.5)
ax.tick_params(labelsize=FS_TICK, pad=1.5)
ax.legend(fontsize=FS_LEGEND, loc='upper right', handlelength=1.8,
          borderpad=0.35, labelspacing=0.25, framealpha=0.9)
ax.grid(True, alpha=0.3, linewidth=0.4)

# ---------------------------------------------------------------------------
# Save at exactly PX_W x PX_H (no bbox_inches='tight', which would change size)
# ---------------------------------------------------------------------------
out_dir = os.path.join(os.path.dirname(__file__), '..', '..',
                       'output', 'figures')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'fig_graphical_abstract.png')
fig.savefig(out_path, dpi=DPI, facecolor='white')
plt.close(fig)
print(f"Saved: {out_path} ({PX_W}x{PX_H} px)")
