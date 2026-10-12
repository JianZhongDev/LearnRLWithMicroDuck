"""Create a MicroDuck mjlab environment and record what happens during a rollout.

The source repository is used read-only: we import its registered tasks and
configurations, change runtime settings on a *copy* of the config, and never
write into the repository.

    env = make_env(num_envs=2, render=True)
    traj = rollout(env, zero_policy(env), steps=150)
    traj.reward.shape          # (150, 2)  -> [policy step, environment]
    traj.reward_terms["..."]   # each reward term's contribution per step
    traj.frames                # rendered images of environment 0

A policy here is any function `policy(obs, t) -> action tensor [num_envs, num_actions]`.
"""

from __future__ import annotations


from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import torch

import mjlab.tasks  # noqa: F401  (populates the task registry)

from duckkit.setup import can_render, default_device
from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg

DEFAULT_TASK = "Mjlab-Velocity-Flat-MicroDuck"

Policy = Callable[[dict, int], torch.Tensor]


def make_env(
    task: str = DEFAULT_TASK,
    num_envs: int = 2,
    seed: int = 0,
    render: bool = False,
    play: bool = False,
    device: str | None = None,
    width: int = 480,
    height: int = 360,
    camera_distance: float = 1.0,
    extra_envs_in_view: int = 0,
    configure: Callable | None = None,
) -> ManagerBasedRlEnv:
    """Build an environment from the registered task config.

    play=False uses the training config (randomization, terminations, time limit).
    play=True uses the task's evaluation config.
    device=None picks the GPU when one is usable, otherwise the CPU (see duckkit.setup).
    render=True is ignored, with one notice, when no rendering backend works on this machine.
    configure(cfg) may edit the config copy before the environment is built.
    """
    device = device or default_device()
    if render and not can_render():
        print("[duckkit] No working MuJoCo rendering backend on this machine: running without GIF frames. "
              "Plots and printed results are unaffected. Run the doctor (lab doctor) for details.")
        render = False
    cfg = load_env_cfg(task, play=play)
    cfg.scene.num_envs = num_envs
    cfg.seed = seed
    if render:
        cfg.viewer.width, cfg.viewer.height = width, height
        cfg.viewer.distance = camera_distance
        cfg.viewer.max_extra_envs = extra_envs_in_view
    if configure is not None:
        configure(cfg)
    env = ManagerBasedRlEnv(cfg=cfg, device=device, render_mode="rgb_array" if render else None)
    env.reset(seed=seed)
    return env


def zero_policy(env: ManagerBasedRlEnv) -> Policy:
    """Action 0 = 'hold the default joint pose' for MicroDuck's joint-position actions."""
    shape = env.action_space.shape

    def policy(obs: dict, t: int) -> torch.Tensor:
        return torch.zeros(shape, device=env.device)

    return policy


def noise_policy(env: ManagerBasedRlEnv, scale: float, seed: int = 0, hold_steps: int = 1) -> Policy:
    """Random actions ~ Normal(0, scale), each held for `hold_steps` policy steps."""
    shape = env.action_space.shape
    gen = torch.Generator(device=env.device).manual_seed(seed)
    current = torch.zeros(shape, device=env.device)

    def policy(obs: dict, t: int) -> torch.Tensor:
        nonlocal current
        if t % hold_steps == 0:
            current = scale * torch.randn(shape, device=env.device, generator=gen)
        return current

    return policy


@dataclass
class Rollout:
    """Everything recorded during a rollout. Arrays are [step, env, ...]."""

    step_dt: float                     # seconds of simulated time per policy step
    physics_dt: float                  # seconds per physics substep
    decimation: int                    # physics substeps per policy step
    action: np.ndarray                 # [T, N, A] action sent at each step
    reward: np.ndarray                 # [T, N] total reward returned by env.step
    terminated: np.ndarray             # [T, N] episode ended by failure/success condition
    truncated: np.ndarray              # [T, N] episode ended by time limit (time_out)
    episode_step: np.ndarray           # [T, N] steps into the current episode AFTER this step (0 = just reset)
    base_height: np.ndarray            # [T, N] trunk height in metres, read after the step
    tilt_deg: np.ndarray               # [T, N] trunk tilt from upright in degrees, read after the step
    reward_terms: dict[str, np.ndarray]       # name -> [T, N] contribution to `reward` this step
    termination_terms: dict[str, np.ndarray]  # name -> [T, N] which condition fired
    obs_shapes: dict[str, tuple]
    frames: list[np.ndarray] = field(default_factory=list)
    frame_steps: list[int] = field(default_factory=list)

    @property
    def time(self) -> np.ndarray:
        """Simulated time (s) at the END of each policy step."""
        return (np.arange(self.reward.shape[0]) + 1) * self.step_dt

    @property
    def done(self) -> np.ndarray:
        return self.terminated | self.truncated

    def ended_by(self, step: int, env: int) -> list[str]:
        return [k for k, v in self.termination_terms.items() if v[step, env]]


