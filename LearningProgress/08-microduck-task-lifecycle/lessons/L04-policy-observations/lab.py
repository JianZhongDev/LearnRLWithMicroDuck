r"""What does the policy actually see?

Run: lab 08/L04
Change: lab 08/L04 gravity_noise=0.15
Outputs: robot.gif, observations.png, layout.json, signals.npz, summary.json;
results/compare.png compares the gravity-reading error across saved runs.
Real MicroDuck with fixed joint targets, no training. This teaching config
removes gravity-channel delay and mounting error to isolate additive noise.
"""
import duckkit as dk

run = dk.lab_config(
    {"gravity_noise": 0.01, "seconds": 1.6, "seed": 0},
    help={
        "gravity_noise": "uniform noise half-width on each gravity-direction component (unitless), 0 to 0.3",
        "seconds": "simulated duration (seconds), 0.1 to 5",
        "seed": "integer random seed for starting conditions and observations (no units)",
    },
)

import json
import numpy as np
import torch
import matplotlib.pyplot as plt
from mjlab.envs import mdp
from mjlab.utils.noise import UniformNoiseCfg

cfg = run.cfg
if not np.isfinite(cfg.gravity_noise) or not 0 <= cfg.gravity_noise <= 0.3:
    raise SystemExit("gravity_noise must be between 0 and 0.3")
if not np.isfinite(cfg.seconds) or not 0.1 <= cfg.seconds <= 5:
    raise SystemExit("seconds must be between 0.1 and 5")

def configure(env_cfg):
    # Change the config copy, never the installed source. Other channels retain
    # their training configuration; only gravity is simplified for this lesson.
    term = env_cfg.observations["actor"].terms["projected_gravity"]
    term.func, term.params = mdp.projected_gravity, {}
    term.delay_min_lag = term.delay_max_lag = 0
    term.noise = UniformNoiseCfg(n_min=-cfg.gravity_noise, n_max=cfg.gravity_noise)
    term.clip, term.scale = None, 1.0

def cpu(tensor):
    return tensor.detach().cpu().numpy().copy()

env = dk.make_env(num_envs=4, seed=cfg.seed, render=True, width=640, height=400, configure=configure)
try:
    manager = env.observation_manager
    layout = {}
    for group in ("actor", "critic"):
        offset, entries = 0, []
        for name, dims in zip(manager.active_terms[group], manager.group_obs_term_dim[group]):
            size = int(np.prod(dims))
            entries.append({"name": name, "start": offset, "stop": offset + size, "count": size})
            offset += size
        layout[group] = entries
    def span(group, name):
        entry = next(x for x in layout[group] if x["name"] == name)
        return slice(entry["start"], entry["stop"])
    assert "base_lin_vel" not in manager.active_terms["actor"]
    assert "base_lin_vel" in manager.active_terms["critic"]
    steps = round(cfg.seconds / env.step_dt)
    dt = float(env.step_dt)
    rec = {key: [] for key in ("actor", "critic", "true_gravity", "true_velocity", "done", "tilt")}
    frames, captions, alerts = [env.render().copy()], ["Copy 0 | fixed joint targets | start"], [False]
    ending_events = []
    pending_end = False
    for step in range(steps):
        obs, _, terminated, truncated, _ = env.step(torch.zeros(env.action_space.shape, device=env.device))
        robot = env.scene["robot"]
        gravity = cpu(robot.data.projected_gravity_b)
        done = cpu(terminated | truncated)
        rec["actor"].append(cpu(obs["actor"]))
        rec["critic"].append(cpu(obs["critic"]))
        rec["true_gravity"].append(gravity)
        rec["true_velocity"].append(cpu(robot.data.root_link_lin_vel_b))
        rec["done"].append(done)
        rec["tilt"].append(np.degrees(np.arccos(np.clip(-gravity[:, 2], -1, 1))))
        if done[0]:
            reasons = [n for n in env.termination_manager.active_terms if env.termination_manager.get_term(n)[0]]
            ending_events.append({"time_s": (step+1)*dt, "reasons": reasons})
        pending_end |= bool(done[0])
        if step % 2 == 0:
            frames.append(env.render().copy())
            captions.append(f"t={(step+1)*dt:.2f} s | " + ("ENDED -> reset pose" if pending_end else f"trunk tilt={rec['tilt'][-1][0]:.0f} deg"))
            alerts.append(pending_end)
            pending_end = False
finally:
    env.close()

