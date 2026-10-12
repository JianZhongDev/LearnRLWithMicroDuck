# duckkit quick reference

Location: `LearningProgress/_shared/duckkit/`. Health check: `lab doctor --full`.

`import duckkit as dk` must come first in a lab. It reads `.course/env.json` (written by setup), puts caches under `.course/cache/`, and selects the MuJoCo rendering backend before MuJoCo loads.

## This machine: `duckkit.setup`

```python
dk.default_device()   # simulation device: "cuda:0" with a usable NVIDIA GPU, else "cpu" (also on Apple Silicon)
dk.torch_device()     # for neural-network-only code: "cuda:0", "mps" (Apple GPU) or "cpu"
dk.is_apple_silicon()
dk.can_render()       # False when no rendering backend works: GIFs are skipped, plots still work
dk.COURSE_ROOT        # repository root
dk.RL_REPO            # the microduck_rl checkout, outside this repository (read-only)
dk.RUNTIME_REPO       # the microduck checkout, outside this repository (read-only)
dk.MICRODUCK_XML_DIR  # the robot's MJCF model files (read-only)
```

Write labs so they work everywhere:

- Never hard-code `"cuda:0"`; leave `device` to `make_env`, and use `env.device` for tensors that touch the simulator.
- Use `dk.torch_device()` only for code that never touches the simulator (toy networks, supervised fits). Never pass `"mps"` to `make_env`, and do not mix the two devices in one computation; on MPS use `float32`.
- A lab must still give a useful result without GIFs: always produce at least one plot.
- On `cpu`, use small defaults (2–4 robot copies, a few seconds). If a lab needs a GPU to finish in reasonable time, say so in its docstring and print a clear message when `dk.default_device() == "cpu"`.

## Lab settings: `duckkit.labkit`

```python
run = dk.lab_config(defaults: dict, help: dict) -> LabRun
run.cfg.<name>      # values after key=value overrides from the command line
run.changed         # dict of settings that differ from the defaults
run.out             # results/<default | key=value,...>/  (created)
run.lab_dir         # folder containing lab.py
run.save_json(name, data)
```

`lab 08/L01 help` prints the settings and their help text.

## Simulation: `duckkit.sim` (imports torch and mjlab; the first run compiles simulation code, 1–3 minutes)

```python
env = dk.make_env(task=dk.DEFAULT_TASK, num_envs=2, seed=0, render=False, play=False,
                  device=None, width=480, height=360, camera_distance=1.0,
                  extra_envs_in_view=0, configure=None)   # configure(cfg) edits the config copy
traj = dk.rollout(env, policy, steps, render_every=1)     # policy(obs_dict, t) -> action [N, A]
dk.zero_policy(env)                         # action 0 = hold the default joint pose
dk.noise_policy(env, scale, seed=0, hold_steps=1)
from duckkit.sim import describe_env        # dict: timing, sizes, reward and termination term names
env.close()
```

`Rollout` fields are numpy arrays shaped `[step, env, ...]`: `action`, `reward`, `terminated`, `truncated`, `done`, `episode_step`, `base_height` (m), `tilt_deg`, `reward_terms` (name → per-step contribution; they sum to `reward`), `termination_terms` (name → bool), `time` (s at the end of each step), `frames` and `frame_steps` (images of env 0; empty when rendering is off), `step_dt`, `physics_dt`, `decimation`. `traj.ended_by(step, env)` gives the termination names.

Auto-reset: signals read after a step that ended an episode already describe the NEW episode for that env.

For other robot quantities, read `env.scene["robot"].data.<field>` (for example `root_link_pos_w`, `joint_pos`, `projected_gravity_b`) inside your own loop. Model it on `rollout` in `sim.py`.

## Pictures: `duckkit.viz`, `duckkit.render`

```python
dk.use_style()
dk.flow_diagram(steps=[("Title", "subtitle"), ...], highlight=[i, ...], highlight_tag="TODAY",
                loop_label=None, edge_labels=None, title="", path=None)
dk.save_fig(fig, path)
dk.COLORS   # ink, muted, box, edge, highlight, blue, orange, green, red, purple
dk.caption_frames(frames, captions, alert=None)   # caption bar per frame; alert -> red bar
dk.save_gif(frames, path, fps=12.5, hold_last=1.0) # returns None and prints a note if there are no frames
dk.model_snapshot(xml_path, keyframe=None, qpos=None, width=480, height=360,
                  distance=0.6, azimuth=135, elevation=-20)   # plain MuJoCo still image (needs rendering)
```

Diagram-only scripts (`flow_diagram`, matplotlib) need no GPU and no renderer, and run in seconds.

## Launcher

`lab` is `./lab.sh` (Linux, macOS) or the Windows `lab` command, which runs `lab.sh` inside WSL.

- `lab list` · `lab <MM>/<Lxx> [key=value ...]` · `lab <MM>/<Lxx> help` · `lab py <script.py> [args]` · `lab doctor [--full]`
- `lab py` changes into the script's folder before running it. On Windows, pass file arguments as paths relative to that folder or as WSL paths (`/mnt/c/...`), not `C:\...`.
- `lab py tools/where.py mjlab rsl_rl` prints where installed packages live, for reading their source.
