"""Lab <MM>/<Lxx> — <question in plain words>.

Run:              lab <MM>/<Lxx>
Change one thing: lab <MM>/<Lxx> <key>=<value>
List settings:    lab <MM>/<Lxx> help

Outputs (in results/<settings>/):
  robot.gif      <what it shows>
  <plot>.png     <what it shows>
  ../compare.png <comparison across every setting you have run>
"""

import numpy as np

import duckkit as dk

run = dk.lab_config(
    {"seconds": 3.0, "num_envs": 4, "<setting>": 0.0, "seed": 0},
    help={
        "seconds": "simulated time to run",
        "num_envs": "independent robot copies simulated in parallel",
        "<setting>": "<meaning, units>",
        "seed": "random seed",
    },
)
cfg = run.cfg

env = dk.make_env(num_envs=cfg.num_envs, seed=cfg.seed, render=True)
try:
    steps = int(round(cfg.seconds / env.step_dt))
    traj = dk.rollout(env, dk.zero_policy(env), steps=steps, render_every=2)
finally:
    env.close()

# 1. A short printed table: words for column names, units, a few meaningful rows.

# 2. Captioned GIF of env 0, red caption at the key event.
captions = [f"t={(s + 1) * traj.step_dt:.2f} s" for s in traj.frame_steps]
dk.save_gif(dk.caption_frames(traj.frames, captions), run.out / "robot.gif", fps=25)

# 3. One or two plots that answer the question; mark events; units on axes.
import matplotlib.pyplot as plt  # noqa: E402

dk.use_style()
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(traj.time, traj.tilt_deg[:, 0])
ax.set_xlabel("simulated time (s)")
ax.set_ylabel("<quantity (unit)>")
ax.set_title("<what the reader should see>")
dk.save_fig(fig, run.out / "<plot>.png")

# 4. Save data for comparison across runs, then plot all runs together.
np.savez(run.out / "signals.npz", t=traj.time, y=traj.tilt_deg)
