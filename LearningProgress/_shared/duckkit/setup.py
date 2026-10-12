"""Runtime environment for labs: paths, caches, compute devices and renderer.

Everything machine-specific comes from `.course/env.json`, which `setup.sh`
writes. Environment variables override it:

    MICRODUCK_RL_REPO       path to the microduck_rl checkout (outside this repository)
    MICRODUCK_RUNTIME_REPO  path to the microduck checkout (outside this repository)
    COURSE_DEVICE           simulation device: "cuda:0" or "cpu"
    COURSE_TORCH_DEVICE     device for neural-network-only code: "cuda:0", "mps" or "cpu"
    MUJOCO_GL               MuJoCo rendering backend ("egl", "glfw", "osmesa"), or "none"
"""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parents[3]          # repository root
LEARNING_ROOT = COURSE_ROOT / "LearningProgress"
COURSE_DIR = COURSE_ROOT / ".course"                        # local, git-ignored
ENV_FILE = COURSE_DIR / "env.json"
CACHE_ROOT = COURSE_DIR / "cache"


def load_env() -> dict:
    try:
        return json.loads(ENV_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


_ENV = load_env()

# The MicroDuck checkouts are never inside this repository. Setup records where they
# are; the fallback is the default location, next to this repository.
RL_REPO = Path(os.environ.get("MICRODUCK_RL_REPO") or _ENV.get("rl_repo") or COURSE_ROOT.parent / "microduck_rl")
RUNTIME_REPO = Path(os.environ.get("MICRODUCK_RUNTIME_REPO") or _ENV.get("runtime_repo")
                    or COURSE_ROOT.parent / "microduck")
MICRODUCK_XML_DIR = RL_REPO / "src/mjlab_microduck/robot/microduck"

_CACHE_VARS = {
    "WARP_CACHE_PATH": "warp",
    "CUDA_CACHE_PATH": "cuda",
    "XDG_CACHE_HOME": "xdg",
    "TORCH_HOME": "torch",
    "TRITON_CACHE_DIR": "triton",
    "MPLCONFIGDIR": "matplotlib",
    "HF_HOME": "huggingface",
    "WANDB_CACHE_DIR": "wandb",
    "WANDB_DATA_DIR": "wandb-data",
    "WANDB_CONFIG_DIR": "wandb-config",
}


def is_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def is_apple_silicon() -> bool:
    return sys.platform == "darwin" and platform.machine() == "arm64"


def render_backend() -> str | None:
    """The MuJoCo rendering backend to use, or None when rendering is unavailable."""
    value = os.environ.get("MUJOCO_GL")
    if value is None and "mujoco_gl" in _ENV:
        value = _ENV["mujoco_gl"]            # None here means setup found no working backend
        if value is None:
            return None
    if value is None:                        # setup has not probed yet: platform default
        if sys.platform == "darwin":
            value = "glfw"
        else:
            value = "glfw" if is_wsl() else "egl"
    return None if str(value).lower() in {"none", "off", ""} else str(value)


def can_render() -> bool:
    return render_backend() is not None


def default_device() -> str:
    """Device for the robot simulation: 'cuda:0' with a usable NVIDIA GPU, otherwise 'cpu'.

    The simulation stack (mjlab on MuJoCo Warp) runs on NVIDIA CUDA or on the CPU.
    It has no Apple-GPU backend, so Apple Silicon Macs simulate on the CPU.
    """
    value = os.environ.get("COURSE_DEVICE") or _ENV.get("device")
    if value:
        return str(value)
    try:
        import torch

        return "cuda:0" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def torch_device() -> str:
    """Device for neural-network-only code that does not touch the simulator.

    'cuda:0' on NVIDIA, 'mps' (Apple GPU) on Apple Silicon, otherwise 'cpu'. Use it for
    toy networks and supervised fits. Never pass 'mps' to make_env or mix it with
    simulator tensors: the simulator's tensors live on default_device().
    """
    value = os.environ.get("COURSE_TORCH_DEVICE") or _ENV.get("torch_device")
    if value:
        return str(value)
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda:0"
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def configure_runtime() -> None:
    """Set environment variables before MuJoCo, Warp or mjlab are imported.

    Existing values win, so a caller can override any of them.
    """
    for var, sub in _CACHE_VARS.items():
        if var not in os.environ:
            path = CACHE_ROOT / sub
            path.mkdir(parents=True, exist_ok=True)
            os.environ[var] = str(path)
    backend = render_backend()
    if backend and "MUJOCO_GL" not in os.environ:
        os.environ["MUJOCO_GL"] = backend
    # Let PyTorch fall back to the CPU for the few operations Apple's MPS backend lacks.
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("WANDB_MODE", "offline")
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    os.environ.setdefault("MPLBACKEND", "Agg")
