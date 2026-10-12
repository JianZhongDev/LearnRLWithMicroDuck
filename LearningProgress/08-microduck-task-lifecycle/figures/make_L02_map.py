"""Draw the L02 module map as a schematic with the reset branch explicit."""
import duckkit as dk
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

dk.use_style()
fig, ax = plt.subplots(figsize=(12, 4.2))
ax.set(xlim=(-0.2, 12), ylim=(-0.3, 4.1))
ax.axis("off")


def box(x, y, w, title, subtitle, today=False):
    ax.add_patch(FancyBboxPatch((x, y), w, 0.95, boxstyle="round,pad=0.04",
                 fc="#fff1dc" if today else "#e8edf3",
                 ec="#e8833a" if today else "#9aa5b1", lw=2 if today else 1))
    ax.text(x+w/2, y+0.62, title, ha="center", va="center", weight="bold", fontsize=12)
    ax.text(x+w/2, y+0.25, subtitle, ha="center", va="center", fontsize=10)


def arrow(points, label=None, label_xy=None):
    xs, ys = zip(*points)
    ax.plot(xs[:-1], ys[:-1], color="#1f2933", lw=1.4)
    ax.annotate("", xy=points[-1], xytext=points[-2], arrowprops=dict(arrowstyle="->", lw=1.4))
    if label:
        ax.text(*label_xy, label, ha="center", fontsize=10)


box(0.2, 1.8, 2, "Observe", "robot readings")
box(3, 1.8, 2, "Policy acts", "joint targets")
box(5.8, 1.8, 2, "Simulate", "robot moves")
box(8.6, 1.8, 2.8, "Score & check", "reward + episode ended?", True)
box(4.4, 0, 3.4, "Reset ended copies", "new pose; episode age = 0", True)
for x in [2.2, 5, 7.8]:
    arrow([(x, 2.3), (x+0.8, 2.3)])
arrow([(10, 2.8), (10, 3.25), (1.2, 3.25), (1.2, 2.8)], "No: same episode continues", (5.6, 3.4))
arrow([(10, 1.8), (10, 0.5), (7.8, 0.5)], "Yes", (10.6, 1.15))
arrow([(4.4, 0.5), (1.2, 0.5), (1.2, 1.8)], "new episode", (2.7, 0.7))
ax.text(5.8, 3.95, "Module 08: simulator to reinforcement learning environment",
        ha="center", fontsize=15, weight="bold")
ax.text(5.8, -0.25, "Schematic | Today: ending checks and reset (orange)", ha="center", fontsize=10)
dk.save_fig(fig, Path(__file__).with_name("map_L02.png"))
