# Environment: setup, platforms and troubleshooting

For learners and for the teaching agent. Short version: run setup once, then `lab doctor` tells you what works. The agent's step-by-step procedure is the `setup-environment` skill.

`lab` means `./lab.sh` on Linux and macOS, and `.\lab` on Windows.

## What setup does

This repository contains no MicroDuck source code. `./setup.sh` (Windows: `.\setup`, which runs the same script inside WSL 2) prepares everything around it:

1. Checks the platform, `git` and `curl`.
2. Installs [`uv`](https://docs.astral.sh/uv/) into `~/.local/bin` if it is missing (asks first; `--yes` skips the question). Nothing else is installed system-wide.
3. Obtains the two MicroDuck repositories as separate checkouts **outside this repository**:
   - `microduck_rl`: training code and robot model (Python), from https://github.com/pollen-robotics/microduck_rl
   - `microduck`: the robot's runtime software (Rust; read for reference, built only in Module 15), from https://github.com/pollen-robotics/microduck

   By default they go next to this folder (`../microduck_rl`, `../microduck`). `--sources <folder>` chooses another place. Existing clones there are reused and never modified.
4. Creates a private Python 3.12 environment from `microduck_rl`'s lock file (`uv sync --frozen`). This is the large download: PyTorch, MuJoCo, Warp, mjlab.
5. Records the result in `.course/` and runs the doctor: package imports, compute devices, rendering, and a short simulation.

Options:

| Option | Effect |
|---|---|
| `--sources DIR` | Use or create the checkouts in `DIR/microduck_rl` and `DIR/microduck`. On Windows a path like `D:\Code` works. |
| `--checkout-pinned` | Switch an existing, clean checkout to the commit the course was tested with (`tools/pins.env`). Without it, an existing checkout at another commit is left alone with a warning. |
| `--latest` | Use the newest upstream code instead of the tested commits. Lesson details may differ. |
| `--cpu` | Ignore the NVIDIA GPU. |
| `--skip-selftest` | Skip the 2–4 minute simulation test. |
| `--yes` | Do not ask before installing `uv`. |
| `--check` | Only check (same as `lab doctor`). |

It is safe to run setup again; it only does what is missing and remembers the sources folder.

## What ends up where

| Path | Content | In this Git repository? |
|---|---|---|
| `<sources>/microduck_rl`, `<sources>/microduck` | the two MicroDuck checkouts, used read-only | no: outside the repository |
| `.venv/` | the Python environment (Linux, macOS) | ignored |
| `~/.local/share/learn-rl-with-microduck/venv-*` | the Python environment when the course folder is on a Windows drive (see below) | outside the repository |
| `.course/env.json`, `.course/env.sh` | what setup found: launcher, Python path, checkout paths, devices, renderer | ignored |
| `.course/cache/` | simulator and plotting caches; safe to delete | ignored |
| `LearningProgress/**/results/` | lab outputs | ignored |

To remove everything setup created: delete `.venv/`, `.course/`, the `venv-*` folder above if present, and the two checkouts if setup cloned them for you.

The Python environment installs `microduck_rl` in "editable" mode, which means it imports the code from the checkout. If you move or delete the checkout, run setup again with `--sources`.

## Platforms

| Platform | Status | Simulation runs on |
|---|---|---|
| Windows 10/11 + WSL 2 (Ubuntu) + NVIDIA GPU | **tested** | NVIDIA GPU |
| Linux (Ubuntu, Debian, Fedora, Arch, …) + NVIDIA GPU | expected to work; not yet tested on native Linux | NVIDIA GPU |
| Windows or Linux without an NVIDIA GPU | works for small labs (tested with the GPU hidden) | CPU |
| macOS on Apple Silicon (M-series) | setup path written, **not yet tested** | CPU; Apple GPU for neural-network-only lessons |
| macOS on Intel | not supported | — |
| Windows without WSL | not supported | — |

### Windows details

- Everything runs inside WSL 2. Install it with `wsl --install -d Ubuntu` (Administrator PowerShell), restart, and open Ubuntu once to create a user.
- GPU: install the normal Windows NVIDIA driver. WSL uses it directly; do **not** install a Linux NVIDIA driver inside WSL. Check with `wsl nvidia-smi`.
- The course folder can stay on a Windows drive (`C:\…`, `D:\…`), which is convenient for desktop agents and editors. In that case setup puts the Python environment on the Linux side (`~/.local/share/learn-rl-with-microduck/`), because Python environments on Windows drives are slow and fragile inside WSL.
- `.\setup` and `.\lab` use your default WSL distribution. To use another one: `set COURSE_WSL_DISTRO=Ubuntu-24.04` (cmd) or `$env:COURSE_WSL_DISTRO="Ubuntu-24.04"` (PowerShell) before running setup. Setup remembers it in `.course/wsl-distro.txt`.
- `lab py tools/where.py mjlab` prints the checkout and library folders, with Windows paths (`D:\…` or `\\wsl.localhost\…`) that Windows tools can open.

### Linux details

- Fedora/RHEL: `sudo dnf install -y git curl`. Ubuntu/Debian: `sudo apt install -y git curl ca-certificates`.
- Rendering without a display (servers, SSH): the doctor tries EGL first, which works with NVIDIA drivers. On Mesa you may need `libegl1` / `mesa-libEGL` or `libosmesa6` / `mesa-libOSMesa`.

### macOS on Apple Silicon

What to expect, plainly:

- **The robot simulation runs on the CPU.** The simulation library under mjlab (NVIDIA Warp) supports Apple Silicon as CPU-only; GPU acceleration needs NVIDIA CUDA, and there is no Metal backend. Small labs (a few robot copies, a few seconds) run well on M-series CPUs.
- **The Apple GPU is used where it can be:** neural-network-only lessons (mostly Modules 05–07) run on PyTorch's MPS backend, and robot GIFs are rendered through macOS OpenGL.
- **Training a walking policy** (Modules 09–13, 17) needs thousands of parallel robots. On a Mac those lessons use short demonstration runs; real training needs a machine with an NVIDIA GPU.

Steps:

1. Use a native arm64 terminal: `uname -m` must print `arm64`. Under Rosetta it prints `x86_64`; open a native shell with `arch -arm64 /bin/zsh`.
2. Install Apple's command line tools if needed: `xcode-select --install`.
3. Run `./setup.sh`. Homebrew and a system Python are not needed.
4. The doctor should report `Apple Silicon, native arm64 Python`, `Simulation device: CPU (Apple Silicon)`, `Apple GPU (PyTorch MPS): available`, and rendering backend `glfw`.

Notes: rendering needs a logged-in graphical session (it does not work over plain SSH). The agent's detailed guide is `.agents/skills/setup-environment/references/apple-silicon.md`. If you get it working, or it fails, please open an issue with the doctor's output so this section can be marked tested.

## Compute devices

The doctor records two devices in `.course/env.json`:

| Field | Used for | Values |
|---|---|---|
| `device` | the robot simulation | `cuda:0` (NVIDIA) or `cpu` |
| `torch_device` | neural-network-only code | `cuda:0`, `mps` (Apple GPU) or `cpu` |

Override per run with the environment variables `COURSE_DEVICE` and `COURSE_TORCH_DEVICE`.

Without an NVIDIA GPU:

- Use small settings: 2–4 robot copies and a few simulated seconds. Agents are told to choose such defaults.
- Modules 00–08 are comfortable. From Module 09 on, lessons that train a policy become short demonstrations. The upstream project can also run training on Hugging Face Jobs (paid; the agent must ask before using it).

## Rendering

Robot GIFs need an OpenGL backend for MuJoCo. The doctor tries `egl`, `glfw` and `osmesa` (order depends on the platform) and records the first that works as `mujoco_gl`. Override with the `MUJOCO_GL` environment variable; `MUJOCO_GL=none` turns rendering off.

If none works, `mujoco_gl` is `null`: labs still run, print results and save plots, and skip GIFs with a note.

- WSL: `glfw` works through WSLg (Windows 11, or Windows 10 with a current WSL). Run `wsl --update` if it does not.
- Headless Linux with NVIDIA: `egl`.
- Headless Linux without a GPU: install OSMesa, then run `lab doctor --write`.
- macOS: `glfw`, from a terminal in a graphical session.

## Checking and repairing

```
lab doctor            # quick check (about 30 s)
lab doctor --full     # also build, step and render the robot environment
lab doctor --write    # re-detect devices and renderer and store them
./setup.sh            # repair: redo anything missing
```

The doctor prints `OK`, `WARN` or `FAIL` per item. `WARN` (no NVIDIA GPU, no renderer, a checkout at another commit) still allows labs to run.

## Troubleshooting

| Symptom | What to do |
|---|---|
| `uv sync` fails downloading | Check the network and re-run setup; downloads resume. Behind a proxy, set `HTTPS_PROXY`. |
| `uv sync` fails with "no matching distribution" / "not available for your platform" | The upstream lock file has no build of some package for your system. See the `setup-environment` skill, section 5 (installing without the lock), and please open an issue with the message. |
| `FAIL microduck_rl checkout` | The checkout was moved or deleted. Run setup again, with `--sources` if it lives elsewhere. |
| `WARN microduck_rl checkout … (course tested with …)` | Your checkout is at another commit. Labs usually still work; quoted line numbers may be off. `./setup.sh --checkout-pinned` switches it if it has no local changes. |
| `FAIL import torch` or `import warp` | The environment is incomplete: re-run setup. Delete the environment folder first if it keeps failing. |
| `WARN Simulation device` on a machine with an NVIDIA card | `nvidia-smi` must work in the same shell (inside WSL on Windows). Update the NVIDIA driver; on Windows run `wsl --update`. |
| "CUDA out of memory" | Close other GPU programs; use fewer robot copies (`num_envs=…`). |
| No GIFs / `WARN MuJoCo rendering` | See Rendering above. Plots are unaffected. |
| First lab run seems stuck | Simulation code is compiling (2–4 minutes the first time, per device). Later runs start in seconds. |
| `lab: The course environment is not set up yet` | Run setup. |
| `bash\r: No such file` or `$'\r': command not found` | A shell script has Windows line endings. `git config core.autocrlf input`, then `git checkout -- .`, or re-clone. The repository's `.gitattributes` normally prevents this. |
| A MicroDuck checkout shows changes in Git | Lessons must never edit the checkouts. `git -C <checkout> status` shows what changed; restore it yourself if the changes are not yours. |
| The agent says it cannot read the MicroDuck source | The checkouts are outside the course folder. Give the agent read access to those two folders (for example `/add-dir` in Claude Code), or let it read them through terminal commands. |
| Everything is slow on Windows | Normal for file access across the Windows/WSL boundary. For more speed, clone the course inside WSL (`~/LearnRLWithMicroDuck`) and open that folder from your agent. |

## Offline use and privacy

After setup, labs need no network. Experiment tracking (Weights & Biases) is forced offline by `duckkit`. Nothing is uploaded unless you explicitly run an upstream publishing command, which the course never does without asking.

## Module 15: building the robot runtime (optional, later)

Module 15 runs MicroDuck's real control software (Rust) against a simulated body. The course setup does not install this toolchain. When you reach that module, the agent walks you through it and asks before installing anything:

- Rust toolchain (the version in the `microduck` checkout's `CONTRIBUTING.md`), installed with `rustup` into your home folder.
- System libraries listed there (for example `libudev` and GStreamer development packages on Linux). These need `sudo` and change your system, so decide deliberately; a container is an alternative.
- Then the documented simulator scripts in that checkout. Build output must go to a separate target folder, not into the checkout.

This path has not been tested yet. Until it works on your machine, treat Module 15 as a reading and tracing module.
