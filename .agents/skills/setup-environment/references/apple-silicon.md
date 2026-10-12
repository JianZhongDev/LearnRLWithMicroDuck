# Apple Silicon (M-series Mac) setup

Status: written from the upstream projects' documentation and lock file; **not yet tested on a Mac by the course**. Work through it carefully with the learner, report what actually happens, and record the outcome in `LearningProgress/STATE.md`.

## What the Apple GPU can and cannot do here

Be straightforward with the learner about this:

| Part of the course | Runs on | Why |
|---|---|---|
| Robot simulation (mjlab on MuJoCo Warp) | **CPU** | The simulation library, NVIDIA Warp, supports Apple Silicon as CPU-only; GPU acceleration needs NVIDIA CUDA. mjlab accepts only `cuda` or `cpu` devices. |
| Neural-network-only code (toy policies, supervised fits; mostly Modules 05–07) | **Apple GPU** through PyTorch MPS | PyTorch supports Apple's Metal Performance Shaders backend. |
| Rendering robot GIFs | Apple GPU through macOS OpenGL | MuJoCo's `glfw` backend. |
| Plots and diagrams | CPU | matplotlib. |

So there is no way to put the physics simulation on the Apple GPU today. M-series CPUs are fast, and small labs (a few robot copies, a few seconds) run well. Training a walking policy (Modules 09–13, 17) needs thousands of parallel robots and is not practical on a Mac: teach those modules with short demonstration runs, pre-existing checkpoints where upstream provides them, or a remote NVIDIA machine if the learner has one.

## Before running setup

1. **Native arm64 shell.** `uname -m` must print `arm64`. If it prints `x86_64`, the terminal runs under Rosetta: open a native shell with `arch -arm64 /bin/zsh`, or untick "Open using Rosetta" in the terminal app's Get Info window. `setup.sh` refuses to continue under Rosetta.
2. **Command line tools** (for `git`): `xcode-select --install`, if `xcode-select -p` prints nothing.
3. **macOS 13 or newer** is recommended (PyTorch MPS and current wheels).
4. Homebrew is **not** required. Do not install a system Python; `uv` downloads a native arm64 Python 3.12 itself.

## Run setup

```
./setup.sh --yes            # add --sources <folder> if the learner chose one
```

Expected: `system: macos (Darwin arm64, macos)`, the two checkouts, then `uv sync --frozen`. The upstream lock file contains macOS arm64 builds of PyTorch, MuJoCo, Warp, ONNX Runtime and the other compiled packages. If a package is reported as unavailable, follow section 5 of the skill.

## What the doctor should report

```
[ OK ] Apple Silicon, native arm64 Python
[ OK ] Simulation device: CPU (Apple Silicon) ...
[ OK ] Apple GPU (PyTorch MPS): available for neural-network-only lessons
[ OK ] MuJoCo rendering: backend 'glfw' works
```

and `.course/env.json` should contain `"device": "cpu"`, `"torch_device": "mps"`, `"apple_silicon": true`, `"mujoco_gl": "glfw"`.

- **MPS WARN:** check macOS version and that Python is arm64 (`python -c "import platform; print(platform.machine())"` through `lab py`). Lessons still work on the CPU.
- **Rendering WARN:** the `glfw` backend needs a logged-in graphical session; it does not work over plain SSH. Run from the Mac's own terminal. Labs still work without GIFs.
- **First simulation run:** Warp compiles its kernels for the CPU (a few minutes, once).

## Teaching on Apple Silicon

- **Simulation labs:** default to 2–4 robot copies and a few simulated seconds. Never pass `mps` to `dk.make_env`; it uses `dk.default_device()`, which is `cpu` here.
- **Neural-network-only labs:** use `dk.torch_device()` (returns `mps`). Keep tensors that touch the simulator on `env.device`, and never mix the two devices in one computation; move data explicitly with `.to(...)` or `.cpu()` if a lab needs both.
- MPS lacks a few operations and `float64`. `duckkit` sets `PYTORCH_ENABLE_MPS_FALLBACK=1`; use `float32`. For tiny networks the CPU is often just as fast; if MPS causes trouble, set `COURSE_TORCH_DEVICE=cpu`.
- **Interactive MuJoCo viewer:** on macOS it must be started with `mjpython` instead of `python`. The course uses saved GIFs, so this is only needed if the learner asks for a live window.
- **Training lessons:** say at the module overview that this machine will run demonstration-size training only, and plan labs accordingly (for example 16 robots for 2 iterations to show the mechanics). Offer the learner the option of doing those labs on a machine with an NVIDIA GPU; do not start cloud or paid compute without their explicit request.
- **Module 15** (building the Rust runtime) has its own untested macOS caveats; treat it as a reading module unless the learner wants to try.

## Report back

After the first successful (or failed) setup on a Mac, add a dated note to `LearningProgress/STATE.md` with the macOS version, chip, what the doctor printed, and any fix that was needed. If the learner is willing, suggest they share it as an issue on the course repository so the guide can be marked tested.
