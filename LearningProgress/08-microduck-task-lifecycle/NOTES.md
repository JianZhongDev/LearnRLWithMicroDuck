# Module 08 notes — how a simulator becomes an RL environment

Dated history: append entries, never rewrite. Format in the session-handoff skill.

## Pre-built material (shipped with the course)

- `MAP.md`, the concept figures in `figures/`, and five lesson pages with labs in `lessons/` come with the repository. They were written and tested on Windows 11 + WSL 2 (Ubuntu) with a 16 GB NVIDIA GPU, against the MicroDuck commits in `tools/pins.env`.
- Before teaching a lesson here, run its lab on this learner's machine and check the page's numbers against the output. Timings, fall times and episode counts can differ between machines and with `--latest` upstream code. Fix the page if they do, and note it below.
- On a machine without a GPU, pass smaller settings (for example `num_envs=2`); L05 runs real training iterations and is slow on a CPU.
- Learner did: nothing yet in this module.
