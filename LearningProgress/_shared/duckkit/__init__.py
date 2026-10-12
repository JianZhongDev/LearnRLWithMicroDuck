"""duckkit: small helpers that keep MicroDuck labs short and readable.

Import duckkit FIRST in a lab script. Importing it sets cache and rendering
environment variables before MuJoCo, Warp or mjlab are loaded.

    import duckkit as dk

    run = dk.lab_config({"steps": 100, "noise": 0.0})   # learner changes values via CLI
    env = dk.make_env(num_envs=2, render=True)
    traj = dk.rollout(env, dk.noise_policy(env, run.cfg.noise), steps=run.cfg.steps)
    dk.save_gif(traj.frames, run.out / "robot.gif")

Modules:
    duckkit.setup   paths, caches, compute devices and renderer (from .course/env.json)
    duckkit.labkit  "change one thing" configuration and per-run result folders
    duckkit.sim     create an mjlab MicroDuck environment and record a rollout
    duckkit.render  GIFs with captions, static MuJoCo snapshots
    duckkit.viz     consistent plot style and simple labelled block diagrams
"""

from duckkit.setup import (
    COURSE_ROOT,
    LEARNING_ROOT,
    MICRODUCK_XML_DIR,
    RL_REPO,
    RUNTIME_REPO,
    can_render,
    configure_runtime,
    default_device,
    is_apple_silicon,
    torch_device,
)

configure_runtime()

from duckkit.labkit import lab_config, LabRun  # noqa: E402
from duckkit.viz import use_style, flow_diagram, save_fig, COLORS  # noqa: E402
from duckkit.render import save_gif, caption_frames, model_snapshot  # noqa: E402


def __getattr__(name):
    # Simulation helpers import torch/mjlab, which are slow. Load them lazily so
    # diagram-only scripts stay fast.
    if name in {"make_env", "rollout", "zero_policy", "noise_policy", "Rollout", "DEFAULT_TASK"}:
        from duckkit import sim

        return getattr(sim, name)
    raise AttributeError(name)


__all__ = [
    "configure_runtime",
    "COURSE_ROOT",
    "LEARNING_ROOT",
    "RL_REPO",
    "RUNTIME_REPO",
    "MICRODUCK_XML_DIR",
    "can_render",
    "default_device",
    "torch_device",
    "is_apple_silicon",
    "lab_config",
    "LabRun",
    "use_style",
    "flow_diagram",
    "save_fig",
    "COLORS",
    "save_gif",
    "caption_frames",
    "model_snapshot",
    "make_env",
    "rollout",
    "zero_policy",
    "noise_policy",
    "Rollout",
    "DEFAULT_TASK",
]
