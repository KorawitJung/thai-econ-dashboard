"""Visual design system for the dashboard."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

NAVY = "#0f2a4a"
INK = "#1d2733"
MUTED = "#6b7785"
LINE = "#e3e7ec"
BG = "#f6f8fb"
CARD = "#ffffff"
BLUE = "#2563eb"
AMBER = "#e08a1e"
GREEN = "#15925a"
RED = "#d64545"
SAMPLE = "#c2410c"

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "axes.edgecolor": LINE,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.titlelocation": "left",
    "axes.titlepad": 10,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": LINE,
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "legend.frameon": False,
    "legend.fontsize": 8,
})


def card(fig, x, y, w, h, color=CARD, edge=LINE, accent=None):
    """Draw a rounded card in figure coordinates; optional left accent stripe."""
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, facecolor=color, edgecolor=edge,
                                      linewidth=0.8, zorder=0))
    if accent:
        fig.patches.append(FancyBboxPatch((x, y + 0.012), 0.004, h - 0.024, boxstyle="square,pad=0",
                                          transform=fig.transFigure, facecolor=accent, edgecolor="none",
                                          zorder=1))
