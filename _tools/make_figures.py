"""Generate the placeholder figures in assets/img/. Replace them with your own anytime.
Run:  python _tools/make_figures.py   (needs numpy, matplotlib, pillow)"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch, Polygon
from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")
os.makedirs(OUT, exist_ok=True)
INK = "#212529"

def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def vector_beam(ax, q=0.5, alpha0=0.0, n=13, cmap="hsv", show_bg=True):
    """Intensity donut + polarization ellipses of a q-plate vector beam."""
    x = np.linspace(-1.6, 1.6, 400); X, Y = np.meshgrid(x, x)
    R, PHI = np.hypot(X, Y), np.arctan2(Y, X)
    I = (R**2) * np.exp(-2 * R**2)
    ang = (q * PHI + alpha0) % np.pi
    if show_bg:
        rgba = plt.get_cmap(cmap)(ang / np.pi)
        rgba[..., :3] = 0.55 * rgba[..., :3] + 0.45  # pastel
        rgba[..., 3] = 0.85 * np.clip(I / I.max(), 0, 1) ** 0.8
        ax.imshow(rgba, extent=[-1.6, 1.6, -1.6, 1.6], origin="lower", interpolation="bilinear")
    g = np.linspace(-1.35, 1.35, n)
    for xi in g:
        for yi in g:
            r = np.hypot(xi, yi)
            w = r**2 * np.exp(-2 * r**2) / (0.5 * np.exp(-1))
            if w < 0.12:
                continue
            th = q * np.arctan2(yi, xi) + alpha0
            ax.add_patch(Ellipse((xi, yi), 0.17 * w**0.4, 0.035 * w**0.4,
                                 angle=np.degrees(th), color=INK, lw=0))
    ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_aspect("equal"); ax.axis("off")

# --- Home: q = 1/2 vector beam -------------------------------------------
fig, ax = plt.subplots(figsize=(6, 6))
vector_beam(ax, q=0.5, n=15)
save(fig, "home.png")

# --- Research 1: steganography (beam -> mask -> Poincare equatorial disk) --
fig, axs = plt.subplots(1, 3, figsize=(10, 3.4), gridspec_kw=dict(wspace=0.25))
vector_beam(axs[0], q=1.0, n=11)
axs[0].set_title("partially polarized\nvector beam", fontsize=15, color=INK)
# spatial mask: thin parametric curve (a triangle)
t = np.linspace(0, 2 * np.pi, 4)
tri = np.c_[0.9 * np.cos(t + np.pi / 2), 0.9 * np.sin(t + np.pi / 2)]
axs[1].add_patch(Rectangle((-1.6, -1.6), 3.2, 3.2, color=INK))
axs[1].plot(tri[:, 0], tri[:, 1], color="white", lw=3)
axs[1].set_xlim(-1.6, 1.6); axs[1].set_ylim(-1.6, 1.6); axs[1].set_aspect("equal"); axs[1].axis("off")
axs[1].set_title("spatial mask\n(the key)", fontsize=15, color=INK)
# Poincare sphere equatorial disk with recovered shape
ax = axs[2]; th = np.linspace(0, 2 * np.pi, 300)
ax.plot(np.cos(th), np.sin(th), color=INK, lw=1)
ax.plot(np.cos(th), 0.3 * np.sin(th), color=INK, lw=0.6, ls="--")
ax.plot([-1, 1], [0, 0], color="#adb5bd", lw=0.6); ax.plot([0, 0], [-1, 1], color="#adb5bd", lw=0.6)
pts = tri * 0.9; pts[:, 1] *= 0.3
rng = np.random.default_rng(1)
for a, b in zip(pts[:-1], pts[1:]):
    s = np.linspace(0, 1, 40)[:, None]; seg = a + s * (b - a) + rng.normal(0, 0.015, (40, 2))
    ax.scatter(seg[:, 0], seg[:, 1], s=6, color="#7048e8")
ax.text(1.05, 0, "$S_1$", fontsize=13, va="center", color=INK); ax.text(0, 1.06, "$S_3$", fontsize=13, ha="center", color=INK)
ax.set_xlim(-1.2, 1.25); ax.set_ylim(-1.2, 1.2); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("hidden shape on the\nPoincaré sphere", fontsize=15, color=INK)
fig.canvas.draw()
for a, b in ((axs[0], axs[1]), (axs[1], axs[2])):
    x0 = a.get_position().x1; x1 = b.get_position().x0; ym = (a.get_position().y0 + a.get_position().y1) / 2
    fig.patches.append(FancyArrowPatch((x0 + 0.004, ym), (x1 - 0.004, ym), transform=fig.transFigure,
                                       arrowstyle="-|>", mutation_scale=14, color="#868e96"))
save(fig, "research_steganography.png")

# --- Research 2: volume grating as a multiport beamsplitter ---------------
fig, ax = plt.subplots(figsize=(7, 4))
slab = Rectangle((-0.35, -1.4), 0.7, 2.8, facecolor="#f1f3f5", edgecolor=INK, lw=1.2)
ax.add_patch(slab)
for k in np.linspace(-1.6, 1.6, 26):
    ln, = ax.plot([-0.35, 0.35], [k - 0.12, k + 0.12], color="#adb5bd", lw=0.8)
    ln.set_clip_path(slab)
cols = ["#e8590c", "#1c7ed6", "#2f9e44"]
ins = [(-3, 0.9), (-3, -0.9)]
outs = [(3, 1.3), (3, 0.0), (3, -1.3)]
for (x, y), c in zip(ins, cols):
    ax.annotate("", xy=(-0.35, 0), xytext=(x, y), arrowprops=dict(arrowstyle="-|>", color=c, lw=2.2))
for (x, y), c in zip(outs, cols + ["#7048e8"]):
    ax.annotate("", xy=(x, y), xytext=(0.35, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
ax.text(-3.05, 1.05, "mode 1", fontsize=10, color=cols[0], ha="left")
ax.text(-3.05, -1.25, "mode 2", fontsize=10, color=cols[1], ha="left")
for (x, y), lab in zip(outs, ["port 1", "port 2", "port 3"]):
    ax.text(x + 0.08, y, lab, fontsize=10, va="center", color=INK)
ax.text(0, -1.65, "volume holographic grating", fontsize=10, ha="center", color=INK)
ax.set_xlim(-3.2, 3.8); ax.set_ylim(-1.9, 1.7); ax.set_aspect("equal"); ax.axis("off")
save(fig, "research_gratings.png")

# --- Research 3: spaceplate compressing propagation -----------------------
fig, axs = plt.subplots(1, 2, figsize=(9, 2.6), gridspec_kw=dict(wspace=0.08))
for ax, sp in zip(axs, (False, True)):
    L = 2.0 if sp else 3.6
    ax.add_patch(Polygon([[0, 1], [0.15, 0.8], [0.15, -0.8], [0, -1], [-0.15, -0.8], [-0.15, 0.8]],
                         closed=True, facecolor="#e7f5ff", edgecolor=INK, lw=1))
    f, x1, t = 3.6, 0.9, 0.6
    d_eff = t + (f - L)          # free-space length emulated by the plate
    for y in np.linspace(-0.75, 0.75, 7):
        sl = -y / f              # ray slope outside the plate
        if sp:
            ya = y + sl * x1; yb = ya + sl * d_eff
            ax.plot([0.15, x1, x1 + t, L], [y, ya, yb, 0], color="#e8590c", lw=1)
        else:
            ax.plot([0.15, L], [y, 0], color="#e8590c", lw=1)
    if sp:
        ax.add_patch(Rectangle((0.9, -1), 0.6, 2, facecolor="#f3f0ff", edgecolor="#7048e8", lw=1.2))
        ax.text(1.2, 1.12, "spaceplate", ha="center", fontsize=11, color="#7048e8")
    ax.plot(L, 0, "o", color=INK, ms=4)
    ax.annotate("", xy=(L, -1.25), xytext=(0, -1.25), arrowprops=dict(arrowstyle="<->", color="#868e96"))
    ax.text(L / 2, -1.55, "focal distance" if not sp else "shorter, same focus", ha="center", fontsize=11, color=INK)
    ax.set_xlim(-0.3, 4.0); ax.set_ylim(-1.7, 1.3); ax.set_aspect("equal"); ax.axis("off")
save(fig, "research_spaceplates.png")

# --- Favicons ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(2, 2))
vector_beam(ax, q=0.5, n=7)
save(fig, "_icon.png")
im = Image.open(os.path.join(OUT, "_icon.png")).convert("RGBA")
side = min(im.size); im = im.crop((0, 0, side, side))
im.resize((152, 152)).save(os.path.join(OUT, "..", "apple-icon-152x152.png"))
im.save(os.path.join(OUT, "..", "favicon.ico"), sizes=[(32, 32), (48, 48)])
os.remove(os.path.join(OUT, "_icon.png"))
print("done")
