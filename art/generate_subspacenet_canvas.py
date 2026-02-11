from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon


def generate_poster(output_path: Path) -> None:
    width_px, height_px = 1920, 1080
    dpi = 120
    fig_w, fig_h = width_px / dpi, height_px / dpi

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    bg = "#0f1116"
    slate = "#1f2a3d"
    grid = "#2b3a55"
    cyan = "#55c3d8"
    amber = "#f1a66a"
    haze = "#b8c2d6"
    white = "#f4f6f8"

    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    # Background vertical gradient for depth.
    grad = np.linspace(0.18, 0.0, 1080).reshape(-1, 1)
    grad_img = np.dstack(
        [
            np.full_like(grad, 31 / 255.0),
            np.full_like(grad, 42 / 255.0),
            np.full_like(grad, 61 / 255.0),
            grad,
        ]
    )
    ax.imshow(grad_img, extent=[0, 1, 0, 1], origin="lower", interpolation="bicubic")

    # Structural lattice lines.
    for x in np.linspace(0.08, 0.92, 11):
        lw = 1.3 if abs(x - 0.5) < 0.005 else 0.5
        alpha = 0.22 if lw > 1 else 0.14
        ax.plot([x, x], [0.08, 0.92], color=grid, lw=lw, alpha=alpha)
    for y in np.linspace(0.1, 0.9, 7):
        ax.plot([0.07, 0.93], [y, y], color=grid, lw=0.5, alpha=0.14)

    # Primary subspace pane.
    pane = Polygon(
        [[0.11, 0.2], [0.55, 0.2], [0.84, 0.72], [0.4, 0.72]],
        closed=True,
        facecolor=slate,
        edgecolor=cyan,
        linewidth=1.2,
        alpha=0.22,
    )
    ax.add_patch(pane)

    # Reference anchors.
    for cx, cy, r, a in [
        (0.2, 0.78, 0.11, 0.14),
        (0.79, 0.24, 0.16, 0.11),
        (0.66, 0.84, 0.06, 0.17),
    ]:
        ax.add_patch(Circle((cx, cy), r, facecolor=slate, edgecolor=cyan, lw=0.9, alpha=a))

    # Trajectory with spatiotemporal uncertainty envelopes.
    t = np.linspace(0, 1, 500)
    x = 0.11 + 0.77 * t
    y = 0.22 + 0.47 * t + 0.055 * np.sin(8.2 * t + 0.4)
    sigma = 0.015 + 0.03 * (0.2 + 0.8 * t) * (1 + 0.35 * np.sin(6.0 * t))

    for m, alpha in [(2.2, 0.07), (1.45, 0.12), (0.75, 0.18)]:
        ax.fill_between(x, y - m * sigma, y + m * sigma, color=haze, alpha=alpha, linewidth=0)

    # Multi-hypothesis trajectories.
    for k, phase in enumerate([0.0, 0.65, 1.25]):
        yk = y + (0.01 + 0.006 * k) * np.sin(14 * t + phase) - 0.005 * k
        col = cyan if k == 0 else ("#7ad0e2" if k == 1 else "#9adbe8")
        ax.plot(x, yk, color=col, lw=1.25 if k == 0 else 0.9, alpha=0.88 if k == 0 else 0.5)

    # Highlight current state and forecast target.
    ax.scatter([x[65]], [y[65]], s=45, color=white, edgecolor=bg, linewidth=0.8, zorder=5)
    ax.scatter([x[-1]], [y[-1]], s=85, color=amber, edgecolor=bg, linewidth=1.0, zorder=6)

    # Sparse ticks to imply temporal cadence.
    tick_idx = np.linspace(45, 460, 16).astype(int)
    for i in tick_idx:
        nx = x[min(i + 1, len(x) - 1)] - x[max(i - 1, 0)]
        ny = y[min(i + 1, len(y) - 1)] - y[max(i - 1, 0)]
        norm = np.hypot(nx, ny) + 1e-8
        px, py = -ny / norm, nx / norm
        tick_len = 0.008
        ax.plot(
            [x[i] - px * tick_len, x[i] + px * tick_len],
            [y[i] - py * tick_len, y[i] + py * tick_len],
            color=cyan,
            lw=0.5,
            alpha=0.35,
        )

    ax.text(
        0.08,
        0.085,
        "SubspaceNet",
        fontsize=62,
        color=white,
        fontweight="semibold",
        family="DejaVu Sans",
        ha="left",
        va="baseline",
    )
    ax.text(
        0.081,
        0.05,
        "Forecasting Motion Under Spatiotemporal Uncertainty",
        fontsize=18,
        color="#c8d1dd",
        family="DejaVu Sans",
        ha="left",
        va="baseline",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), dpi=dpi)
    plt.close(fig)


if __name__ == "__main__":
    generate_poster(Path("art/subspacenet_canvas_poster_1920x1080.png"))
