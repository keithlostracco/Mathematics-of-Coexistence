"""Shared plotting utilities for paper figures."""

import matplotlib.pyplot as plt


def paper_style():
    """Apply consistent figure styling for the paper."""
    plt.rcParams.update({
        "figure.figsize": (8, 5),
        "font.size": 12,
        "font.family": "serif",
        "axes.labelsize": 14,
        "axes.titlesize": 14,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })
