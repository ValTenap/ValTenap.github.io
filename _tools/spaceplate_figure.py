"""Spaceplate illustration for the website (indigo background, HeNe-red rays).
Run: python _tools/spaceplate_figure.py"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch

INK, ON, MUTED, RED, VIOLET = "#101b3a", "#e9ecf6", "#a8b0cc", "#ff5a4d", "#9d8cff"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img", "spaceplate_card.png")
plt.rcParams["font.family"] = "DejaVu Serif"

fig = plt.figure(figsize=(8, 6), facecolor=INK)
for row, sp in enumerate((False, True)):
    ax = fig.add_axes([0.05, 0.53 - row * 0.47, 0.9, 0.42]); ax.set_facecolor(INK)
    f, x1, t = 6.0, 1.6, 1.1
    L = f if not sp else f - 2.4
    d_eff = t + (f - L)
    lens = [[0, 1.25], [0.22, 0.95], [0.22, -0.95], [0, -1.25], [-0.22, -0.95], [-0.22, 0.95]]
    ax.add_patch(Polygon(lens, closed=True, facecolor="#2a3a6e", edgecolor=ON, lw=1))
    for y in np.linspace(-0.9, 0.9, 9):
        sl = -y / f
        if sp:
            ya = y + sl * x1; yb = ya + sl * d_eff
            xs, ys = [0.22, x1, x1 + t, L], [y, ya, yb, 0]
        else:
            xs, ys = [0.22, L], [y, 0]
        ax.plot(xs, ys, color=RED, lw=1.3, alpha=0.9, solid_capstyle="round")
        ax.plot(xs, ys, color=RED, lw=5, alpha=0.08)
    if sp:
        ax.add_patch(FancyBboxPatch((x1, -1.25), t, 2.5, boxstyle="round,pad=0,rounding_size=0.08",
                                    facecolor=VIOLET, alpha=0.18, edgecolor=VIOLET, lw=1.2))
        ax.text(x1 + t / 2, 1.42, "spaceplate", ha="center", color=VIOLET, fontsize=14, style="italic")
    ax.plot(L, 0, "o", color="white", ms=6, zorder=5)
    ax.plot(L, 0, "o", color=RED, ms=16, alpha=0.25, zorder=4)
    ax.annotate("", xy=(L, -1.55), xytext=(0, -1.55), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1))
    ax.text(L / 2, -1.95, "free space" if not sp else "shorter, same focus", ha="center", color=ON, fontsize=14, style="italic")
    ax.set_xlim(-0.6, 6.6); ax.set_ylim(-2.2, 1.7); ax.set_aspect("equal"); ax.axis("off")
fig.savefig(OUT, dpi=150, facecolor=INK)
print("saved", OUT)
