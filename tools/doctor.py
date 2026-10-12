"""Check the course environment, and record what works on this machine.

    lab doctor            quick check (about 30 s)
    lab doctor --full     also build, step and render the MicroDuck environment (2-4 min first time)
    lab doctor --write    store the detected devices and renderer in .course/env.json (setup does this)

Exit code 0 means labs can run. Warnings (no NVIDIA GPU, no renderer) do not fail the check:
labs then simulate on the CPU and skip GIFs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Load duckkit/setup.py by path: it only needs the standard library, so the doctor can
# still report clearly when third-party packages are missing.
_spec = importlib.util.spec_from_file_location(
    "course_setup", ROOT / "LearningProgress" / "_shared" / "duckkit" / "setup.py")
cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfg)

RENDER_PROBE = r"""
import os, sys
os.environ["MUJOCO_GL"] = sys.argv[1]
import mujoco
m = mujoco.MjModel.from_xml_string('<mujoco><worldbody><light pos="0 0 3"/><geom size="0.2"/></worldbody></mujoco>')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
with mujoco.Renderer(m, 64, 64) as r:
    r.update_scene(d)
    img = r.render()
assert img.shape == (64, 64, 3) and img.max() > 0
print("ok")
"""

MPS_PROBE = r"""
import torch
x = torch.ones(64, 64, device="mps")
assert float((x @ x).sum().cpu()) == 64.0 ** 3
print("ok")
"""

results: list[tuple[str, str, str]] = []  # (status, name, detail)


def record(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))
    print(f"  [{status:^4}] {name}" + (f": {detail}" if detail else ""), flush=True)


def git_commit(path: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(path), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or None
    except Exception:
        return None


def pinned(name: str) -> str | None:
    try:
        for line in (ROOT / "tools" / "pins.env").read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return None


def run_probe(code: str, *args: str) -> bool:
    try:
        out = subprocess.run([sys.executable, "-c", code, *args], capture_output=True, text=True, timeout=120)
        return out.returncode == 0 and "ok" in out.stdout
    except Exception:
        return False


def probe_renderers() -> str | None:
    if sys.platform == "darwin":
        order = ["glfw"]
    elif cfg.is_wsl():
        order = ["glfw", "egl", "osmesa"]
    else:
        order = ["egl", "glfw", "osmesa"]
    forced = os.environ.get("MUJOCO_GL")
    if forced:
        order = [forced] + [b for b in order if b != forced]
    for backend in order:
        if run_probe(RENDER_PROBE, backend):
            return backend
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="store detected devices/renderer in .course/env.json")
    parser.add_argument("--full", action="store_true", help="also run the simulation self-test")
    parser.add_argument("--cpu", action="store_true", help="record the CPU as the device even if a GPU exists")
    args = parser.parse_args()

    print(f"Course root: {ROOT}")
    print(f"Platform:    {platform.platform()}" + ("  (WSL)" if cfg.is_wsl() else ""))
    print(f"Python:      {sys.version.split()[0]}  ({sys.executable})\n")
    failed = False

    if sys.version_info[:2] == (3, 12):
        record("OK", "Python 3.12")
    else:
        record("FAIL", "Python version", f"{sys.version.split()[0]} found; microduck_rl requires 3.12. Re-run setup.")
        failed = True
    if sys.platform == "darwin":
        if platform.machine() == "arm64":
            record("OK", "Apple Silicon, native arm64 Python")
        else:
            record("FAIL", "Mac architecture", f"Python runs as {platform.machine()} (Intel or Rosetta). "
                                               "Use a native arm64 shell: arch -arm64 /bin/zsh, then re-run setup.")
            failed = True

    rl_commit = git_commit(cfg.RL_REPO) if (cfg.RL_REPO / "pyproject.toml").exists() else None
    if rl_commit:
        want = pinned("MICRODUCK_RL_COMMIT")
        note = "" if not want or want == rl_commit else f"  (course tested with {want[:10]})"
        record("OK" if not note else "WARN", "microduck_rl checkout", f"{cfg.RL_REPO} @ {rl_commit[:10]}{note}")
    else:
        record("FAIL", "microduck_rl checkout", f"not found at {cfg.RL_REPO}. Run setup (see the setup-environment skill).")
        failed = True
    try:
        cfg.RL_REPO.resolve().relative_to(ROOT)
        record("WARN", "checkout location", "microduck_rl is inside this repository; it should live outside it")
    except ValueError:
        pass
    if (cfg.RUNTIME_REPO / "Cargo.toml").exists():
        record("OK", "microduck (runtime) checkout",
               f"{cfg.RUNTIME_REPO} @ {(git_commit(cfg.RUNTIME_REPO) or '?')[:10]}")
    else:
        record("WARN", "microduck (runtime) checkout", f"not found at {cfg.RUNTIME_REPO} (needed from Module 14 on)")

    device, torch_device = "cpu", "cpu"
    for module in ("numpy", "matplotlib", "PIL", "mujoco", "torch", "warp", "mjlab"):
        try:
            mod = __import__(module)
            record("OK", f"import {module}", getattr(mod, "__version__", ""))
        except Exception as exc:  # noqa: BLE001
            record("FAIL", f"import {module}", f"{type(exc).__name__}: {exc}")
            failed = True
    if not failed:
        try:
            import mjlab.tasks  # noqa: F401
            from mjlab.tasks.registry import list_tasks

            tasks = [t for t in list_tasks() if "MicroDuck" in t]
            if tasks:
                record("OK", "MicroDuck tasks registered", f"{len(tasks)} tasks, e.g. {tasks[0]}")
            else:
                record("FAIL", "MicroDuck tasks registered", "none found; is mjlab-microduck installed in this venv?")
                failed = True
        except Exception as exc:  # noqa: BLE001
            record("FAIL", "MicroDuck tasks registered", f"{type(exc).__name__}: {exc}")
            failed = True
        try:
            import torch

            if torch.cuda.is_available() and not args.cpu:
                device = torch_device = "cuda:0"
                mem = torch.cuda.get_device_properties(0).total_memory / 2**30
                record("OK", "Simulation device", f"NVIDIA GPU: {torch.cuda.get_device_name(0)}, {mem:.0f} GiB")
            elif cfg.is_apple_silicon():
                record("OK", "Simulation device", "CPU (Apple Silicon). The simulator has no Apple-GPU backend; "
                                                  "small labs are fine, training lessons are short demonstrations")
                mps = getattr(torch.backends, "mps", None)
                if not args.cpu and mps is not None and mps.is_available() and run_probe(MPS_PROBE):
                    torch_device = "mps"
                    record("OK", "Apple GPU (PyTorch MPS)", "available for neural-network-only lessons")
                else:
                    record("WARN", "Apple GPU (PyTorch MPS)", "not available; neural-network lessons use the CPU")
            else:
                record("WARN", "Simulation device", "no usable NVIDIA GPU: labs run on the CPU (fine for small labs; "
                                                    "training labs will be slow)")
        except Exception as exc:  # noqa: BLE001
            record("WARN", "Simulation device", f"{type(exc).__name__}: {exc}")

    backend = probe_renderers() if not failed else None
    if backend:
        record("OK", "MuJoCo rendering", f"backend '{backend}' works: labs can make robot GIFs")
    elif not failed:
        record("WARN", "MuJoCo rendering", "no backend worked: labs skip GIFs, plots still work. "
                                           "See docs/ENVIRONMENT.md, section Rendering.")

    if args.write and not failed:
        env = cfg.load_env()
        env.update({"device": device, "torch_device": torch_device, "mujoco_gl": backend,
                    "apple_silicon": cfg.is_apple_silicon(), "rl_commit": rl_commit,
                    "checked": dt.datetime.now().isoformat(timespec="seconds")})
        cfg.COURSE_DIR.mkdir(exist_ok=True)
        cfg.ENV_FILE.write_text(json.dumps(env, indent=2), encoding="utf-8")
        print(f"\nRecorded device={device}, torch_device={torch_device}, mujoco_gl={backend} in {cfg.ENV_FILE}")

    if args.full and not failed:
        print("\nRunning the simulation self-test (first run compiles simulation code, 2-4 minutes)...", flush=True)
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "LearningProgress" / "_shared") + os.pathsep + env.get("PYTHONPATH", "")
        code = subprocess.run([sys.executable, "-B", str(ROOT / "LearningProgress" / "_shared" / "selftest.py")],
                              env=env).returncode
        record("OK" if code == 0 else "FAIL", "simulation self-test", "" if code == 0 else f"exit code {code}")
        failed = failed or code != 0

    warnings = sum(1 for s, _, _ in results if s == "WARN")
    print("\n" + ("FAILED: fix the items marked FAIL, then run the doctor again." if failed
                  else f"READY: labs can run ({warnings} warning(s))."))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