data = {key: np.stack(values) for key, values in rec.items()}
time = (np.arange(steps)+1)*dt
actor_gravity = data["actor"][:, :, span("actor", "projected_gravity")]
critic_gravity = data["critic"][:, :, span("critic", "projected_gravity")]
critic_velocity = data["critic"][:, :, span("critic", "base_lin_vel")]
error = actor_gravity - data["true_gravity"]
for value in data.values():
    assert np.isfinite(value).all()
np.testing.assert_allclose(critic_gravity, data["true_gravity"], atol=1e-6)
np.testing.assert_allclose(critic_velocity, data["true_velocity"], atol=1e-6)
assert np.max(np.abs(error)) <= cfg.gravity_noise + 1e-6
for group in ("actor", "critic"):
    assert layout[group][-1]["stop"] == data[group].shape[-1]
np.testing.assert_allclose(data["actor"][:, :, span("actor", "actions")], 0, atol=1e-7)

run.save_json("layout.json", layout)
run.save_json("summary.json", {
    "steps_per_copy": steps, "num_copies": 4, "step_dt_s": dt,
    "actor_count": data["actor"].shape[-1], "critic_count": data["critic"].shape[-1],
    "gravity_noise_half_width": cfg.gravity_noise,
    "mean_absolute_gravity_error": float(np.abs(error).mean()),
    "max_absolute_gravity_error": float(np.abs(error).max()),
    "copy_0_endings": ending_events,
    "checks": "passed: layout sizes, noise bound, critic gravity and velocity against simulator, zero action history",
    "teaching_override": "gravity channel only: no delay or mounting rotation; uniform additive noise; scale 1",
})
np.savez(run.out / "signals.npz", time=time, actor_gravity=actor_gravity, gravity_error=error, **data)
print("\nObservation pieces (counts of numbers; order is group-specific)")
print(f"{'Piece':25} {'Policy / actor':>15} {'Training critic':>16}")
names = list(dict.fromkeys(x["name"] for entries in layout.values() for x in entries))
for name in names:
    counts = [next((str(x["count"]) for x in layout[g] if x["name"] == name), "absent") for g in ("actor", "critic")]
    print(f"{name:25} {counts[0]:>15} {counts[1]:>16}")
print(f"Checks passed. Mean absolute gravity error: {np.abs(error).mean():.5f} (unitless).")
dk.save_gif(dk.caption_frames(frames, captions, alerts), run.out / "robot.gif", fps=25)

dk.use_style()
fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
axes[0].plot(time, data["true_gravity"][:, 0, 2], color="black", label="Simulator / critic")
axes[0].plot(time, actor_gravity[:, 0, 2], color=dk.COLORS["orange"], label="Policy input", lw=1.3)
axes[0].set(ylabel="gravity direction: z (unitless)", title="As the trunk tips, its gravity reading moves away from -1")
axes[0].legend(loc="best")
axes[1].plot(time, error[:, 0, 2], color=dk.COLORS["orange"])
axes[1].axhline(0, color="black", lw=0.8)
axes[1].set(xlabel="simulated time (s)", ylabel="policy minus simulator (unitless)",
            ylim=(-0.17, 0.17), title="The policy receives a noisy version of that reading")
limit = max(0.17, cfg.gravity_noise*1.15)
axes[1].set_ylim(-limit, limit)
for ax in axes:
    for index, event in enumerate(ending_events):
        ax.axvline(event["time_s"], color=dk.COLORS["red"], ls=":", label="Ended / reset" if index == 0 else None)
axes[1].legend(loc="upper right") if ending_events else None
fig.suptitle(f"Copy 0: observation is a chosen reading | gravity noise ±{cfg.gravity_noise}")
fig.tight_layout()
dk.save_fig(fig, run.out / "observations.png")

fig, ax = plt.subplots(figsize=(10, 4))
for folder in sorted((run.lab_dir / "results").iterdir()):
    if not (folder / "signals.npz").exists():
        continue
    with np.load(folder / "signals.npz") as saved:
        ax.plot(saved["time"], saved["gravity_error"][:, 0, 2], label=folder.name, alpha=0.85, lw=1)
ax.axhline(0, color="black", lw=0.8)
ax.set(xlabel="simulated time (s)", ylabel="policy minus simulator (unitless)",
       title="Compare how far the policy's gravity reading differs from the simulator")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2))
dk.save_fig(fig, run.lab_dir / "results/compare.png")
print("Open robot.gif first, then observations.png. Compare runs in results/compare.png.")
