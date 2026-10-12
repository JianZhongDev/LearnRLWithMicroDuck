r"""Lab 08/L03: where does the reward number come from?

Run: lab 08/L03
Change one thing: lab 08/L03 action_noise=0.3
Outputs in results/<settings>: robot.gif, reward_parts.png, signals.npz,
terms.csv, summary.json; results/compare.png compares mean contributions.
Real MicroDuck, fixed or random joint targets; no policy training.
"""
import duckkit as dk

run = dk.lab_config(
    {"action_noise": 0.0, "seconds": 2.0, "seed": 0},
    help={
        "action_noise": "standard deviation of random joint-target offsets (radians); zero holds default targets",
        "seconds": "total simulated duration (seconds), from 0.02 to 10",
        "seed": "integer random seed for starting states and target offsets (no units)",
    },
)

import csv
import json
import numpy as np
import matplotlib.pyplot as plt

cfg = run.cfg
if not np.isfinite(cfg.seconds) or not 0.02 <= cfg.seconds <= 10:
    raise SystemExit("seconds must be between 0.02 and 10")
if not np.isfinite(cfg.action_noise) or not 0 <= cfg.action_noise <= 1:
    raise SystemExit("action_noise must be between 0 and 1 radian")

env = dk.make_env(num_envs=4, seed=cfg.seed, render=True, width=640, height=400)
try:
    rm = env.reward_manager
    names = list(rm.active_terms)
    weights = {n: float(rm.get_term_cfg(n).weight) for n in names}
    scale_by_dt = bool(rm._scale_by_dt)
    steps = max(1, round(cfg.seconds / env.step_dt))
    policy = dk.zero_policy(env) if cfg.action_noise == 0 else dk.noise_policy(env, cfg.action_noise, seed=cfg.seed)
    traj = dk.rollout(env, policy, steps=steps, render_every=2)
    assert weights == {n: float(rm.get_term_cfg(n).weight) for n in names}, "Weights changed during this short lab"
finally:
    env.close()

parts = np.stack([traj.reward_terms[n] for n in names], axis=-1)
assert np.isfinite(parts).all() and np.isfinite(traj.reward).all()
sum_error = float(np.max(np.abs(parts.sum(axis=-1) - traj.reward)))
np.testing.assert_allclose(parts.sum(axis=-1), traj.reward, atol=2e-6, rtol=2e-5)

# Independent check from the actions, restricted to each copy's first episode.
# That avoids relying on implementation-specific action history at reset.
previous = np.concatenate([np.zeros_like(traj.action[:1]), traj.action[:-1]])
raw_action_change = np.square(traj.action - previous).sum(axis=-1)
scale = traj.step_dt if scale_by_dt else 1.0
expected = raw_action_change * weights["action_rate_l2"] * scale
first_episode = np.cumsum(traj.done, axis=0) - traj.done == 0
np.testing.assert_allclose(traj.reward_terms["action_rate_l2"][first_episode],
                           expected[first_episode], atol=2e-6, rtol=2e-5)

means = parts.mean(axis=(0, 1))
endings = [{"time_s": float(traj.time[s]), "env": int(e), "reasons": traj.ended_by(s, e)}
           for s, e in zip(*np.nonzero(traj.done))]
