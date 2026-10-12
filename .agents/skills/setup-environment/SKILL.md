---
name: setup-environment
description: Set up or repair the Learn RL with MicroDuck course environment with the learner - obtain the two MicroDuck repositories outside this repository, create the Python environment, and verify compute and rendering on Windows (WSL), Linux or macOS including Apple Silicon. Use when .course/env.json is missing, when lab doctor reports FAIL, or when the learner asks to set up, move or repair the environment.
---

# Set up the course environment

This repository contains **no MicroDuck source code**. The course needs two upstream repositories on the learner's machine, outside this folder, used read-only:

- `microduck_rl`: training code and the robot model: https://github.com/pollen-robotics/microduck_rl
- `microduck`: the robot's runtime software (read for reference; built only in Module 15): https://github.com/pollen-robotics/microduck

`setup.sh` (Windows: `setup.cmd`, which runs it inside WSL 2) obtains them, builds a private Python environment from `microduck_rl`'s lock file, and records everything in `.course/env.json`. Your job is to run it with the learner's agreement and get to `READY`.

## 1. Agree on the plan (one short message, then wait for a yes)

Tell the learner, in their language:

- what will happen: two Git clones, several GB of Python packages, 10–30 minutes; nothing system-wide except the `uv` tool in `~/.local/bin` if missing;
- **where the MicroDuck checkouts go.** Default: next to this folder (`../microduck_rl`, `../microduck`). Ask whether they already have clones or prefer another folder; then use `--sources <folder>`. Never choose a location inside this repository;
- their platform's note from section 3.

Do not run anything that needs `sudo`. If a system package is missing, show the command and let the learner run it.

## 2. Run setup

| System | Command (from the course folder) |
|---|---|
| Windows | `.\setup --yes` in PowerShell or cmd (add `--sources D:\some\folder` if chosen) |
| Linux, macOS | `./setup.sh --yes` (add `--sources /some/folder` if chosen) |

- Run it yourself if the learner agreed and your tools can run long commands; otherwise give them the command and wait. It prints clear `==>` stages.
- Existing checkouts are reused and never modified. If one is at a different commit than the course was tested with (`tools/pins.env`), setup warns and leaves it alone. Ask the learner before re-running with `--checkout-pinned`; that switches their checkout to the tested commit.
- `--latest` uses the newest upstream code. Use it only if the learner wants it; lesson details may then differ.
- Setup ends with the doctor's report and `READY`, or with `FAIL` lines.

## 3. Platform notes

- **Windows:** needs WSL 2 with a Linux distribution (`wsl --install -d Ubuntu`, restart, open Ubuntu once). The NVIDIA driver is the normal Windows one. Details: `docs/ENVIRONMENT.md`.
- **Linux:** needs `git` and `curl`. With an NVIDIA GPU, `nvidia-smi` must work.
- **macOS:** Apple Silicon only. Read [references/apple-silicon.md](references/apple-silicon.md) before running setup and follow it.
- **No NVIDIA GPU (any system):** everything still works on the CPU with small labs. Say so once, plainly.

## 4. Verify and give yourself access

1. `lab doctor` must end with `READY`. For each `FAIL`, use `docs/ENVIRONMENT.md` (Troubleshooting) and re-run. Explain `WARN` lines to the learner in one sentence each.
2. Read `.course/env.json`. Note `launcher`, `device`, `torch_device`, `mujoco_gl`, `rl_repo`, `runtime_repo`.
3. Make sure **you** can read the two checkouts, because lessons cite their source. They are outside your workspace:
   - try reading `<rl_repo>/README.md` with your file tool;
   - if that is blocked, ask the learner to grant read access to both folders (for example `/add-dir <path>` in Claude Code, or adding the folders to the workspace in an IDE), or read through the terminal instead (`lab py tools/where.py` prints the paths; `cat`, `grep`, `rg` with the path);
   - never ask for or use write access there.
4. Record a short environment summary in `LearningProgress/LEARNER.md` (Machine section) and, if this was a repair, in `STATE.md`.

## 5. If package installation fails for this platform

`uv sync --frozen` installs exactly what upstream locked. If it reports that a package has no build for this machine:

1. Copy the exact error for the learner. Do not edit anything in the `microduck_rl` checkout, including `uv.lock`.
2. Check `docs/ENVIRONMENT.md` for a known note on this platform.
3. Offer the fallback, and only with the learner's agreement: install from an exported copy of the lock, so every other package keeps its tested version. Use the venv path that setup printed (`.venv` in the course folder unless it said otherwise). The requirements file is written into `.course/`, not into the checkout:
   ```
   cd <rl_repo> && uv export --frozen --no-hashes --no-emit-project -o <course>/.course/requirements.txt
   uv venv --python 3.12 <venv>
   uv pip install --python <venv>/bin/python -r <course>/.course/requirements.txt
   cd <rl_repo> && uv pip install --python <venv>/bin/python --no-deps -e .
   ```
   If one package has no build for this machine, change only that line in `.course/requirements.txt` to the nearest version that has one, and repeat the install. Do **not** fall back to a plain `uv pip install -e .`: without the lock, the actuator-model dependency resolves to a newer, incompatible version and the MicroDuck tasks fail to load (verified).

   Then write `.course/env.sh` and `.course/env.json` (see `tools/write_env.py` for the fields; `setup.sh` section 5 shows the three `export` lines) and run `lab doctor --write --full`. Record in `STATE.md` which versions differ from the tested ones. This procedure was verified on Linux; on other platforms report what happens.
4. If it still fails, stop and say so honestly. Suggest a Linux or Windows machine with an NVIDIA GPU, and offer to continue with the modules that need no simulator (reading, diagrams, math) meanwhile.

## 6. Hand back

End with `READY` status in one line, where the checkouts are, and:
`▶ Next: reply "start" to begin, or type start-course in a new session.`
