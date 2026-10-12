"""Lab 08/L01 — watch what one env.step() does, many times in a row.

Question: when the policy hands the environment an action, what comes back,
and how much simulated time passes?

Run:              lab 08/L01
Change one thing: lab 08/L01 action_noise=0.3
List settings:    lab 08/L01 help

Outputs (in results/<settings>/):
  robot.gif      environment 0 as seen by a camera; red caption = episode ended this step
  signals.png    trunk height, trunk tilt and reward for every environment over time
  summary.json   timing, interface sizes and episode endings
  ../compare.png env-0 tilt for every setting you have run so far
"""

import json

import numpy as np

import duckkit as dk
from duckkit.sim import describe_env

run = dk.lab_config(
    {
        "seconds": 4.0,
        "num_envs": 4,
        "action_noise": 0.0,
        "hold_steps": 1,
        "seed": 0,
        "config": "train",
    },
    help={
        "seconds": "simulated time to run",
        "num_envs": "how many independent robot copies to simulate in parallel",
        "action_noise": "std-dev (radians) of random joint-target offsets; 0 = hold the default pose",
        "hold_steps": "keep each random action for this many policy steps",
        "seed": "random seed for resets and noise",
        "config": "train = training config (random pushes, randomized mass/friction); play = the task's evaluation config",
    },
)
cfg = run.cfg

# 1. Build the environment from the registered MicroDuck walking task (read-only source).
if cfg.config not in ("train", "play"):
    raise SystemExit("config must be train or play")
env = dk.make_env(num_envs=cfg.num_envs, seed=cfg.seed, render=True, play=(cfg.config == "play"))
try:
    info = describe_env(env)
    steps = int(round(cfg.seconds / info["policy_dt_s"]))
    policy = (dk.zero_policy(env) if cfg.action_noise == 0
              else dk.noise_policy(env, cfg.action_noise, seed=cfg.seed, hold_steps=cfg.hold_steps))

    # 2. The loop under study: action in -> env.step -> observation, reward, done out.
    traj = dk.rollout(env, policy, steps=steps, render_every=2)
finally:
    env.close()

t = traj.time
done = traj.done

# 3. Print the step anatomy for the first steps and every episode ending.
print(f"\nOne env.step = {traj.decimation} physics substeps x {traj.physics_dt*1000:.0f} ms "
      f"= {traj.step_dt*1000:.0f} ms of simulated time  ({1/traj.step_dt:.0f} policy decisions per second)")
print(f"Policy input (actor observation): {info['observation_groups']['actor'][1]} numbers per robot; "
      f"output (action): {info['action_dim']} joint-target offsets per robot\n")
print(" step  time_s  env  |action|  reward   height_m  tilt_deg  terminated  truncated  episode_step")
rows = [(s, e) for s in range(min(3, steps)) for e in range(min(2, cfg.num_envs))]
rows += [(s, e) for s, e in zip(*np.nonzero(done)) if s >= 3]
for s, e in rows:
    print(f"{s:5d}  {t[s]:6.2f}  {e:3d}  {np.linalg.norm(traj.action[s, e]):8.3f}  {traj.reward[s, e]:+7.4f}"
          f"  {traj.base_height[s, e]:8.3f}  {traj.tilt_deg[s, e]:8.1f}  {str(traj.terminated[s, e]):>10}"
          f"  {str(traj.truncated[s, e]):>9}  {traj.episode_step[s, e]:12d}"
          + ("   <- ended: " + ", ".join(traj.ended_by(s, e)) if done[s, e] else ""))

endings = [{"step": int(s), "time_s": float(t[s]), "env": int(e), "reason": traj.ended_by(s, e)}
           for s, e in zip(*np.nonzero(done))]
print(f"\nEpisode endings: {len(endings)}" + ("" if endings else " (every robot stayed up)"))

# 4. Animation of environment 0 with a caption tying each frame to the numbers.
captions, alert = [], []
for s in traj.frame_steps:
    if s < 0:
        captions.append("t=0.00 s  start (after reset)")
        alert.append(False)
        continue
    window = slice(max(0, s - 1), s + 1)  # frames are every 2 steps; catch endings in between
    ended_steps = [k for k in range(window.start, window.stop) if done[k, 0]]
    if ended_steps:
        reason = ", ".join(traj.ended_by(ended_steps[0], 0))
        captions.append(f"t={t[s]:.2f} s  ENDED ({reason}) -> new episode starts")
    else:
        captions.append(f"t={t[s]:.2f} s  tilt={traj.tilt_deg[s, 0]:4.0f} deg")
    alert.append(bool(ended_steps))
dk.save_gif(dk.caption_frames(traj.frames, captions, alert), run.out / "robot.gif", fps=25)

# 5. Signals over time, one line per robot copy.
import matplotlib.pyplot as plt  # noqa: E402

dk.use_style()
fig, axes = plt.subplots(3, 1, figsize=(9, 7.5), sharex=True)
panels = [
    (traj.base_height, "trunk height (m)", None),
    (traj.tilt_deg, "trunk tilt from upright (deg)", 70.0),
    (traj.reward, "reward per step", None),
]
for ax, (data, label, limit) in zip(axes, panels):
    for e in range(cfg.num_envs):
        ax.plot(t, data[:, e], lw=1.6, label=f"env {e}")
    if limit is not None:
        ax.axhline(limit, color=dk.COLORS["red"], ls="--", lw=1.2)
        ax.text(t[0], limit, "  fall limit: episode ends", color=dk.COLORS["red"], va="bottom", fontsize=10)
    for s, e in zip(*np.nonzero(done)):
        ax.axvline(t[s], color=dk.COLORS["muted"], lw=0.8, ls=":")
    ax.set_ylabel(label)
axes[0].legend(ncol=min(cfg.num_envs, 4), loc="upper center", bbox_to_anchor=(0.5, 1.22), fontsize=9)
axes[-1].set_xlabel("simulated time (s)  — one point per policy step (20 ms)")
changed = ", ".join(f"{k}={v}" for k, v in run.changed.items()) or "default settings"
fig.suptitle(f"What the robots did — {changed}\n(dotted lines: an episode ended and that robot was reset)",
             fontsize=13)
dk.save_fig(fig, run.out / "signals.png")

np.savez(run.out / "signals.npz", t=t, tilt=traj.tilt_deg, height=traj.base_height, reward=traj.reward, done=done)
run.save_json("summary.json", {"interface_and_timing": info, "steps": steps, "episode_endings": endings,
                               "mean_reward_per_step": float(traj.reward.mean())})

# 6. Compare env-0 tilt across every setting run so far.
fig, ax = plt.subplots(figsize=(9, 3.6))
for folder in sorted(p for p in (run.lab_dir / "results").iterdir() if (p / "signals.npz").exists()):
    data = np.load(folder / "signals.npz")
    ax.plot(data["t"], data["tilt"][:, 0], lw=1.8, label=folder.name)
ax.axhline(70, color=dk.COLORS["red"], ls="--", lw=1.2)
ax.set_xlabel("simulated time (s)")
ax.set_ylabel("env 0 tilt (deg)")
ax.set_title("Env 0 tilt for each setting you have tried")
ax.legend(fontsize=9, loc="upper left", bbox_to_anchor=(1.01, 1.0))
dk.save_fig(fig, run.lab_dir / "results" / "compare.png")
print("\nDone. Open results/<settings>/robot.gif and signals.png; results/compare.png compares runs.")