run.save_json("summary.json", {
    "step_dt_s": traj.step_dt, "scale_by_dt": scale_by_dt, "steps_per_copy": steps,
    "num_copies": 4, "weights": weights, "mean_contributions": dict(zip(names, means.tolist())),
    "mean_reward_per_step": float(traj.reward.mean()), "max_sum_error": sum_error,
    "action_change_check": "passed on all first-episode steps", "episode_endings": endings,
})
with (run.out / "terms.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["term", "weight", "mean_contribution_reward_units_per_step"])
    writer.writerows(zip(names, [weights[n] for n in names], means))
print("\nAll contributions include weight and time scaling; means over four copies and all steps.")
print(f"{'Named term':28} {'Weight':>9} {'Mean contribution':>19}")
for n in ["upright", "action_rate_l2", "track_linear_velocity", "pose"]:
    print(f"{n:28} {weights[n]:+9.3f} {means[names.index(n)]:+19.6f}")
print(f"All terms added: {means.sum():+.6f}; returned reward mean: {traj.reward.mean():+.6f}")
print(f"Checks passed: full sum (maximum error {sum_error:.2g}); action-change formula.")

captions, alerts = [], []
for s in traj.frame_steps:
    if s < 0:
        captions.append("Copy 0 | start after reset")
        alerts.append(False)
        continue
    ended = any(traj.done[k, 0] for k in range(max(0, s-1), s+1))
    captions.append(f"t={traj.time[s]:.2f} s | " + ("ENDED -> reset pose" if ended else
                    f"tilt={traj.tilt_deg[s, 0]:.0f} deg | reward={traj.reward[s, 0]:+.3f}"))
    alerts.append(ended)
dk.save_gif(dk.caption_frames(traj.frames, captions, alerts), run.out / "robot.gif", fps=25)

dk.use_style()
fig, axes = plt.subplots(1, 2, figsize=(14, 6.8), gridspec_kw={"width_ratios": [1, 1.1]})
order = np.argsort(means)
axes[0].barh(np.arange(len(names)), means[order], color=[dk.COLORS["green"] if v >= 0 else dk.COLORS["red"] for v in means[order]])
axes[0].set_yticks(np.arange(len(names)), [names[i].replace("_", " ") for i in order], fontsize=10)
axes[0].axvline(0, color="black", lw=0.8)
axes[0].set_xlabel("mean contribution (reward units / step)")
axes[0].set_title("Named parts add to one reward\nMean over four copies and all steps", fontsize=12)
ax = axes[1]
up = traj.reward_terms["upright"][:, 0]
change = traj.reward_terms["action_rate_l2"][:, 0]
others = parts[:, 0, [i for i, n in enumerate(names) if n not in ("upright", "action_rate_l2")]].sum(axis=-1)
for vals, label, color in [(up, "Upright contribution", dk.COLORS["green"]),
                           (change, "Target-change contribution", dk.COLORS["red"]),
                           (others, "All other contributions", dk.COLORS["blue"]),
                           (traj.reward[:, 0], "Returned total", "black")]:
    ax.plot(traj.time, vals, label=label, color=color, lw=1.6)
for index, s in enumerate(np.flatnonzero(traj.done[:, 0])):
    ax.axvline(traj.time[s], color=dk.COLORS["muted"], ls=":", label="Episode ended / reset" if index == 0 else None)
ax.set(xlabel="simulated time (s)", ylabel="reward units / step")
ax.set_title("Copy 0: the three parts sum to the total", fontsize=12)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), fontsize=9)
fig.suptitle(f"Reward comes from named contributions | action_noise={cfg.action_noise} rad", fontsize=14)
fig.tight_layout()
dk.save_fig(fig, run.out / "reward_parts.png")

np.savez(run.out / "signals.npz", time=traj.time, reward=traj.reward, parts=parts,
         names=np.array(names), tilt=traj.tilt_deg, done=traj.done, action=traj.action)

folders = sorted(p for p in (run.lab_dir / "results").iterdir() if (p / "summary.json").exists())
fig, ax = plt.subplots(figsize=(10, 4.5))
labels = ["Upright", "Target changes", "All other terms", "Returned total"]
width = 0.8 / len(folders)
for i, folder in enumerate(folders):
    summary = json.loads((folder / "summary.json").read_text())
    m = summary["mean_contributions"]
    vals = [m["upright"], m["action_rate_l2"], sum(v for n, v in m.items() if n not in ("upright", "action_rate_l2")), summary["mean_reward_per_step"]]
    ax.bar(np.arange(4) - 0.4 + width*(i+0.5), vals, width, label=folder.name)
ax.axhline(0, color="black", lw=0.8)
ax.set_xticks(np.arange(4), labels)
ax.set_ylabel("mean reward units / step")
ax.set_title("Compare which contributions changed\nMeans over four copies, including falls and resets")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), fontsize=9)
dk.save_fig(fig, run.lab_dir / "results/compare.png")
print("Open robot.gif first, then reward_parts.png. All terms are in terms.csv.")
