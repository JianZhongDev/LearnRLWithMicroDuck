"""Consistent figure style and simple labelled block diagrams.

`flow_diagram` draws the "big picture" process with today's step highlighted.
Every lesson starts with one of these, so the learner always sees where the
current detail fits.

    flow_diagram(
        [("Observe", "joint angles, IMU"), ("Policy", "neural network"),
         ("Actuators", "PD + motor model"), ("Physics", "MuJoCo, 4 substeps")],
        highlight=3, loop_label="next observation",
        title="One environment step", path=out / "map.png")
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

COLORS = {
    "ink": "#1f2933",
    "muted": "#7b8794",
    "box": "#e8edf3",
    "edge": "#9aa5b1",
    "highlight": "#f0a33a",
    "highlight_fill": "#fff1dc",
    "blue": "#2f6fde",
    "orange": "#e8833a",
    "green": "#2e9e6b",
    "red": "#d64545",
    "purple": "#8e5bd8",
}
SERIES = [COLORS["blue"], COLORS["orange"], COLORS["green"], COLORS["purple"], COLORS["red"]]


def use_style() -> None:
    """Readable defaults: large fonts, light grid, no top/right spines."""
    plt.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 130,
            "font.size": 12,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.prop_cycle": matplotlib.cycler(color=SERIES),
            "legend.frameon": False,
        }
    )


def save_fig(fig, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved figure: {path}")
    return path


def _wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width)) if text else ""


def flow_diagram(
    steps: Sequence[str | tuple[str, str]],
    highlight: int | Sequence[int] | None = None,
    title: str = "",
    path: str | Path | None = None,
    loop_label: str | None = None,
    edge_labels: Sequence[str] | None = None,
    highlight_tag: str = "TODAY",
    box_width: float = 2.3,
    gap: float = 0.9,
):
    """Draw boxes left-to-right joined by arrows; optionally loop back to the start.

    steps        list of "Title" or ("Title", "short subtitle")
    highlight    index or indices of the step(s) this lesson zooms into
    loop_label   if given, draw a return arrow from the last box to the first
    edge_labels  optional text on each forward arrow (len(steps) - 1 entries)
    """
    use_style()
    items = [(s, "") if isinstance(s, str) else (s[0], s[1]) for s in steps]
    hl = set([highlight] if isinstance(highlight, int) else (highlight or []))
    n = len(items)
    box_h = 1.25
    total_w = n * box_width + (n - 1) * gap
    fig_h = 2.9 if loop_label else 2.3
    fig, ax = plt.subplots(figsize=(max(6.0, total_w * 1.05), fig_h))
    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(-1.35 if loop_label else -0.45, box_h + (0.9 if title else 0.5))
    ax.axis("off")

    centers = []
    for i, (name, sub) in enumerate(items):
        x0 = i * (box_width + gap)
        is_hl = i in hl
        box = FancyBboxPatch(
            (x0, 0),
            box_width,
            box_h,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            linewidth=2.6 if is_hl else 1.2,
            edgecolor=COLORS["highlight"] if is_hl else COLORS["edge"],
            facecolor=COLORS["highlight_fill"] if is_hl else COLORS["box"],
        )
        ax.add_patch(box)
        ax.text(x0 + box_width / 2, box_h * 0.68, _wrap(name, int(16 * box_width / 2.3)), ha="center", va="center",
                fontsize=12.5, fontweight="bold", color=COLORS["ink"])
        if sub:
            ax.text(x0 + box_width / 2, box_h * 0.27, _wrap(sub, int(24 * box_width / 2.3)), ha="center", va="center",
                    fontsize=9.5, color=COLORS["muted"])
        centers.append(x0 + box_width / 2)

    if hl and highlight_tag:
        lo, hi = min(hl), max(hl)
        x_left = lo * (box_width + gap)
        x_right = hi * (box_width + gap) + box_width
        if hi > lo:  # one bracket spanning the highlighted boxes
            y = box_h + 0.1
            ax.plot([x_left, x_left, x_right, x_right], [y, y + 0.08, y + 0.08, y],
                    color=COLORS["highlight"], lw=1.6)
        ax.text((x_left + x_right) / 2, box_h + 0.22, highlight_tag, ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", color=COLORS["highlight"])

    for i in range(n - 1):
        x_start = i * (box_width + gap) + box_width
        arrow = FancyArrowPatch((x_start + 0.05, box_h / 2), (x_start + gap - 0.05, box_h / 2),
                                arrowstyle="-|>", mutation_scale=16, color=COLORS["ink"], linewidth=1.4)
        ax.add_patch(arrow)
        if edge_labels and i < len(edge_labels) and edge_labels[i]:
            ax.text(x_start + gap / 2, box_h / 2 + 0.12, _wrap(edge_labels[i], 12), ha="center",
                    va="bottom", fontsize=8.5, color=COLORS["muted"])

    if loop_label:
        y = -0.55
        ax.add_patch(FancyArrowPatch((centers[-1], -0.02), (centers[-1], y), arrowstyle="-",
                                     color=COLORS["ink"], linewidth=1.4))
        ax.add_patch(FancyArrowPatch((centers[-1], y), (centers[0], y), arrowstyle="-",
                                     color=COLORS["ink"], linewidth=1.4))
        ax.add_patch(FancyArrowPatch((centers[0], y), (centers[0], -0.02), arrowstyle="-|>",
                                     mutation_scale=16, color=COLORS["ink"], linewidth=1.4))
        ax.text((centers[0] + centers[-1]) / 2, y - 0.12, loop_label, ha="center", va="top",
                fontsize=10, style="italic", color=COLORS["ink"])

    if title:
        ax.text(total_w / 2, box_h + 0.62, title, ha="center", va="bottom", fontsize=14,
                fontweight="bold", color=COLORS["ink"])
    if path is not None:
        save_fig(fig, path)
    return fig
