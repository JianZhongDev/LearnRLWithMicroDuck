"""Make the README's animated figure from real lab data, with no robot rendering.

Left: a schematic bar that leans by the trunk tilt measured for robot copy 0.
Right: the measured tilt of all copies over time, drawn as the lab ran.
The numbers come from `lab 08/L01`; the drawing is a plain matplotlib schematic,
so the image is entirely this repository's own work (MIT).

    lab 08/L01
    lab py docs/images/make_hero.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import duckkit as dk

HERE = Path(__file__).resolve().parent
DATA = (dk.LEARNING_ROOT / "08-microduck-task-lifecycle" / "lessons" / "L01-one-env-step"
        / "results" / "default" / "signals.npz")
if not DATA.exists():
    raise SystemExit("Run `lab 08/L01` first: this figure is drawn from that lab's results.")

data = np.load(DATA)
t, tilt, done = data["t"], data["tilt"], data["done"]
steps, copies = tilt.shape
LIMIT = 70.0
C = dk.COLORS
SERIES = [C["blue"], C["orange"], C["green"], C["purple"]]

dk.use_style()
frames = []
flash = 0
shown_tilt = float(tilt[0, 0])
for k in range(0, steps, 2):
    if done[max(0, k - 1):k + 1, 0].any():
        flash = 5                                   # show "ended" for a few frames
    # After an ending the recorded tilt already belongs to the reset robot.
    shown_tilt = float(tilt[k, 0])
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [1, 1.9]})

    # Left: schematic bar leaning by the measured tilt.
    ax_l.set_xlim(-1.25, 1.25)
    ax_l.set_ylim(-0.25, 1.45)
    ax_l.set_aspect("equal")
    ax_l.axis("off")
    ax_l.plot([-1.2, 1.2], [0, 0], color=C["ink"], lw=2)
    ax_l.plot([0, 0], [0, 1.25], color=C["edge"], lw=1, ls=":")
    angle = np.radians(shown_tilt)
    tip = np.array([np.sin(angle), np.cos(angle)]) * 1.05
    color = C["red"] if flash else C["blue"]
    ax_l.plot([0, tip[0]], [0, tip[1]], color=color, lw=9, solid_capstyle="round")
    ax_l.scatter([tip[0]], [tip[1]], s=420, color=color, zorder=3)
    limit = np.radians(LIMIT)
    ax_l.plot([0, np.sin(limit) * 1.25], [0, np.cos(limit) * 1.25], color=C["red"], lw=1.2, ls="--")
    ax_l.text(np.sin(limit) * 1.27, np.cos(limit) * 1.27 + 0.04, "fall limit 70°", color=C["red"], fontsize=9,
              ha="right", va="bottom")
    ax_l.set_title("Copy 0: trunk tilt (schematic)", fontsize=11.5)
    label = "episode ended → reset" if flash else f"tilt = {shown_tilt:4.0f}°"
    ax_l.text(0, -0.2, label, ha="center", va="center", fontsize=11.5, fontweight="bold", color=color)

    # Right: measured tilt of every copy so far.
    for e in range(copies):
        ax_r.plot(t[:k + 1], tilt[:k + 1, e], lw=1.8, color=SERIES[e % len(SERIES)], label=f"copy {e}")
        ax_r.scatter([t[k]], [tilt[k, e]], s=22, color=SERIES[e % len(SERIES)], zorder=3)
    ax_r.axhline(LIMIT, color=C["red"], ls="--", lw=1.2)
    ax_r.set_xlim(0, float(t[-1]))
    ax_r.set_ylim(-3, 80)
    ax_r.set_xlabel("simulated time (s)")
    ax_r.set_ylabel("trunk tilt (degrees)")
    ax_r.set_title("No policy: every copy tips over, is reset, and tips again", fontsize=11.5)
    ax_r.legend(ncol=copies, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    fig.tight_layout()
    fig.canvas.draw()
    frames.append(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
    plt.close(fig)
    flash = max(0, flash - 1)

dk.save_gif(frames, HERE / "lab_tilt.gif", fps=16, hold_last=2.0)