def _robot(env):
    return env.scene["robot"]


def rollout(env: ManagerBasedRlEnv, policy: Policy, steps: int, render_every: int = 1) -> Rollout:
    """Run `steps` policy steps for all environments and record signals.

    Note on automatic reset: when an environment's episode ends inside env.step,
    mjlab resets it immediately. Signals read after the step (height, tilt,
    episode_step) therefore already describe the NEW episode for that env,
    while reward/terminated/truncated describe the step that ended the old one.
    """
    rm, tm = env.reward_manager, env.termination_manager
    reward_scale = env.step_dt if getattr(rm, "_scale_by_dt", False) else 1.0
    robot = _robot(env)

    obs = env.observation_manager.compute()
    obs_shapes = {k: tuple(v.shape) for k, v in obs.items() if hasattr(v, "shape")}
    rec: dict[str, list] = {k: [] for k in
                            ("action", "reward", "terminated", "truncated", "episode_step", "height", "tilt")}
    rterms = {name: [] for name in rm.active_terms}
    tterms = {name: [] for name in tm.active_terms}
    frames, frame_steps = [], []

    if env.render_mode == "rgb_array" and render_every:
        frames.append(env.render().copy())
        frame_steps.append(-1)

    for t in range(steps):
        action = policy(obs, t)
        obs, reward, terminated, truncated, _ = env.step(action)
        rec["action"].append(action.detach().cpu().numpy().copy())
        rec["reward"].append(reward.detach().cpu().numpy().copy())
        rec["terminated"].append(terminated.detach().cpu().numpy().copy())
        rec["truncated"].append(truncated.detach().cpu().numpy().copy())
        rec["episode_step"].append(env.episode_length_buf.detach().cpu().numpy().copy())
        rec["height"].append(robot.data.root_link_pos_w[:, 2].detach().cpu().numpy().copy())
        gz = robot.data.projected_gravity_b[:, 2].detach().clamp(-1.0, 1.0)
        rec["tilt"].append(torch.rad2deg(torch.arccos(-gz)).cpu().numpy().copy())
        for idx, name in enumerate(rm.active_terms):
            rterms[name].append((rm._step_reward[:, idx] * reward_scale).detach().cpu().numpy().copy())
        for name in tm.active_terms:
            tterms[name].append(tm.get_term(name).detach().cpu().numpy().copy())
        if env.render_mode == "rgb_array" and render_every and (t % render_every == 0):
            frames.append(env.render().copy())
            frame_steps.append(t)

    stack = lambda xs: np.stack(xs, axis=0)  # noqa: E731
    return Rollout(
        step_dt=float(env.step_dt),
        physics_dt=float(env.physics_dt),
        decimation=int(env.cfg.decimation),
        action=stack(rec["action"]),
        reward=stack(rec["reward"]),
        terminated=stack(rec["terminated"]).astype(bool),
        truncated=stack(rec["truncated"]).astype(bool),
        episode_step=stack(rec["episode_step"]),
        base_height=stack(rec["height"]),
        tilt_deg=stack(rec["tilt"]),
        reward_terms={k: stack(v) for k, v in rterms.items()},
        termination_terms={k: stack(v).astype(bool) for k, v in tterms.items()},
        obs_shapes=obs_shapes,
        frames=frames,
        frame_steps=frame_steps,
    )


def describe_env(env: ManagerBasedRlEnv) -> dict:
    """Short, readable summary of the environment's interface and timing."""
    obs = env.observation_manager.compute()
    return {
        "num_envs": env.num_envs,
        "physics_dt_s": float(env.physics_dt),
        "decimation": int(env.cfg.decimation),
        "policy_dt_s": float(env.step_dt),
        "policy_rate_hz": round(1.0 / float(env.step_dt), 3),
        "episode_length_s": float(env.max_episode_length_s),
        "episode_length_steps": int(env.max_episode_length),
        "action_dim": int(env.action_space.shape[-1]),
        "observation_groups": {k: list(v.shape) for k, v in obs.items() if hasattr(v, "shape")},
        "reward_terms": list(env.reward_manager.active_terms),
        "termination_terms": {n: bool(env.termination_manager.get_term_cfg(n).time_out)
                              for n in env.termination_manager.active_terms},
    }


__all__ = ["DEFAULT_TASK", "make_env", "zero_policy", "noise_policy", "rollout", "Rollout", "describe_env"]
