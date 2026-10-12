"""Concept figures for Module 08 (no simulation needed; runs in a few seconds).

Run from the repository root:  lab py LearningProgress/08-microduck-task-lifecycle/figures/make_figures.py
Makes:
  map_L01.png                   the module's big-picture loop with lesson 1's part highlighted
                                (map_L02..L05.png are drawn by make_L02_map.py .. make_L05_map.py)
  step_timeline.png             what happens inside ONE env.step(), on a time axis
  steps_to_batch.png            how many robots x many steps become one training batch
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import duckkit as dk

HERE = Path(__file__).resolve().parent

LOOP = [
    ("Reset", "choose a start pose"),
    ("Observe", "sensors -> 61 numbers"),
    ("Policy acts", "61 numbers -> 14 joint targets"),
    ("Simulate", "4 physics steps x 5 ms"),
    ("Score & check", "reward; fell? time up?"),
]
LESSON_HIGHLIGHT = {
    "L01": ([1, 2, 3, 4], "TODAY: one full step"),
}

for lesson, (hl, tag) in LESSON_HIGHLIGHT.items():
    dk.flow_diagram(
        LOOP, highlight=hl, highlight_tag=tag,
        loop_label="repeat every 20 ms; a robot whose episode ended goes back to Reset",
        title="Module 08: how a simulator becomes an RL environment",
        path=HERE / f"map_{lesson}.png",
    )

# ---- What happens inside one env.step(): a 20 ms timeline -----------------------------
dk.use_style()
fig, ax = plt.subplots(figsize=(11, 3.9))
ax.set_xlim(-6, 31)
ax.set_ylim(-2.3, 3.2)
ax.axis("off")
C = dk.COLORS


def block(x, y, w, h, text, fc, ec, size=10.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.3",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            fontweight="bold" if bold else "normal", color=C["ink"])


# action arrives
block(-5.6, 0.2, 4.6, 1.3, "action in\n(14 joint\ntargets)", "#e3f0ff", C["blue"], bold=True)
ax.annotate("", xy=(0, 0.85), xytext=(-1.0, 0.85), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.5))
# four physics substeps
for k in range(4):
    block(5 * k + 0.1, 0.2, 4.8, 1.3, f"physics\nstep {k + 1}\n(5 ms)", C["box"], C["edge"])
ax.text(10, 1.9, "same joint targets held for all four physics steps", ha="center", fontsize=10.5,
        color=C["muted"], style="italic")
# after physics
block(20.4, 0.2, 4.6, 1.3, "check:\nfell? time up?\n+ reward", C["highlight_fill"], C["highlight"])
block(25.4, 0.2, 5.4, 1.3, "reset robots\nthat ended,\nthen observe", "#e6f6ee", C["green"])
# time axis
ax.annotate("", xy=(20.2, -0.45), xytext=(0, -0.45), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.2))
for ms in (0, 5, 10, 15, 20):
    ax.plot([ms, ms], [-0.55, -0.35], color=C["ink"], lw=1.2)
    ax.text(ms, -0.8, f"{ms} ms", ha="center", va="top", fontsize=10)
ax.text(10, -1.55, "simulated time inside ONE env.step(): 4 x 5 ms = 20 ms  ->  50 decisions per second",
        ha="center", fontsize=11.5, fontweight="bold", color=C["ink"])
ax.text(27.8, -0.75, "no time\npasses here", ha="center", va="top", fontsize=9.5, color=C["muted"])
ax.text(12.5, 2.75, "Inside one env.step(action)", ha="center", fontsize=14, fontweight="bold", color=C["ink"])
dk.save_fig(fig, HERE / "step_timeline.png")

# ---- Many robots x many steps -> one training batch -------------------------------------
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.axis("off")
ax.set_xlim(0, 20)
ax.set_ylim(0, 7.5)
n_env, n_step = 6, 10
for e in range(n_env):
    for s in range(n_step):
        ax.add_patch(FancyBboxPatch((0.6 + s * 0.8, 0.8 + e * 0.9), 0.65, 0.7,
                                    boxstyle="round,pad=0.01,rounding_size=0.08",
                                    fc="#e3f0ff", ec=C["blue"], lw=0.8))
    ax.text(0.45, 1.15 + e * 0.9, f"robot {e}", ha="right", va="center", fontsize=9)
ax.annotate("", xy=(8.6, 0.45), xytext=(0.6, 0.45), arrowprops=dict(arrowstyle="-|>", color=C["ink"]))
ax.text(4.6, 0.05, "policy steps (time)", ha="center", fontsize=10)
ax.text(4.6, 6.75, "each square = one transition:\nobservation, action, reward, ended?", ha="center", fontsize=10)
ax.annotate("", xy=(12.2, 3.6), xytext=(9.4, 3.6), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=2))
block_kw = dict(boxstyle="round,pad=0.02,rounding_size=0.3", lw=1.6)
ax.add_patch(FancyBboxPatch((12.4, 2.4), 6.8, 2.4, fc=C["highlight_fill"], ec=C["highlight"], **block_kw))
ax.text(15.8, 3.6, "training batch\n= robots x steps transitions\n-> PPO update (Module 07)", ha="center",
        va="center", fontsize=11, fontweight="bold", color=C["ink"])
ax.text(15.8, 1.6, "MicroDuck walking: robots x 24 steps per update", ha="center", fontsize=9.5, color=C["muted"])
dk.save_fig(fig, HERE / "steps_to_batch.png")
