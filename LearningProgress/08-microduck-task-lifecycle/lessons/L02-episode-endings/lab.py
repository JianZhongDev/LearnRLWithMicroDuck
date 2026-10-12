r"""Lab 08/L02: how do episodes end and restart?

Run: lab 08/L02
Change one thing: lab 08/L02 episode_seconds=0.6
Real MicroDuck simulation; a shortened time limit makes endings easy to see.
Outputs in results/<settings>: robot.gif (copy 0), endings.png (all copies),
signals.npz (recorded flags and counters), summary.json (events and checks).
results/compare.png compares episode age for copy 0 across runs.
"""

import duckkit as dk

run = dk.lab_config(
    {"episode_seconds": 1.3, "action_noise": 0.0, "seconds": 2.6, "seed": 0},
    help={
        "episode_seconds": "maximum episode duration in seconds; rounded up to whole decision steps",
        "action_noise": "standard deviation of random joint-target offsets in radians; 0 holds the default pose",
        "seconds": "total simulated duration in seconds, across successive episodes",
        "seed": "integer random seed for starts and actions (unitless)",
    },
)

import numpy as np
import matplotlib.pyplot as plt
from duckkit.sim import describe_env

cfg = run.cfg
if not (np.isfinite(cfg.episode_seconds) and cfg.episode_seconds >= 0.02
        and np.isfinite(cfg.seconds) and cfg.seconds >= 0.02
        and np.isfinite(cfg.action_noise) and cfg.action_noise >= 0):
    raise SystemExit("Use finite durations >= 0.02 seconds and action_noise >= 0 radians.")


def configure(env_cfg):
    env_cfg.episode_length_s = cfg.episode_seconds


env = dk.make_env(num_envs=16, seed=cfg.seed, render=True, width=640,
                  height=360, configure=configure)
try:
    info = describe_env(env)
    steps = max(1, round(cfg.seconds / env.step_dt))
    policy = (dk.zero_policy(env) if cfg.action_noise == 0
              else dk.noise_policy(env, cfg.action_noise, seed=cfg.seed))
    traj = dk.rollout(env, policy, steps=steps, render_every=2)
finally:
    env.close()

# Independently reconstruct every episode counter from the returned flags.
previous = np.vstack([np.zeros((1, 16), dtype=int), traj.episode_step[:-1]])
expected = np.where(traj.done, 0, previous + 1)
assert np.array_equal(expected, traj.episode_step), "Episode counters disagree with reset flags"
time_out = traj.termination_terms["time_out"]
assert np.array_equal(time_out, previous + 1 >= info["episode_length_steps"])
for flag, is_timeout in [(traj.terminated, False), (traj.truncated, True)]:
    terms = [traj.termination_terms[name] for name, value in info["termination_terms"].items()
             if value == is_timeout]
    assert np.array_equal(flag, np.logical_or.reduce(terms))

events = []
for s, e in zip(*np.nonzero(traj.done)):
    events.append({"time_s": float(traj.time[s]), "copy": int(e),
                   "episode_age_before_reset_s": float((previous[s, e] + 1) * traj.step_dt),
                   "terminated": bool(traj.terminated[s, e]),
                   "truncated": bool(traj.truncated[s, e]),
                   "reasons": traj.ended_by(s, e)})
print("\nFirst episode endings (all events are in summary.json)")
print("time (s)  copy  age at ending (s)  terminated  truncated  reason")
for event in events[:12]:
    print(f"{event['time_s']:8.2f}  {event['copy']:4d}  "
          f"{event['episode_age_before_reset_s']:17.2f}  "
          f"{str(event['terminated']):>10}  {str(event['truncated']):>9}  "
          f"{', '.join(event['reasons'])}")
counts = {name: int(values.sum()) for name, values in traj.termination_terms.items()}
print(f"\nEnding reasons: {counts}")
print("Verified: ended copies restart at age zero; all other copies advance one step.")

# Frames show post-step state: the ending pose has already been reset.
captions, alerts = [], []
last_frame_step = -1
for s in traj.frame_steps:
    if s == -1:
        captions.append("Copy 0 | start of episode")
        alerts.append(False)
        continue
    ended = [k for k in range(last_frame_step + 1, s + 1) if traj.done[k, 0]]
    if ended:
        k = ended[-1]
        reason = " + ".join(traj.ended_by(k, 0))
        label = "fall" if reason == "fell_over" else "time up" if reason == "time_out" else "ended"
        captions.append(f"{traj.time[s]:.2f}s | {label} -> reset")
    else:
        captions.append(f"{traj.time[s]:.2f}s | copy 0 | episode age {traj.episode_step[s, 0]*traj.step_dt:.2f}s")
    alerts.append(bool(ended))
    last_frame_step = s
dk.save_gif(dk.caption_frames(traj.frames, captions, alerts), run.out / "robot.gif", fps=25)

dk.use_style()
fig, ax = plt.subplots(figsize=(10, 6))
for e in range(16):
    ax.hlines(e, 0, traj.time[-1], color="#d6dee5", lw=2)
for mask, marker, color, label in [
    (traj.terminated & ~traj.truncated, "x", dk.COLORS["red"], "Terminated (task ending)"),
    (traj.truncated & ~traj.terminated, "o", dk.COLORS["blue"], "Truncated (cut short)"),
    (traj.terminated & traj.truncated, "D", dk.COLORS["purple"], "Both flags"),
]:
    s, e = np.nonzero(mask)
    if len(s):
        ax.scatter(traj.time[s], e, marker=marker, color=color, s=45, label=label, zorder=3)
ax.set(yticks=range(16), ylim=(15.7, -0.7), xlim=(0, traj.time[-1]+0.04),
       xlabel="Simulated time across episodes (s)", ylabel="Robot copy (index)",
       title="Each marker ends one episode; only that copy resets")
ax.grid(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=10)
dk.save_fig(fig, run.out / "endings.png")

np.savez(run.out / "signals.npz", time=traj.time, episode_step=traj.episode_step,
         step_dt=traj.step_dt, terminated=traj.terminated, truncated=traj.truncated,
         **{f"reason_{k}": v for k, v in traj.termination_terms.items()})
run.save_json("summary.json", {"interface": info, "reason_counts": counts,
                               "events": events, "counter_and_reason_checks_passed": True})

fig, ax = plt.subplots(figsize=(10, 3.6))
for folder in sorted((run.lab_dir / "results").iterdir()):
    if not (folder / "signals.npz").exists():
        continue
    with np.load(folder / "signals.npz") as data:
        ax.plot(np.r_[0, data["time"]], np.r_[0, data["episode_step"][:, 0]*data["step_dt"]],
                label=folder.name, lw=1.8)
ax.set(xlabel="Simulated time across episodes (s)", ylabel="Copy 0 episode age (s)",
       title="Episode age returns to zero whenever copy 0 resets")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=10)
dk.save_fig(fig, run.lab_dir / "results/compare.png")
print("\nOpen robot.gif, then endings.png. Compare runs in results/compare.png.")
